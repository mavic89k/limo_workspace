# 파라미터 튜닝 일지 (Tuning Log)

## AMCL 파라미터 민감도 튜닝 (`nav2_explore_params.yaml`)
* `update_min_d`: 0.25 -> 0.10 (10cm 이동 시 파티클 위치 즉시 갱신)[cite: 5].
* `update_min_a`: 0.20 -> 0.10 (약 5.7도 회전 시 즉시 갱신)[cite: 5].
* `laser_min_range`: -1.0 -> 0.05 (차체 내부에서 반사되는 비정상 음수 노이즈 필터링)[cite: 5].
* `laser_max_range`: 100.0 -> 10.0 (실제 LIMO LiDAR 한계 스펙인 8~10m에 맞춰 노이즈 절삭)[cite: 5].
* `base_frame_id`: `base_footprint` -> `base_link` (정확한 차체 중심 기준으로 변경)[cite: 5].