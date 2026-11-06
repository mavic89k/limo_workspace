"""
limo_rtabmap.launch.py
----------------------
RTAB-Map(RGB-D + 2D 라이다 융합 SLAM)을 LIMO에 맞는 인자로 실행하는 래퍼 런치 파일.
rtabmap_launch 패키지의 rtabmap.launch.py를 포함하고 아래 인자들을 전달한다.

사전 조건: limo_light.launch.py + 카메라 드라이버 + /odometry/filtered(EKF) 발행 중.
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg_rtabmap_launch = get_package_share_directory('rtabmap_launch')

    # RTAB-Map 래퍼 런치 구성
    # 값은 모두 문자열이어야 한다 (launch_arguments 규칙).
    rtabmap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rtabmap_launch, 'launch', 'rtabmap.launch.py')
        ),
        launch_arguments={
            # --- 기본 동작 ---
            'rtabmap_args': '--delete_db_on_start',  # 시작 시 기존 DB(~/.ros/rtabmap.db) 삭제 -> 항상 새 지도
            'use_sim_time': 'false',                 # 실제 로봇이므로 시스템 시계 사용

            # --- 오도메트리 ---
            'visual_odometry': 'false',              # 비주얼 오도메트리 끔 (바퀴/EKF 오도메트리 사용)
            'subscribe_odom_info': 'false',          # 비주얼 오도 정보 토픽 구독 안 함
            'frame_id': 'base_link',                 # 로봇 기준 프레임
            'odom_topic': '/odometry/filtered',      # EKF로 융합된 오도메트리 입력

            # --- 라이다 ---
            'subscribe_scan': 'true',                # 2D 라이다 스캔을 SLAM에 함께 사용
            'scan_topic': '/scan',                   # 라이다 토픽

            # --- RGB-D 카메라 ---
            'subscribe_depth': 'true',               # 깊이 영상 구독
            'rgb_topic': '/camera/color/image_raw',          # 컬러 영상
            'depth_topic': '/camera/depth/image_raw',        # 깊이 영상
            'camera_info_topic': '/camera/color/camera_info',# 카메라 내부 파라미터

            # --- QoS (1 = Best Effort: 센서 드라이버 기본값과 맞춤, 0 = Reliable) ---
            'qos_image': '1',
            'qos_camera_info': '1',
            'qos_scan': '1',
            'qos_odom': '1',

            # --- 동기화 ---
            'approx_sync': 'true',          # 센서 타임스탬프가 정확히 일치하지 않아도 근사 동기화
            'sync_queue_size': '50',        # 동기화용 큐 크기 (클수록 지연 허용, 메모리 증가)
            'topic_queue_size': '30',       # 각 토픽 구독 큐 크기
            'wait_for_transform': '0.5',    # TF 대기 최대 시간(초)

            # --- RTAB-Map 내부 파라미터 (Section/Name 형식) ---
            'Reg/Strategy': '1',                   # 정합 방식: 0=비주얼, 1=ICP(라이다), 2=비주얼+ICP
            'RGBD/NeighborLinkRefining': 'true',   # 인접 노드 링크를 라이다 ICP로 보정
            'Grid/FromDepth': 'false',             # 점유격자를 깊이 영상 대신 라이다 스캔으로 생성

            # --- 시각화 ---
            'rtabmap_viz': 'false',        # rtabmap_viz GUI 끔
            'rviz': 'true',                # RViz 실행
        }.items()
    )

    return LaunchDescription([
        rtabmap_launch
    ])
