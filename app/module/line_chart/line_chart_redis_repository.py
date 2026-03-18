from collections.abc import Callable
import time

import redis

from app.core import redis_ext

REDIS_KEY = "line_chart:points"
LIVE_UPDATES_CHANNEL = "line_chart:updates"
RECONNECT_DELAY_SECONDS = 1


def fetch_history_rows(start: int, end: int) -> list[str]:
    redis_client = redis_ext.get_redis()
    return redis_client.zrangebyscore(REDIS_KEY, start, end)


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
