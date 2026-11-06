# 초기 세팅 및 실행 가이드 (Setup Guide)

## 1. 런치 파일(Launch) 실행 순서
* `explore_node`보다 `static_tf`(`base_link` -> `base_footprint`)가 먼저 실행되도록 배치해야 탐색 노드의 TF 대기 경고를 방지할 수 있음[cite: 4].

## 2. RViz2 Map QoS 설정
* `map_server`는 지도를 `Transient Local`로 발행함[cite: 5].
* RViz2 Displays 패널의 Map -> Topic 아래 Durability Policy를 `Transient Local`로 맞추어야 지도가 정상 출력됨[cite: 5].

## 3. 비상 정지(Stop) 단축어 설정
* 터미널 환경에 아래 단축어를 등록하여 비상시 즉각 활용:
  `alias stop='ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"'`[cite: 4].

## 4. 지도 수동 저장 명령어
* 자율 탐색(explore_lite) 완료 또는 중단 시 즉각 맵 저장:
  `ros2 run nav2_map_server map_saver_cli -f ~/capstone_ws/src/limo_capstone/maps/MC3F_room_map`[cite: 5].