# 실행 모드와 데이터 흐름

README의 분산 구성에서는 LIMO 본체가 LiDAR 스캔, 카메라 영상과 오도메트리를 제공하고 원격 PC가 DDS로 이를 수신한다. 노드 배치는 선택한 런치에 따라 달라진다.

| 실행 모드 | 데이터 흐름과 역할 |
|---|---|
| RGB-D와 LiDAR로 지도 작성 | 카메라 영상과 스캔을 RTAB-Map에 입력한다. 입력 토픽과 동기화 설정은 [RTAB-Map 런치](../limo_capstone_ros/launch/limo_rtabmap.launch.py)에서 확인한다. |
| 미지 환경 탐색 | SLAM Toolbox가 갱신하는 지도를 바탕으로 explore_lite가 탐색 목표를 정하고 Nav2가 주행을 담당한다. [자동 맵핑 런치](../limo_capstone_ros/launch/limo_auto_mapping.launch.py) |
| 저장 지도 주행 | map_server의 지도와 AMCL 위치 추정을 사용한다. [Nav2 런치](../limo_capstone_ros/launch/limo_nav2.launch.py)가 bringup에 지도와 파라미터를 전달한다. |
| 센서와 탐색 통합 | [실차용 통합 런치](../limo_capstone_ros/launch/limo_integrated_auto_mapping_real.launch.py)에서 깊이 장애물 필터, 오도메트리 처리, 탐색과 정체 감지의 실행 조건을 확인한다. |

위치 추정을 수정할 때는 선택한 런치 인자에서 활성화되는 EKF와 TF 발행자를 추적한다. 같은 프레임 변환을 두 노드가 동시에 발행하는지도 확인한다.
