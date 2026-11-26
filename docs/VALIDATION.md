# 검증 기록

| 대상 | 수준 | 근거와 확인 범위 |
|---|---|---|
| Nav2 설정 전달 | 정적 확인 | [런치](../limo_capstone_ros/launch/limo_nav2.launch.py)가 nav2_explore_params.yaml을 params_file로 전달한다. 런타임에서 노드가 읽은 값은 별도 확인이 필요하다. |
| YAML 주석 수정 | 과거 작업 기록 | [11월 6일 튜닝 이력](tuning_log.md)에 주석 전후 파싱 결과가 같았다고 기록되어 있다. |
| 워크스페이스 문법 검사·빌드 | 실행 절차 확인 | [CI](../.github/workflows/ci.yml)는 Python·XML·YAML 문법을 검사하고, `dev` 대상 PR과 `dev` 푸시에서 ROS 2 Humble `colcon build`를 실행한다. |

새 시험에는 커밋, 환경과 구동 조건(개발 PC 검사·LIMO 정지 점검·LIMO 주행), 런치 인자, 입력, 기대 동작, 관찰 결과, 판정과 로그 위치를 함께 기록한다. 실패와 생략도 기록한다.
