# Redis Storage

Read [00-storage-catalog.md](./00-storage-catalog.md) first and [../01-overview.md](../01-overview.md) for system context, then use this file as the Redis storage reference.

## 1. Overview

- Redis client setup: `app/core/redis_ext.py`
- Current storage usage: mainly `line_chart`
- `notification` SSE fanout is in-memory, not Redis
- Main files:
  - `app/module/line_chart/line_chart_redis_repository.py`
  - `app/module/line_chart/pickle_test/long_running_program_demo.py`

## 2. Stored Data

- Key pattern: `chart_history:<series>`
- Data type: sorted set
- Current series seen in the code: `cpu`, `network`, `memory`, `btc`, `abc`
- Example keys:
  - `chart_history:cpu`
  - `chart_history:network`
  - `chart_history:memory`
  - `chart_history:btc`
  - `chart_history:abc`
- Score: unix timestamp
- Member payload:

```json
{"timestamp":1710000000,"value":12.34}
```

## 3. Live Updates

- Channel: `line_chart:updates`
- Data type: Redis pub/sub
- Each message stores one series update for the same series set above
- Message payload:

```json
{"series":"cpu","timestamp":1710000000,"value":12.34}
```
- History reads use `ZRANGEBYSCORE` through a pipeline.
- Demo writers prune old history with `ZREMRANGEBYSCORE`.
- Pub/sub messages are transient; they are not persisted like sorted-set history.
