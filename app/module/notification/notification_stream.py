import threading
import uuid
from queue import Full, Queue


class NotificationStreamHub:
    def __init__(self):
        self._lock = threading.Lock()
        self._subscribers: dict[int, dict[str, Queue]] = {}

    def subscribe(self, user_id: int) -> tuple[str, Queue]:
        connection_id = str(uuid.uuid4())
        queue: Queue = Queue(maxsize=100)

        with self._lock:
            user_subscribers = self._subscribers.setdefault(user_id, {})
            user_subscribers[connection_id] = queue
            total_for_user = len(user_subscribers)
            total_connections = self._connection_count_locked()

        print(
            f"[SSE][subscribe] user_id={user_id} connection_id={connection_id} "
            f"user_connections={total_for_user} total_connections={total_connections}",
            flush=True,
        )

        return connection_id, queue

    def unsubscribe(self, user_id: int, connection_id: str) -> None:
        with self._lock:
            user_subscribers = self._subscribers.get(user_id)
            if not user_subscribers:
                return

            user_subscribers.pop(connection_id, None)
            if not user_subscribers:
                self._subscribers.pop(user_id, None)
                total_for_user = 0
            else:
                total_for_user = len(user_subscribers)
            total_connections = self._connection_count_locked()

        print(
            f"[SSE][unsubscribe] user_id={user_id} connection_id={connection_id} "
            f"user_connections={total_for_user} total_connections={total_connections}",
            flush=True,
        )

    def publish(self, user_id: int, event: dict) -> None:
        with self._lock:
            user_subscribers = self._subscribers.get(user_id, {})
            queues = list(user_subscribers.values())
            total_for_user = len(user_subscribers)
            total_connections = self._connection_count_locked()

        print(
            f"[SSE][publish] user_id={user_id} target_connections={len(queues)} "
            f"user_connections={total_for_user} total_connections={total_connections} "
            f"event_type={event.get('type')}",
            flush=True,
        )

        for queue in queues:
            try:
                queue.put_nowait(event)
            except Full:
                # Drop events for slow clients to protect process memory.
                continue

    def _connection_count_locked(self) -> int:
        return sum(len(connections) for connections in self._subscribers.values())


notification_hub = NotificationStreamHub()
