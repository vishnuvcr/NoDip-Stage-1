# P9 Primary-Source Timestamp / ATM Alignment Audit

- Audit date: 2026-04-01
- Near expiry: 2026-04-07
- Far expiry: 2026-04-28

## Index timestamps
- Index rows: 405
- First index timestamp: 2026-04-01 09:15:00
- Last index timestamp: 2026-04-01 15:59:00
- First 10 timestamps: [Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:16:00'), Timestamp('2026-04-01 09:17:00'), Timestamp('2026-04-01 09:18:00'), Timestamp('2026-04-01 09:19:00'), Timestamp('2026-04-01 09:20:00'), Timestamp('2026-04-01 09:21:00'), Timestamp('2026-04-01 09:22:00'), Timestamp('2026-04-01 09:23:00'), Timestamp('2026-04-01 09:24:00')]
- First 10 closes: [22843.45, 22824.1, 22869.05, 22885.05, 22887.0, 22894.7, 22887.55, 22893.65, 22882.8, 22899.55]

## Reference daily spot open
entry_date  spot_open
2026-04-01    22899.0

## Option timestamps
- Near rows: 58868; first timestamp: 2026-04-01 09:15:00; last: 2026-04-01 15:30:00
- Far rows: 903; first timestamp: 2026-04-01 09:15:00; last: 2026-04-01 15:30:00
- Near timestamp sample: [Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00')]
- Far timestamp sample: [Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:15:00'), Timestamp('2026-04-01 09:16:00'), Timestamp('2026-04-01 09:16:00'), Timestamp('2026-04-01 09:17:00'), Timestamp('2026-04-01 09:17:00'), Timestamp('2026-04-01 09:17:00'), Timestamp('2026-04-01 09:18:00'), Timestamp('2026-04-01 09:18:00'), Timestamp('2026-04-01 09:18:00')]

## 09:15
- Near rows at exact timestamp: 170
- Far rows at exact timestamp: 2
No complete four-leg common-strike panel.

## 09:16
- Near rows at exact timestamp: 177
- Far rows at exact timestamp: 2
No complete four-leg common-strike panel.

## 09:22
- Near rows at exact timestamp: 178
- Far rows at exact timestamp: 3
 strike     spot  distance_points  distance_pct     cbr
20500.0 22893.65          2393.65     10.455519 0.08178

## 09:26
- Near rows at exact timestamp: 172
- Far rows at exact timestamp: 4
 strike     spot  distance_points  distance_pct      cbr
20500.0 22900.05          2400.05     10.480545 0.083238

