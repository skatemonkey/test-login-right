from datetime import UTC, datetime
import json
import random
import time

import redis
from redis.exceptions import ResponseError

REDIS_URL = (
    "redis://default:pD8Pvvvx3R2mzZUEzUrCqwtQxobrEpr8@"
    "redis-15870.c11.us-east-1-2.ec2.cloud.redislabs.com:15870"
)
TIME_SERIES_KEY_PREFIX = "ts:line_chart:"
LIVE_UPDATES_CHANNEL = "line_chart:updates"
SAMPLE_INTERVAL_SECONDS = 5
INITIAL_HISTORY_SECONDS = 5 * 60 * 60
RETENTION_SECONDS = 7 * 24 * 60 * 60
RETENTION_MILLISECONDS = RETENTION_SECONDS * 1000
SERIES_NAMES = ("btc", "abc")


def create_sample(timestamp):
    btc_price = round(random.uniform(30_000, 90_000), 2)
    abc_price = round(btc_price - random.uniform(100, 1_500), 2)

    return {
        "timestamp": timestamp,
        "btc": btc_price,
        "abc": abc_price,
    }


def get_redis_client():
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def history_key(series_name):
    return f"{TIME_SERIES_KEY_PREFIX}{series_name}"


def serialize_live_update(series_name, timestamp, value):
    return json.dumps(
        {"series": series_name, "timestamp": timestamp, "value": value},
        separators=(",", ":"),
    )


def ensure_timeseries(ts_client, key):
    try:
        ts_client.create(key, retention_msecs=RETENTION_MILLISECONDS)
    except ResponseError as exc:
        if "already exists" not in str(exc).lower():
            raise


def save_sample(redis_client, sample):
    timestamp = sample["timestamp"]
    ts_client = redis_client.ts()

    for series_name in SERIES_NAMES:
        key = history_key(series_name)
        ensure_timeseries(ts_client, key)
        ts_client.add(key, timestamp, sample[series_name], duplicate_policy="LAST")
        redis_client.publish(
            LIVE_UPDATES_CHANNEL,
            serialize_live_update(series_name, timestamp, sample[series_name]),
        )

    return 0


def reset_and_seed_history(
    redis_client,
    now=None,
    history_seconds=INITIAL_HISTORY_SECONDS,
    interval_seconds=SAMPLE_INTERVAL_SECONDS,
):
    timestamp = int(time.time() * 1000) if now is None else now
    start_timestamp = timestamp - (history_seconds * 1000)
    interval_milliseconds = interval_seconds * 1000
    ts_client = redis_client.ts()
    seeded_count = 0
    seed_rows = []

    keys = [history_key(series_name) for series_name in SERIES_NAMES]
    redis_client.delete(*keys)
    for key in keys:
        ensure_timeseries(ts_client, key)

    for sample_timestamp in range(start_timestamp, timestamp + 1, interval_milliseconds):
        sample = create_sample(sample_timestamp)
        seeded_count += 1

        for series_name in SERIES_NAMES:
            seed_rows.append(
                (history_key(series_name), sample_timestamp, sample[series_name])
            )

    if seed_rows:
        ts_client.madd(seed_rows)

    return seeded_count


def run_once(redis_client, now=None):
    timestamp = int(time.time() * 1000) if now is None else now
    sample = create_sample(timestamp)
    removed_count = save_sample(redis_client, sample)

    readable_time = datetime.fromtimestamp(timestamp / 1000, UTC).isoformat()
    print(
        f"[{readable_time}] saved "
        f"btc={sample['btc']} abc={sample['abc']} "
        f"pruned={removed_count}"
    )

    return sample, removed_count


def run_forever(
    redis_client,
    interval_seconds=SAMPLE_INTERVAL_SECONDS,
    sleep=time.sleep,
    time_func=time.time,
    sleep_first=False,
):
    while True:
        if sleep_first:
            sleep(interval_seconds)
            sleep_first = False
        run_once(redis_client, now=int(time_func() * 1000))
        sleep(interval_seconds)


def main():
    redis_client = get_redis_client()
    print(f"Writing samples to RedisTimeSeries {TIME_SERIES_KEY_PREFIX}*")
    seeded_count = reset_and_seed_history(redis_client)
    print(f"Seeded {seeded_count} samples covering the last 5 hours")
    run_forever(redis_client, sleep_first=True)


if __name__ == "__main__":
    main()
