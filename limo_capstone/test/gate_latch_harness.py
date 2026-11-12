#!/usr/bin/env python3
"""Fake-sensor test: a STALL latch must survive a sensor FAILSAFE and recovery.

Sequence checked (require_operator_unlatch=False, as in limo_integrated_auto_mapping_real.launch.py):
  stall -> STALL_LATCHED -> sensor loss -> FAILSAFE -> sensor back + cmd 0 -> STALL_LATCHED (not NORMAL)
  -> new motion command -> output stays 0 -> /stall_detector/reset_latch -> re-arm -> commands pass.
Control case: without a latch, the same dropout recovers to NORMAL (unchanged behaviour).

Run (after building and sourcing the workspace, isolated domain, motors not involved):
  ROS_LOCALHOST_ONLY=1 ROS_DOMAIN_ID=<unused id> python3 gate_latch_harness.py
"""
import json, os, subprocess, sys, time
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from std_srvs.srv import Trigger


class Fake(Node):
    def __init__(self):
        super().__init__('fake_sensors')
        self.on = dict(scan=True, lidar=True, wheel=True, est=True)
        self.cmd = Twist()
        self.wheel_vx = 0.0
        self.state = None
        self.out = []
        self.p_scan = self.create_publisher(LaserScan, '/scan', qos_profile_sensor_data)
        self.p_lidar = self.create_publisher(Odometry, '/odometry/lidar_odom', 20)
        self.p_odom = self.create_publisher(Odometry, '/odom', 20)
        self.p_est = self.create_publisher(Odometry, '/odom_nav2', 20)
        self.p_cmd = self.create_publisher(Twist, '/cmd_vel_raw', 10)
        self.create_subscription(String, '/stall_detector/status_json', self.cb_s, 50)
        self.create_subscription(Twist, '/cmd_vel', lambda m: self.out.append((m.linear.x, m.angular.z)), 100)
        self.cli = self.create_client(Trigger, '/stall_detector/reset_latch')
        self.create_timer(0.1, self.tick10)
        self.create_timer(0.05, self.tick20)

    def cb_s(self, m):
        self.state = json.loads(m.data)['state']

    def tick10(self):
        if self.on['scan']:
            s = LaserScan(); s.header.frame_id = 'laser'; s.range_min = 0.1; s.range_max = 10.0
            s.ranges = [2.0] * 10; self.p_scan.publish(s)
        if self.on['lidar']:
            o = Odometry(); o.pose.pose.position.x = 0.0; self.p_lidar.publish(o)  # lidar says: not moving

    def tick20(self):
        if self.on['wheel']:
            o = Odometry(); o.twist.twist.linear.x = self.wheel_vx; self.p_odom.publish(o)
        if self.on['est']:
            self.p_est.publish(Odometry())
        if self.cmd.linear.x or self.cmd.angular.z:
            self.p_cmd.publish(self.cmd)


def spin(n, sec):
    t0 = time.monotonic()
    while time.monotonic() - t0 < sec:
        rclpy.spin_once(n, timeout_sec=0.01)


def reset(n):
    n.cli.wait_for_service(timeout_sec=3.0)
    f = n.cli.call_async(Trigger.Request())
    t0 = time.monotonic()
    while not f.done() and time.monotonic() - t0 < 3:
        rclpy.spin_once(n, timeout_sec=0.01)
    return f.result()


def nonzero(out):
    return sum(1 for vx, wz in out if abs(vx) > 1e-6 or abs(wz) > 1e-6)


RESULTS = []


def check(name, cond, detail=''):
    RESULTS.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}", flush=True)


def run(title, body):
    print(f'== {title}', flush=True)
    n = Fake()
    args = ['ros2', 'run', 'limo_capstone', 'stall_detector_node', '--ros-args',
            '-p', 'enabled:=true', '-p', 'require_operator_unlatch:=false',
            '-p', 'enable_auto_reverse:=false', '-p', 'enable_auto_rotate_recovery:=false',
            '-p', 'require_lidar_odom:=true', '-p', 'depth_mode:=disabled',
            '-p', 'estimator_odom_topic:=/odom_nav2', '-p', 'startup_timeout_sec:=5.0']
    g = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        body(n)
    finally:
        os.killpg(g.pid, 9); g.wait()
        n.destroy_node()
        time.sleep(0.5)


