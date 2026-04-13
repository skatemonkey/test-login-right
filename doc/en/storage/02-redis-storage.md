# Redis Storage

Read [00-storage-catalog.md](./00-storage-catalog.md) first and [../01-overview.md](../01-overview.md) for system context, then use this file as the Redis storage reference.

## 1. Overview

- Redis client setup: `app/core/redis_ext.py`
- Current storage usage: mainly `line_chart`
- `line_chart` history uses RedisTimeSeries; live updates use Redis pub/sub
- `notification` SSE fanout is in-memory, not Redis
- Main files:
  - `app/module/line_chart/line_chart_redis_repository.py`
  - `app/module/line_chart/pickle_test/long_running_program_demo.py`
  - `app/module/line_chart/pickle_test/long_running_program_btc_abc.py`

## 2. History Storage

- Key pattern: `ts:line_chart:<series>`
- Data type: RedisTimeSeries
- Current series seen in the code: `cpu`, `network`, `memory`, `btc`, `abc`
- Example keys:
  - `ts:line_chart:cpu`
  - `ts:line_chart:network`
  - `ts:line_chart:memory`
  - `ts:line_chart:btc`
  - `ts:line_chart:abc`
- Timestamp unit: milliseconds since Unix epoch
- Stored sample model: one numeric sample per timestamp in the time series
- Example returned row from `redis-py`:

```text
(1710000000000, 12.34)
```
- Write behavior:
  - Demo writers create series with `TS.CREATE` and 7-day retention (`retention_msecs=604800000`)
  - Point writes use `TS.ADD` with `duplicate_policy="LAST"`
  - History seeding uses `TS.MADD`
- Query behavior:
  - History reads use `pipeline.ts().range(...)` / `TS.RANGE`
  - `POST /line-chart/history` expects `start` and `end` in milliseconds
  - History queries use the exact series names from the request; the history endpoint does not normalize case or aliases

## 3. Live Updates

- Channel: `line_chart:updates`
- Data type: Redis pub/sub
- Each message stores one series update for the same series set above
- Message payload:

```json
{"series":"cpu","timestamp":1710000000000,"value":12.34}
```
- `GET /line-chart/stream` consumes this channel and keeps the JSON payload shape above.
- Pub/sub messages are transient; they are not persisted like RedisTimeSeries history.
