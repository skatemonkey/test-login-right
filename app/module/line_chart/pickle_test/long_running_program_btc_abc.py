from datetime import UTC, datetime
import json
import random
import time

import redis

REDIS_URL = (
    "redis://default:pD8Pvvvx3R2mzZUEzUrCqwtQxobrEpr8@"
    "redis-15870.c11.us-east-1-2.ec2.cloud.redislabs.com:15870"
)
HISTORY_KEY_PREFIX = "chart_history:"
LIVE_UPDATES_CHANNEL = "line_chart:updates"
SAMPLE_INTERVAL_SECONDS = 5
INITIAL_HISTORY_SECONDS = 5 * 60 * 60
RETENTION_SECONDS = 7 * 24 * 60 * 60
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
    return f"{HISTORY_KEY_PREFIX}{series_name}"


def serialize_history_point(timestamp, value):
    return json.dumps({"timestamp": timestamp, "value": value}, separators=(",", ":"))


def serialize_live_update(series_name, timestamp, value):
    return json.dumps(
        {"series": series_name, "timestamp": timestamp, "value": value},
        separators=(",", ":"),
    )


def save_sample(redis_client, sample):
    timestamp = sample["timestamp"]
    cutoff_timestamp = timestamp - RETENTION_SECONDS
    removed_count = 0

    for series_name in SERIES_NAMES:
        redis_client.zadd(
            history_key(series_name),
            {serialize_history_point(timestamp, sample[series_name]): timestamp},
        )
        redis_client.publish(
            LIVE_UPDATES_CHANNEL,
            serialize_live_update(series_name, timestamp, sample[series_name]),
        )
        removed_count += redis_client.zremrangebyscore(
            history_key(series_name),
            "-inf",
            cutoff_timestamp - 1,
        )

    return removed_count


def reset_and_seed_history(
    redis_client,
    now=None,
    history_seconds=INITIAL_HISTORY_SECONDS,
    interval_seconds=SAMPLE_INTERVAL_SECONDS,
):
    timestamp = int(time.time()) if now is None else now
    start_timestamp = timestamp - history_seconds

    members_by_series = {series_name: {} for series_name in SERIES_NAMES}
    seeded_count = 0
    for sample_timestamp in range(start_timestamp, timestamp + 1, interval_seconds):
        sample = create_sample(sample_timestamp)
        seeded_count += 1

        for series_name in SERIES_NAMES:
            members_by_series[series_name][
                serialize_history_point(sample_timestamp, sample[series_name])
            ] = sample_timestamp

    redis_client.delete(*(history_key(series_name) for series_name in SERIES_NAMES))
    for series_name, members in members_by_series.items():
        if members:
            redis_client.zadd(history_key(series_name), members)

    return seeded_count


def run_once(redis_client, now=None):
    timestamp = int(time.time()) if now is None else now
    sample = create_sample(timestamp)
    removed_count = save_sample(redis_client, sample)

    readable_time = datetime.fromtimestamp(timestamp, UTC).isoformat()
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
        run_once(redis_client, now=int(time_func()))
        sleep(interval_seconds)


def main():
    redis_client = get_redis_client()
    print(f"Writing samples to Redis sorted sets {HISTORY_KEY_PREFIX}*")
    seeded_count = reset_and_seed_history(redis_client)
    print(f"Seeded {seeded_count} samples covering the last 5 hours")
    run_forever(redis_client, sleep_first=True)


if __name__ == "__main__":
    main()
