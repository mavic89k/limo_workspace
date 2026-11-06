"""
limo_light.launch.py
--------------------
LIMO 로봇의 '최소 하드웨어 구동' 런치 파일.
SLAM / Nav2 / 탐색을 올리기 전에 먼저 실행해야 하는 기반 노드들을 한 번에 띄운다.

  1) limo_base            : 모터 구동 + 오도메트리(/odom) 발행 (odom -> base_link TF 포함)
  2) limo_description     : URDF 로드 (base_link -> laser_link 등 정적 TF)
  3) ydlidar_ros2_driver  : YDLidar 구동 (/scan 토픽 발행)

실행 예: ros2 launch limo_capstone limo_light.launch.py
"""
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
# FindPackageShare: 패키지의 share 디렉터리 경로를 '실행 시점'에 찾아주는 substitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 1. Base (limo_base) with odom TF enabled
    #    pub_odom_tf=true -> limo_base가 odom -> base_link TF를 직접 브로드캐스트한다.
    #    (SLAM Toolbox / Nav2가 이 TF에 의존하므로 반드시 true여야 함)
    base_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('limo_base'), '/launch/limo_base.launch.py'
        ]),
        launch_arguments={'pub_odom_tf': 'true'}.items()
    )

    # 2. Robot TF Description (load_urdf -> base_link to laser_link)
    #    URDF를 읽어 robot_state_publisher로 로봇 각 링크 간 고정 TF를 발행한다.
    #    라이다 위치(laser_link)가 여기서 정의되어 스캔 데이터를 base_link 기준으로 변환 가능.
    urdf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('limo_description'), '/launch/load_urdf.launch.py'
        ])
    )

    # 3. YDLidar
    #    2D 라이다 드라이버. /scan (sensor_msgs/LaserScan)을 발행하며
    #    SLAM, costmap, AMCL 모두 이 토픽을 사용한다.
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('ydlidar_ros2_driver'), '/launch/ydlidar.launch.py'
        ])
    )

    # 위에서 정의한 3개의 include를 동시에 실행
    return LaunchDescription([
        base_launch,
        urdf_launch,
        lidar_launch
    ])
