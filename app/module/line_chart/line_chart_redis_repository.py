from collections.abc import Callable
import json
import time

import redis

from app.core import redis_ext
from app.shared.schemas.line_chart_schema import LineChartPoint, LineChartSeries
from app.shared.utils import number_utils

HISTORY_KEY_PREFIX = "chart_history:"
LIVE_UPDATES_CHANNEL = "line_chart:updates"
RECONNECT_DELAY_SECONDS = 1


def history_key(series_name: str) -> str:
    return f"{HISTORY_KEY_PREFIX}{series_name}"


def fetch_history_series(series_names: list[str], start: int, end: int) -> list[LineChartSeries]:
    redis_client = redis_ext.get_redis()
    pipeline = redis_client.pipeline()

    for series_name in series_names:
        pipeline.zrangebyscore(history_key(series_name), start, end)

    rows = pipeline.execute()
    return [
        LineChartSeries(name=series_name, data=_parse_points(series_rows))
        for series_name, series_rows in zip(series_names, rows, strict=False)
    ]


def _parse_points(rows: list[str]) -> list[LineChartPoint]:
    points: list[LineChartPoint] = []

    for row in rows:
        point = _parse_point(row)
        if point is not None:
            points.append(point)

    return points


def _parse_point(raw_row: str) -> LineChartPoint | None:
    try:
        payload = json.loads(raw_row)
    except (TypeError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None

    timestamp = number_utils.to_int_or_none(payload.get("timestamp"))
    value = number_utils.to_float_or_none(payload.get("value"))
    if timestamp is None or value is None:
        return None

    return LineChartPoint(x=timestamp, y=value)


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
