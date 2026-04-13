# Redis 存储

先读 [00-storage-catalog.md](./00-storage-catalog.md) 和 [../01-overview.md](../01-overview.md) 获取系统背景，再使用本文件作为 Redis 存储参考。

## 1. 概览

- Redis 客户端初始化：`app/core/redis_ext.py`
- 当前使用 Redis 存储的模块：主要是 `line_chart`
- `line_chart` 的历史数据使用 RedisTimeSeries；实时更新使用 Redis pub/sub
- `notification` 的 SSE fanout 是进程内内存实现，不走 Redis
- 主要文件：
  - `app/module/line_chart/line_chart_redis_repository.py`
  - `app/module/line_chart/pickle_test/long_running_program_demo.py`
  - `app/module/line_chart/pickle_test/long_running_program_btc_abc.py`

## 2. 历史数据存储

- Key 模式：`ts:line_chart:<series>`
- 数据结构：RedisTimeSeries
- 当前代码里出现的 series：`cpu`、`network`、`memory`、`btc`、`abc`
- Key 示例：
  - `ts:line_chart:cpu`
  - `ts:line_chart:network`
  - `ts:line_chart:memory`
  - `ts:line_chart:btc`
  - `ts:line_chart:abc`
- 时间戳单位：Unix epoch 毫秒
- 存储模型：每个时间戳保存一个数值 sample
- `redis-py` 返回的单条样本示例：

```text
(1710000000000, 12.34)
```
- 写入行为：
  - 示例写入程序通过 `TS.CREATE` 创建 time series，并设置 7 天保留期（`retention_msecs=604800000`）
  - 单点写入使用 `TS.ADD`，并设置 `duplicate_policy="LAST"`
  - 历史数据初始化使用 `TS.MADD`
- 查询行为：
  - 历史数据读取通过 `pipeline.ts().range(...)` / `TS.RANGE`
  - `POST /line-chart/history` 的 `start` 和 `end` 需要使用毫秒
  - 历史查询按请求中的原始 series 名称查 key；history 接口不会自动做大小写或别名归一化

## 3. 实时更新

- Channel：`line_chart:updates`
- 数据结构：Redis pub/sub
- 每条消息只保存一个 series 的实时更新，series 范围同上
- 消息 payload：

```json
{"series":"cpu","timestamp":1710000000000,"value":12.34}
```
- `GET /line-chart/stream` 消费这个 channel，消息 JSON 结构保持如上。
- pub/sub 消息是瞬时的，不会像 RedisTimeSeries 历史数据那样持久保存。
