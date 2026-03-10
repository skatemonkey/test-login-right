from datetime import UTC, datetime
import json
import random
import time

import redis

REDIS_URL = (
    "redis://default:pD8Pvvvx3R2mzZUEzUrCqwtQxobrEpr8@"
    "redis-15870.c11.us-east-1-2.ec2.cloud.redislabs.com:15870"
)
REDIS_KEY = "line_chart:points"
SAMPLE_INTERVAL_SECONDS = 5
INITIAL_HISTORY_SECONDS = 2 * 60 * 60
RETENTION_SECONDS = 7 * 24 * 60 * 60


def create_sample(timestamp):
    return {
        "timestamp": timestamp,
        "cpu": round(random.uniform(10, 90), 2),
        "network": round(random.uniform(100, 1000), 2),
        "memory": round(random.uniform(20, 95), 2),
    }


def get_redis_client():
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def serialize_sample(sample):
    return json.dumps(sample, separators=(",", ":"))


def save_sample(redis_client, sample):
    payload = serialize_sample(sample)
    redis_client.zadd(REDIS_KEY, {payload: sample["timestamp"]})

    cutoff_timestamp = sample["timestamp"] - RETENTION_SECONDS
    removed_count = redis_client.zremrangebyscore(
        REDIS_KEY,
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

    members = {}
    for sample_timestamp in range(start_timestamp, timestamp + 1, interval_seconds):
        sample = create_sample(sample_timestamp)
        members[serialize_sample(sample)] = sample_timestamp

    redis_client.delete(REDIS_KEY)
    if members:
        redis_client.zadd(REDIS_KEY, members)

    return len(members)


def run_once(redis_client, now=None):
    timestamp = int(time.time()) if now is None else now
    sample = create_sample(timestamp)
    removed_count = save_sample(redis_client, sample)

    readable_time = datetime.fromtimestamp(timestamp, UTC).isoformat()
    print(
        f"[{readable_time}] saved "
        f"cpu={sample['cpu']} network={sample['network']} memory={sample['memory']} "
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
    print(f"Writing samples to Redis sorted set {REDIS_KEY}")
    seeded_count = reset_and_seed_history(redis_client)
    print(f"Seeded {seeded_count} samples covering the last 2 hours")
    run_forever(redis_client, sleep_first=True)


if __name__ == "__main__":
    main()
