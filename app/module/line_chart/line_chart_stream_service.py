from dataclasses import dataclass
import json
from queue import Full, Queue
import threading
import uuid

from flask import current_app

from app.module.line_chart import line_chart_redis_repository, line_chart_service
from app.shared.utils import number_utils


@dataclass
class _Subscriber:
    series: set[str]
    queue: Queue


class LineChartStreamHub:
    def __init__(
        self,
        channel: str = line_chart_redis_repository.LIVE_UPDATES_CHANNEL,
        queue_size: int = 200,
    ):
        self._channel = channel
        self._queue_size = queue_size
        self._lock = threading.Lock()
        self._subscribers: dict[str, _Subscriber] = {}
        self._listener_thread: threading.Thread | None = None
        self._listener_stop_event = threading.Event()

    def subscribe(self, series: list[str]) -> tuple[str, Queue]:
        connection_id = str(uuid.uuid4())
        queue: Queue = Queue(maxsize=self._queue_size)
        normalized_series = set(line_chart_service.normalize_series(series))

        with self._lock:
            self._subscribers[connection_id] = _Subscriber(series=normalized_series, queue=queue)

        return connection_id, queue

    def unsubscribe(self, connection_id: str) -> None:
        with self._lock:
            self._subscribers.pop(connection_id, None)

    def subscriber_count(self) -> int:
        with self._lock:
            return len(self._subscribers)

    def ensure_listener_started(self) -> None:
        with self._lock:
            if self._listener_thread and self._listener_thread.is_alive():
                return

            self._listener_stop_event.clear()
            redis_url = str(current_app.config["REDIS_URL"])
            listener_thread = threading.Thread(
                target=self._listen_to_redis,
                args=(redis_url,),
                daemon=True,
                name="line-chart-pubsub-listener",
            )
            listener_thread.start()
            self._listener_thread = listener_thread

    def handle_pubsub_message(self, raw_payload: str) -> None:
        try:
            payload = json.loads(raw_payload)
        except (TypeError, json.JSONDecodeError):
            return

        if not isinstance(payload, dict):
            return

        series_name = payload.get("series")
        timestamp = number_utils.to_int_or_none(payload.get("timestamp"))
        value = number_utils.to_float_or_none(payload.get("value"))
        if not isinstance(series_name, str) or timestamp is None or value is None:
            return

        self.publish(series_name, timestamp, value)

    def publish(self, series_name: str, timestamp: int, value: float) -> None:
        with self._lock:
            subscribers = [
                subscriber
                for subscriber in self._subscribers.values()
                if series_name in subscriber.series
            ]

        for subscriber in subscribers:
            payload = {
                "series": series_name,
                "timestamp": timestamp,
                "value": value,
            }

            try:
                subscriber.queue.put_nowait(payload)
            except Full:
                # Drop events for slow clients to avoid unbounded memory growth.
                continue

    def _listen_to_redis(self, redis_url: str) -> None:
        line_chart_redis_repository.listen_for_live_updates(
            redis_url=redis_url,
            handle_message=self.handle_pubsub_message,
            should_stop=self._listener_stop_event.is_set,
            channel=self._channel,
        )


line_chart_stream_hub = LineChartStreamHub()
