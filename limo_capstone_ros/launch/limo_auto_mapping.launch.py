"""
limo_auto_mapping.launch.py
---------------------------
'자율 탐색 + 실시간 지도 작성' 통합 런치 파일.
  SLAM Toolbox(지도 작성) + Nav2(주행) + explore_lite(프론티어 탐색)을 함께 실행하여
  로봇이 스스로 미지의 공간을 돌아다니며 지도를 만든다.

사전 조건: limo_light.launch.py(base, TF, lidar)가 먼저 실행 중이어야 한다.
지도 저장: ros2 run nav2_map_server map_saver_cli -f <이름>
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # 각 패키지의 share 디렉터리 경로
    pkg_limo_capstone = get_package_share_directory('limo_capstone')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')

    # 설정 파일 경로 선언
    slam_params_file = os.path.join(pkg_limo_capstone, 'config', 'slam_params.yaml')         # SLAM Toolbox 파라미터
    nav2_params_file = os.path.join(pkg_limo_capstone, 'config', 'nav2_explore_params.yaml') # Nav2 파라미터
    explore_params_file = os.path.join(pkg_limo_capstone, 'config', 'explore.yaml')          # explore_lite 파라미터

    # use_sim_time: 기본 false (실제 로봇). 'use_sim_time:=true'로 덮어쓰기 가능하나
    # 이 파일에는 DeclareLaunchArgument가 없어 기본값만 사용된다.
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # 1. SLAM Toolbox (온라인 비동기 매핑 모드 + 커스텀 파라미터 적용)
    #    online_async: 처리가 밀리면 스캔을 건너뛰어 실시간성을 우선하는 방식.
    #    map -> odom TF와 /map 토픽을 발행한다.
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_file,
        }.items()
    )

    # 2. Nav2 Navigation (AMCL/정적 지도 없이 컨트롤러/플래너 스택만 실행)
    #    bringup_launch.py가 아닌 navigation_launch.py를 사용 -> map_server/AMCL 제외.
    #    위치 추정(map->odom)은 SLAM Toolbox가 담당한다.
    nav2_navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file,
            'autostart': 'true'   # lifecycle 노드 자동 활성화
        }.items()
    )

    # 3. base_footprint 정적 TF 브로드캐스터
    #    Nav2 기본 설정이 base_footprint를 참조하는 경우를 대비해
    #    base_link -> base_footprint 를 (x y z yaw pitch roll = 0) 동일 위치로 연결한다.
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_pub',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint']
    )

    # 4. explore_lite 프론티어 탐색 노드
    #    프론티어(알려진 영역과 미지 영역의 경계)를 찾아 Nav2에 목표점을 자동 전송한다.
    #    ※ 현재는 아래 LaunchDescription에 포함되어 자동 실행된다.
    explore_node = Node(
        package='explore_lite',
        executable='explore',
        name='explore_node',   # explore.yaml 최상위 키(explore_node)와 반드시 일치해야 함
        parameters=[explore_params_file],
        output='screen'
    )

    # 실행할 구성요소 목록 (SLAM -> Nav2 -> TF -> 탐색 순)
    return LaunchDescription([
        slam_launch,
        nav2_navigation_launch,
        static_tf,
        explore_node
    ])
