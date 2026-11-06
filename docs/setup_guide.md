# 초기 세팅 및 실행 가이드 (Setup Guide)

## 목차
1. [런치 파일 실행 순서](#1-런치-파일launch-실행-순서)
2. [RViz2 Map QoS 설정](#2-rviz2-map-qos-설정)
3. [비상 정지(Stop) 단축어](#3-비상-정지stop-단축어-설정)
4. [지도 수동 저장](#4-지도-수동-저장-명령어)
5. [Nav2 정적 지도 주행](#5-nav2-정적-지도-주행-limo_nav2launchpy)

---

## 1. 런치 파일(Launch) 실행 순서
- `explore_node`보다 `static_tf`(`base_link` → `base_footprint`)가 먼저 실행되도록 배치한다.
- 이렇게 해야 탐색 노드의 TF 대기 경고를 방지할 수 있다.

## 2. RViz2 Map QoS 설정
- `map_server`는 지도를 `Transient Local`로 발행한다.
- RViz2 Displays 패널에서 **Map → Topic → Durability Policy**를 `Transient Local`로 맞춰야 지도가 정상 출력된다.

## 3. 비상 정지(Stop) 단축어 설정
터미널 환경(`~/.bashrc`)에 아래 단축어를 등록해 비상시 바로 사용한다.

```bash
alias stop='ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"'
```

## 4. 지도 수동 저장 명령어
자율 탐색(`explore_lite`)이 완료되거나 중단되면 즉시 지도를 저장한다.

```bash
ros2 run nav2_map_server map_saver_cli -f ~/capstone_ws/src/limo_capstone/maps/MC3F_room_map
```

## 5. Nav2 정적 지도 주행 (`limo_nav2.launch.py`)
- `config/nav2_explore_params.yaml`이 `params_file`로 자동 적용된다. (2026-11-06 변경, 상세는 [tuning_log.md](tuning_log.md) 참고)
- 설정 변경 후에는 `colcon build` 및 source를 다시 해야 install 경로의 yaml에 반영된다.
