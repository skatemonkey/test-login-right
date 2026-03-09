import os
import time
import random
import pickle
from pathlib import Path
from datetime import datetime, timedelta, timezone

pickle_path = "/Users/user/hub/dev/test/output/line_chart_1.pkl"


def floor_to_minute(ts: int) -> int:
    return ts - (ts % 60)


def generate_row(ts: int) -> dict:
    """
    Mock metric values for one timestamp.
    Replace this later with real cpu/network/memory data if needed.
    """
    return {
        "timestamp": ts,
        "cpu": round(random.uniform(10, 90), 2),
        "network": round(random.uniform(100, 1000), 2),
        "memory": round(random.uniform(20, 95), 2),
    }


def load_data(path: str) -> list:
    if not os.path.exists(path):
        return []

    with open(path, "rb") as f:
        data = pickle.load(f)

    if not isinstance(data, list):
        raise ValueError("Pickle data must be a list of dict rows.")

    return data


def save_data(path: str, data: list) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(data, f)


def backfill_missing_data(data: list) -> list:
    now_ts = floor_to_minute(int(time.time()))

    if not data:
        # First run: generate last 12 hours of minute data
        start_ts = now_ts - (12 * 60 * 60)
        for ts in range(start_ts, now_ts + 1, 60):
            data.append(generate_row(ts))
        return data

    last_ts = data[-1]["timestamp"]

    # Fill any missing minutes until now
    next_ts = last_ts + 60
    while next_ts <= now_ts:
        data.append(generate_row(next_ts))
        next_ts += 60

    return data


def seconds_until_next_minute() -> int:
    now = time.time()
    return 60 - int(now % 60)


def main():
    print(f"Using pickle file: {pickle_path}")

    data = load_data(pickle_path)
    data = backfill_missing_data(data)
    save_data(pickle_path, data)

    print(f"Initial rows: {len(data)}")
    print("Started live append loop...")

    while True:
        sleep_seconds = seconds_until_next_minute()
        time.sleep(sleep_seconds)

        current_ts = floor_to_minute(int(time.time()))

        data = load_data(pickle_path)

        if not data or data[-1]["timestamp"] < current_ts:
            data.append(generate_row(current_ts))
            save_data(pickle_path, data)
            print(f"Appended row for {current_ts} ({datetime.fromtimestamp(current_ts)})")
        else:
            print(f"Timestamp {current_ts} already exists, skipped.")


if __name__ == "__main__":
    main()