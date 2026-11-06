# 파라미터 튜닝 일지 (Tuning Log)

## 목차
- [AMCL 파라미터 민감도 튜닝](#amcl-파라미터-민감도-튜닝-nav2_explore_paramsyaml)
- [2026-11-06 런치/설정 변경](#2026-11-06-런치설정-파일-주석-추가-및-nav2-파라미터-적용-수정)

---

## AMCL 파라미터 민감도 튜닝 (`nav2_explore_params.yaml`)

| 파라미터 | 변경 | 목적 |
|----------|------|------|
| `update_min_d` | 0.25 → 0.10 | 10cm 이동 시 파티클 위치 즉시 갱신 |
| `update_min_a` | 0.20 → 0.10 | 약 5.7도 회전 시 즉시 갱신 |
| `laser_min_range` | -1.0 → 0.05 | 차체 내부 반사로 인한 비정상 음수 노이즈 필터링 |
| `laser_max_range` | 100.0 → 10.0 | 실제 LIMO LiDAR 한계 스펙(8~10m)에 맞춰 노이즈 절삭 |
| `base_frame_id` | `base_footprint` → `base_link` | 정확한 차체 중심 기준으로 변경 |

---

## 2026-11-06 런치/설정 파일 주석 추가 및 Nav2 파라미터 적용 수정

### 1. 상세 주석 추가 (동작 변경 없음)
* 대상: `limo_capstone/launch/*.py` (`limo_light`, `limo_nav2`, `limo_rtabmap`, `limo_auto_mapping`), `limo_capstone/config/*.yaml` (`explore.yaml`, `nav2_explore_params.yaml`).
* `slam_params.yaml`은 이미 상세 주석이 있어 수정하지 않음.
* 런치 파일: 파일 상단에 용도/사전 조건, 각 노드·인자별 설명 추가.
* `nav2_explore_params.yaml`: 구역(AMCL, Controller, Costmap 등)별 헤더와 파라미터별 인라인 주석 추가. 기존 주석이 있던 줄은 뒤에 ` | 설명` 형태로 덧붙임.
* 주석 추가 전후 YAML 파싱 결과가 동일함을 확인함.

### 2. `limo_nav2.launch.py`: `params_file` 적용 (동작 변경)
* 문제: `params_file`을 넘기지 않아 `nav2_bringup` 기본 파라미터(`nav2_params.yaml`)가 사용되어, LIMO 튜닝값이 적용되지 않았음.
  * 미적용 값 예: 최대속도 0.26 m/s, `robot_radius` 0.19, `inflation_radius` 0.30, AMCL 라이다 범위/갱신 거리.
* 수정: `config/nav2_explore_params.yaml` 경로를 `nav2_params_file`로 선언하고 `bringup_launch.py`에 `'params_file': nav2_params_file`로 전달.
* `limo_auto_mapping.launch.py`는 기존부터 해당 파일을 사용 중이므로 변경 없음.

### 3. 참고 사항
* `nav2_explore_params.yaml`은 탐색용으로 튜닝했지만 정적 지도 주행에도 사용 가능함 (AMCL, map_server 섹션 포함).
* 탐색 전용 값: `planner_server.GridBased.allow_unknown: true`, `global_costmap.track_unknown_space: true`. 정적 지도 주행 시 지도 밖으로 경로가 생성되면 `allow_unknown`을 `false`로 변경할 것.
* 적용 방법: `colcon build` 후 workspace를 다시 source.
