// Regression tests for the PR #8 review items (frontier first cell, partial map stride).
#include <gtest/gtest.h>

#include <map_msgs/msg/occupancy_grid_update.hpp>
#include <rclcpp/rclcpp.hpp>

#include "explore/costmap_client.h"
#include "explore/frontier_search.h"
#include "nav2_costmap_2d/cost_values.hpp"
#include "nav2_costmap_2d/costmap_2d.hpp"

namespace
{
const rclcpp::Logger kLogger = rclcpp::get_logger("test_review_fixes");
}

// A frontier made of one cell: middle/points/centroid must be that cell, not (0, 0).
TEST(Frontier, OneCellFrontierUsesItsOwnCell)
{
  // 5x5, resolution 1 m, origin (0, 0): everything free except cell (4, 2) unknown
  nav2_costmap_2d::Costmap2D costmap(5, 5, 1.0, 0.0, 0.0, nav2_costmap_2d::FREE_SPACE);
  costmap.setCost(4, 2, nav2_costmap_2d::NO_INFORMATION);

  frontier_exploration::FrontierSearch search(&costmap, 1.0, 1.0, 0.5, kLogger);
  geometry_msgs::msg::Point robot;
  robot.x = 0.5;
  robot.y = 2.5;
  auto frontiers = search.searchFrom(robot);

  ASSERT_EQ(frontiers.size(), 1u);
  const auto & f = frontiers[0];
  EXPECT_EQ(f.size, 1u);
  ASSERT_EQ(f.points.size(), 1u);
  EXPECT_DOUBLE_EQ(f.middle.x, 4.5);
  EXPECT_DOUBLE_EQ(f.middle.y, 2.5);
  EXPECT_DOUBLE_EQ(f.centroid.x, 4.5);
  EXPECT_DOUBLE_EQ(f.centroid.y, 2.5);
  EXPECT_DOUBLE_EQ(f.points[0].x, 4.5);
  EXPECT_DOUBLE_EQ(f.points[0].y, 2.5);
  EXPECT_NEAR(f.min_distance, 4.0, 1e-9);
}

// The first discovered cell is the one closest to the robot: it must define min_distance and middle,
// and points.size() must equal size.
TEST(Frontier, FirstCellCanBeTheClosest)
{
  // unknown column x = 4, y = 1..3; robot in cell (3, 1) so (4, 1) is found first
  nav2_costmap_2d::Costmap2D costmap(5, 5, 1.0, 0.0, 0.0, nav2_costmap_2d::FREE_SPACE);
  for (unsigned int y = 1; y <= 3; ++y) {
    costmap.setCost(4, y, nav2_costmap_2d::NO_INFORMATION);
  }

  frontier_exploration::FrontierSearch search(&costmap, 1.0, 1.0, 0.5, kLogger);
  geometry_msgs::msg::Point robot;
  robot.x = 3.5;
  robot.y = 1.5;
  auto frontiers = search.searchFrom(robot);

  ASSERT_EQ(frontiers.size(), 1u);
  const auto & f = frontiers[0];
  EXPECT_EQ(f.size, 3u);
  EXPECT_EQ(f.points.size(), 3u);
  EXPECT_NEAR(f.min_distance, 1.0, 1e-9);
  EXPECT_DOUBLE_EQ(f.middle.x, 4.5);
  EXPECT_DOUBLE_EQ(f.middle.y, 1.5);
  EXPECT_DOUBLE_EQ(f.centroid.x, 4.5);
  EXPECT_DOUBLE_EQ(f.centroid.y, 2.5);
}

// Update clipped on the right: row 2 must be read from data[width], not data[clipped_width].
TEST(PartialUpdate, ClippedRightKeepsRowStride)
{
  nav2_costmap_2d::Costmap2D costmap(6, 6, 1.0, 0.0, 0.0, 100);  // untouched cells keep their initial cost 100
  map_msgs::msg::OccupancyGridUpdate msg;
  msg.x = 4;
  msg.y = 0;
  msg.width = 3;   // columns 4, 5 fit; column 6 is clipped
  msg.height = 2;
  // occupancy: 0 -> free (0), 100 -> lethal (254), -1 -> unknown (255)
  msg.data = {0, 100, -1,
    100, -1, 0};

  EXPECT_TRUE(explore::Costmap2DClient::copyPartialUpdate(costmap, msg, kLogger));
  EXPECT_EQ(costmap.getCost(4, 0), 0);
  EXPECT_EQ(costmap.getCost(5, 0), 254);
  EXPECT_EQ(costmap.getCost(4, 1), 254);   // data[3]; the old code read data[2] = unknown
  EXPECT_EQ(costmap.getCost(5, 1), 255);   // data[4]
  EXPECT_EQ(costmap.getCost(3, 0), 100);   // untouched (initial cost value)
}

TEST(PartialUpdate, ShortDataIsRejectedWithoutWriting)
{
  nav2_costmap_2d::Costmap2D costmap(6, 6, 1.0, 0.0, 0.0, 100);
  map_msgs::msg::OccupancyGridUpdate msg;
  msg.x = 1;
  msg.y = 1;
  msg.width = 3;
  msg.height = 2;
  msg.data = {0, 0, 0, 0, 0};  // 5 cells for 3 x 2

  EXPECT_FALSE(explore::Costmap2DClient::copyPartialUpdate(costmap, msg, kLogger));
  for (unsigned int y = 0; y < 6; ++y) {
    for (unsigned int x = 0; x < 6; ++x) {
      EXPECT_EQ(costmap.getCost(x, y), 100) << "cell " << x << "," << y;
    }
  }
}

TEST(PartialUpdate, InteriorUpdateIsCopiedRowByRow)
{
  nav2_costmap_2d::Costmap2D costmap(6, 6, 1.0, 0.0, 0.0, 100);
  map_msgs::msg::OccupancyGridUpdate msg;
  msg.x = 1;
  msg.y = 2;
  msg.width = 3;
  msg.height = 2;
  msg.data = {0, 100, -1, -1, 100, 0};

  EXPECT_TRUE(explore::Costmap2DClient::copyPartialUpdate(costmap, msg, kLogger));
  EXPECT_EQ(costmap.getCost(1, 2), 0);
  EXPECT_EQ(costmap.getCost(2, 2), 254);
  EXPECT_EQ(costmap.getCost(3, 2), 255);
  EXPECT_EQ(costmap.getCost(1, 3), 255);
  EXPECT_EQ(costmap.getCost(2, 3), 254);
  EXPECT_EQ(costmap.getCost(3, 3), 0);
}

int main(int argc, char ** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
