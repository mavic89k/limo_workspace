# 코드 색인

경로는 저장소 루트 기준이다. 소스 폴더 이름은 `limo_capstone_ros`, ROS 패키지 이름은 [package.xml](../limo_capstone_ros/package.xml)의 `limo_capstone`이다.

| 찾을 대상 | 소스 진입점 |
|---|---|
| 센서 구동 | [limo_light.launch.py](../limo_capstone_ros/launch/limo_light.launch.py) |
| 주행 및 맵핑 모드별 런치 | [실행 모드 표](ARCHITECTURE.md) |
| 정적 지도 주행의 Nav2 파라미터 | [nav2_explore_params.yaml](../limo_capstone_ros/config/nav2_explore_params.yaml) |
| 통합 맵핑용 SLAM 설정 | [integrated_slam_params.yaml](../limo_capstone_ros/config/integrated_slam_params.yaml) |
| 자동 맵핑 액션 정의와 런치 | [AutoMapping.action](../limo_mapping_interfaces/action/AutoMapping.action) · [auto_mapping.launch.py](../limo_auto_mapping/launch/auto_mapping.launch.py) |
| 탐색 및 온보드 시험 진입점 | [explore.launch.py](../limo_mapping_explore/launch/explore.launch.py) · [탐색 시험](../limo_onboard_trials/launch/exploration_trial.launch.py) · [주행 시험](../limo_onboard_trials/launch/navigation_trial.launch.py) |
