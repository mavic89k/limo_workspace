# 트러블슈팅 가이드 (Troubleshooting)

## 1. YDLIDAR 배열 크기 연산 오류 (243개 오류)
* **증상:** `LaserRangeScan contains 243 range readings, expected 244` 에러 발생 및 빈 지도 생성[cite: 4].
* **원인:** OpenKarto는 244개를 기대하지만, `ydlidar_ros2_driver_node.cpp`의 배열 크기 계산 시 소수점이 버려져 243개가 됨[cite: 4].
* **해결:** 배열 크기 계산식을 `std::round`로 수정. `int size = std::round((scan.config.max_angle - scan.config.min_angle) / scan.config.angle_increment) + 1;`[cite: 4].

## 2. map_server & amcl Lifecycle 멈춤 (unconfigured)
* **증상:** `/map` 토픽이 전혀 발행되지 않고 RViz에 지도가 뜨지 않음[cite: 5].
* **원인:** 온보드 PC에 `.pgm` 지도 파일이 없거나 빌드 문제로 누락되었을 때 생명주기가 멈춤[cite: 5].
* **해결:** `ros2 lifecycle set /map_server configure` 및 `activate` 명령어로 수동 기동하거나 전체 활성화 서비스(`ros2 service call /lifecycle_manager_localization/...`) 호출[cite: 5].

## 3. maps 폴더 오염 및 심볼릭 링크 깨짐
* **증상:** `install/.../maps/MC_3F_10_15.pgm`이 깨진 링크가 되어 지도 로드 실패[cite: 5].
* **원인:** `maps/` 폴더 안에서 빌드를 실행해 `build`, `install`, `log` 폴더가 생성됨[cite: 5].
* **해결:** 오염된 폴더 삭제 후, `setup.py`에서 파일(`os.path.isfile(f)`)만 복사하도록 수정하고 재빌드 진행[cite: 5].

## 4. global_costmap TF 대기 타임아웃
* **증상:** `frame "map" does not exist` 에러 무한 반복[cite: 5].
* **원인:** 초기 위치가 주입되지 않아 AMCL이 `map` TF를 네트워크에 발행하지 않음[cite: 5].
* **해결:** RViz의 2D Pose Estimate 또는 CLI로 `/initialpose` 토픽을 1회 발행하여 초기 위치 주입[cite: 5].

## 5. RViz2 그래픽 깨짐 (GLSL 셰이더 에러)
* **증상:** NoMachine 환경 등에서 지도가 검게 보이거나 렌더링 에러 발생[cite: 5].
* **해결:** 터미널에서 `LIBGL_ALWAYS_SOFTWARE=1 rviz2` 명령어로 소프트웨어 렌더링을 켜거나, Map Color Scheme을 `costmap`으로 변경[cite: 5].

## 6. explore_lite 탐색 중단 (No frontiers found)
* **증상:** `No frontiers found, stopping` 로그 발생 후 탐색 포기[cite: 5].
* **원인:** 10초 타임아웃에 걸려 블랙리스트에 등록되거나, 코스트맵 마진(반경 0.19m + 안전거리 0.30m) 때문에 통과 경로가 아예 닫힘[cite: 5].
* **해결:** 좁은 문이나 틈새 진입 실패 시 포기 상태가 되므로 즉각 지도를 수동 저장[cite: 5].

## 7. 전압 강하(Voltage Sag) 및 센서 연결 끊김 (-19 에러)
* **증상:** `USB disconnect, ttyUSB1: failed set request ... status: -19`[cite: 5].
* **원인:** 배터리 2칸 이하 상태에서 주행 모터의 돌입 전류로 인해 전압이 강하되어 USB 허브 전원이 차단됨[cite: 5].
* **대책:** 로봇 구동 시 배터리 상태 상시 3칸 이상 유지[cite: 5].