# 트러블슈팅 가이드 (Troubleshooting)

## 목차
| # | 문제 | 핵심 원인 |
|---|------|-----------|
| 1 | [YDLIDAR 배열 크기 오류](#1-ydlidar-배열-크기-연산-오류-243개-오류) | 소수점 버림으로 243개 |
| 2 | [map_server & amcl 멈춤](#2-map_server--amcl-lifecycle-멈춤-unconfigured) | 지도 파일 누락 |
| 3 | [maps 폴더 오염](#3-maps-폴더-오염-및-심볼릭-링크-깨짐) | maps/ 안에서 빌드 |
| 4 | [global_costmap TF 타임아웃](#4-global_costmap-tf-대기-타임아웃) | 초기 위치 미주입 |
| 5 | [RViz2 그래픽 깨짐](#5-rviz2-그래픽-깨짐-glsl-셰이더-에러) | GLSL 셰이더 |
| 6 | [explore_lite 중단](#6-explore_lite-탐색-중단-no-frontiers-found) | 타임아웃/코스트맵 마진 |
| 7 | [전압 강하](#7-전압-강하voltage-sag-및-센서-연결-끊김--19-에러) | 배터리 부족 |

---

## 1. YDLIDAR 배열 크기 연산 오류 (243개 오류)
- **증상:** `LaserRangeScan contains 243 range readings, expected 244` 에러 발생 및 빈 지도 생성
- **원인:** OpenKarto는 244개를 기대하지만, `ydlidar_ros2_driver_node.cpp`의 배열 크기 계산 시 소수점이 버려져 243개가 된다.
- **해결:** 배열 크기 계산식을 `std::round`로 수정한다.

```cpp
int size = std::round((scan.config.max_angle - scan.config.min_angle) / scan.config.angle_increment) + 1;
```

## 2. map_server & amcl Lifecycle 멈춤 (unconfigured)
- **증상:** `/map` 토픽이 전혀 발행되지 않고 RViz에 지도가 뜨지 않는다.
- **원인:** 온보드 PC에 `.pgm` 지도 파일이 없거나 빌드 문제로 누락되면 생명주기가 멈춘다.
- **해결:** `ros2 lifecycle set /map_server configure` 및 `activate` 명령어로 수동 기동하거나, 전체 활성화 서비스(`ros2 service call /lifecycle_manager_localization/...`)를 호출한다.

## 3. maps 폴더 오염 및 심볼릭 링크 깨짐
- **증상:** `install/.../maps/MC_3F_10_15.pgm`이 깨진 링크가 되어 지도 로드에 실패한다.
- **원인:** `maps/` 폴더 안에서 빌드를 실행해 `build`, `install`, `log` 폴더가 생성되었다.
- **해결:** 오염된 폴더를 삭제한 뒤, `setup.py`에서 파일(`os.path.isfile(f)`)만 복사하도록 수정하고 재빌드한다.

## 4. global_costmap TF 대기 타임아웃
- **증상:** `frame "map" does not exist` 에러가 무한 반복된다.
- **원인:** 초기 위치가 주입되지 않아 AMCL이 `map` TF를 발행하지 않는다.
- **해결:** RViz의 2D Pose Estimate 또는 CLI로 `/initialpose` 토픽을 1회 발행해 초기 위치를 주입한다.

## 5. RViz2 그래픽 깨짐 (GLSL 셰이더 에러)
- **증상:** NoMachine 환경 등에서 지도가 검게 보이거나 렌더링 에러가 발생한다.
- **해결:** 아래 중 하나를 적용한다.
  - 소프트웨어 렌더링 사용: `LIBGL_ALWAYS_SOFTWARE=1 rviz2`
  - Map Color Scheme을 `costmap`으로 변경

## 6. explore_lite 탐색 중단 (No frontiers found)
- **증상:** `No frontiers found, stopping` 로그 발생 후 탐색을 포기한다.
- **원인:**
  - 10초 타임아웃에 걸려 블랙리스트에 등록됨
  - 코스트맵 마진(반경 0.19m + 안전거리 0.30m) 때문에 통과 경로가 닫힘
- **해결:** 좁은 문이나 틈새 진입에 실패하면 포기 상태가 되므로, 즉시 지도를 수동 저장한다.

## 7. 전압 강하(Voltage Sag) 및 센서 연결 끊김 (-19 에러)
- **증상:** `USB disconnect, ttyUSB1: failed set request ... status: -19`
- **원인:** 배터리 2칸 이하에서 주행 모터의 돌입 전류로 전압이 강하되어 USB 허브 전원이 차단된다.
- **대책:** 로봇 구동 시 배터리를 상시 3칸 이상 유지한다.
