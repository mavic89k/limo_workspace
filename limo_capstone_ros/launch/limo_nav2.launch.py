"""
limo_nav2.launch.py
-------------------
미리 만들어 둔 '정적 지도'를 이용한 Nav2 자율주행 런치 파일.
nav2_bringup의 bringup_launch.py를 포함하여 아래 구성요소를 모두 실행한다.
  - map_server        : 저장된 지도(yaml/pgm) 제공
  - AMCL              : 파티클 필터 기반 지도 상 위치 추정
  - planner / controller / bt_navigator / behavior 등 Nav2 스택

사전 조건: limo_light.launch.py(base, TF, lidar)가 먼저 실행 중이어야 한다.
실행 예: ros2 launch limo_capstone limo_nav2.launch.py map:=/path/to/map.yaml
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # 설치된(install/share) 패키지 경로 조회
    pkg_limo_capstone = get_package_share_directory('limo_capstone')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # 수정된 지도 경로 기본값 지정
    # <limo_capstone share>/maps/map_limo.yaml (setup.py의 data_files에 maps가 포함되어야 함)
    default_map_path = os.path.join(pkg_limo_capstone, 'maps', 'map_limo.yaml')

    # Nav2 파라미터 파일 경로 (LIMO 튜닝값)
    nav2_params_file = os.path.join(pkg_limo_capstone, 'config', 'nav2_explore_params.yaml')

    # [런치 인자] map: 사용할 지도 yaml 파일의 절대 경로
    #   명령행에서 map:=... 로 덮어쓸 수 있다.
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Full path to map yaml file to load'
    )

    # [런치 인자] use_sim_time: 시뮬레이션(Gazebo) 시계 사용 여부
    #   실제 로봇에서는 반드시 false (true면 /clock이 없어 TF 오류 발생)
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    # Nav2 표준 bringup 런치 포함 (AMCL, Costmap, Planner, Controller 등)
    # autostart=true -> lifecycle 노드들을 자동으로 configure/activate 한다.
    # params_file: LIMO에 맞게 튜닝한 config/nav2_explore_params.yaml 을 사용한다.
    #              (넘기지 않으면 nav2_bringup 기본 파라미터가 적용됨)
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': 'true',
            'params_file': nav2_params_file,
        }.items()
    )

    # 인자 선언 -> bringup 포함 순서로 등록해야 LaunchConfiguration이 올바르게 해석된다.
    return LaunchDescription([
        map_arg,
        use_sim_time_arg,
        nav2_bringup_launch
    ])
