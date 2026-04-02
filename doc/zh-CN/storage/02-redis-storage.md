# Redis 存储

先读 [00-storage-catalog.md](./00-storage-catalog.md) 和 [../01-overview.md](../01-overview.md) 获取系统背景，再使用本文件作为 Redis 存储参考。

## 1. 概览

- Redis 客户端初始化：`app/core/redis_ext.py`
- 当前使用 Redis 存储的模块：主要是 `line_chart`
- `notification` 的 SSE fanout 是进程内内存实现，不走 Redis
- 主要文件：
  - `app/module/line_chart/line_chart_redis_repository.py`
  - `app/module/line_chart/pickle_test/long_running_program_demo.py`

## 2. 存储数据

- Key 模式：`chart_history:<series>`
- 数据结构：sorted set
- 当前代码里出现的 series：`cpu`、`network`、`memory`、`btc`、`abc`
- Key 示例：
  - `chart_history:cpu`
  - `chart_history:network`
  - `chart_history:memory`
  - `chart_history:btc`
  - `chart_history:abc`
- score：unix timestamp
- member payload：

```json
{"timestamp":1710000000,"value":12.34}
```

## 3. 实时更新

- Channel：`line_chart:updates`
- 数据结构：Redis pub/sub
- 每条消息只保存一个 series 的实时更新，series 范围同上
- 消息 payload：

```json
{"series":"cpu","timestamp":1710000000,"value":12.34}
```
- 历史数据读取通过 pipeline 调用 `ZRANGEBYSCORE`。
- 示例写入程序通过 `ZREMRANGEBYSCORE` 清理旧历史数据。
- pub/sub 消息是瞬时的，不会像 sorted set 历史数据那样持久保存。
