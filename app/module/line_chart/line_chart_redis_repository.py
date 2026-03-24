from collections.abc import Callable
import time

import redis

from app.core import redis_ext

HISTORY_KEY_PREFIX = "chart_history:"
LIVE_UPDATES_CHANNEL = "line_chart:updates"
RECONNECT_DELAY_SECONDS = 1


def history_key(series_name: str) -> str:
    return f"{HISTORY_KEY_PREFIX}{series_name}"


def fetch_history_rows(series_names: list[str], start: int, end: int) -> dict[str, list[str]]:
    redis_client = redis_ext.get_redis()
    pipeline = redis_client.pipeline()

    for series_name in series_names:
        pipeline.zrangebyscore(history_key(series_name), start, end)

    rows = pipeline.execute()
    return {
        series_name: series_rows
        for series_name, series_rows in zip(series_names, rows, strict=False)
    }


def listen_for_live_updates(
    redis_url: str,
    handle_message: Callable[[str], None],
    should_stop: Callable[[], bool],
    channel: str = LIVE_UPDATES_CHANNEL,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    while not should_stop():
        redis_client = None
        pubsub = None

        try:
            redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
            pubsub.subscribe(channel)

            for message in pubsub.listen():
                if should_stop():
                    return
                if message.get("type") != "message":
                    continue

                data = message.get("data")
                if isinstance(data, str):
                    handle_message(data)
        except Exception:
            if should_stop():
                return
            sleep(RECONNECT_DELAY_SECONDS)
        finally:
            if pubsub is not None:
                try:
                    pubsub.close()
                except Exception:
                    pass

            if redis_client is not None:
                try:
                    redis_client.close()
                except Exception:
                    pass