def make_stall(n):
    spin(n, 1.8)
    check('armed', n.state == 'NORMAL', f'state={n.state}')
    n.cmd.linear.x = 0.2; n.wheel_vx = 0.2; spin(n, 2.5)   # wheels turn, lidar sees no motion
    check('stall -> STALL_LATCHED', n.state == 'STALL_LATCHED', f'state={n.state}')


def latched_then_dropout(sensor):
    def body(n):
        make_stall(n)
        n.on[sensor] = False; spin(n, 1.0)
        check(f'{sensor} lost -> FAILSAFE_SENSOR_TIMEOUT', n.state == 'FAILSAFE_SENSOR_TIMEOUT', f'state={n.state}')
        n.on[sensor] = True; n.cmd = Twist(); n.wheel_vx = 0.0; spin(n, 1.5)
        check(f'{sensor} back + cmd 0 -> back to STALL_LATCHED, not NORMAL', n.state == 'STALL_LATCHED', f'state={n.state}')
        n.out.clear(); n.cmd.linear.x = 0.1; spin(n, 1.5)
        check('new motion command -> output stays 0 while latched', nonzero(n.out) == 0 and n.state == 'STALL_LATCHED',
              f'nonzero={nonzero(n.out)}/{len(n.out)} state={n.state}')
        n.cmd = Twist(); spin(n, 0.5)
        r = reset(n)
        check('reset_latch accepted', r is not None and r.success, r.message if r else 'no resp')
        spin(n, 1.8)
        check('re-armed to NORMAL after reset_latch', n.state == 'NORMAL', f'state={n.state}')
        n.out.clear(); n.cmd.linear.x = 0.1; n.wheel_vx = 0.0; spin(n, 0.5)
        check('commands pass again after reset', nonzero(n.out) > 0, f'nonzero={nonzero(n.out)}')
    return body


def control_no_latch(n):
    spin(n, 1.8)
    check('armed', n.state == 'NORMAL', f'state={n.state}')
    n.on['scan'] = False; spin(n, 1.0)
    check('scan lost -> FAILSAFE_SENSOR_TIMEOUT', n.state == 'FAILSAFE_SENSOR_TIMEOUT', f'state={n.state}')
    n.on['scan'] = True; spin(n, 1.5)
    check('no latch before: recovers to NORMAL (unchanged)', n.state == 'NORMAL', f'state={n.state}')


def reverse_blocked_spin_passes(n):
    spin(n, 1.8)
    check('armed', n.state == 'NORMAL', f'state={n.state}')
    n.out.clear(); n.cmd.linear.x = -0.05; spin(n, 1.0)       # what Nav2 BackUp publishes
    check('reverse (BackUp-style) command -> output 0 in NORMAL', nonzero(n.out) == 0, f'nonzero={nonzero(n.out)}/{len(n.out)}')
    n.cmd = Twist(); n.cmd.angular.z = 0.5; n.out.clear(); spin(n, 1.0)   # what Nav2 Spin publishes
    check('in-place rotation (Spin-style) passes in NORMAL', nonzero(n.out) > 0 and n.state == 'NORMAL',
          f'nonzero={nonzero(n.out)} state={n.state}')


rclpy.init()
run('latch -> scan loss -> recovery', latched_then_dropout('scan'))
run('latch -> wheel odom loss -> recovery', latched_then_dropout('wheel'))
run('control: no latch, scan loss -> recovery', control_no_latch)
run('reverse blocked, in-place spin passes (BT recovery policy)', reverse_blocked_spin_passes)
print(f'\nTOTAL {sum(RESULTS)}/{len(RESULTS)} passed')
sys.exit(0 if all(RESULTS) else 1)
