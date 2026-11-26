# 결정 및 변경 근거

| 반영된 변경 | 이유와 근거 |
|---|---|
| 소스 폴더를 limo_capstone_ros로 변경하고 ROS 패키지명 limo_capstone 유지 | 커밋 `a94bcd8`의 디렉터리 변경. 기존 런치의 패키지 조회에는 [패키지 선언](../limo_capstone_ros/package.xml)의 이름을 사용한다. |
| 정적 지도 주행에서 프로젝트 Nav2 설정을 명시적으로 전달 | 기본 설정이 사용되어 LIMO 튜닝값이 누락되던 문제를 수정했다. [튜닝 기록](tuning_log.md) · [현재 구현](../limo_capstone_ros/launch/limo_nav2.launch.py) |

후속 설계는 채택된 시점에 변경 이유, 적용 범위, 근거 커밋 또는 팀 결정 기록을 추가한다.
