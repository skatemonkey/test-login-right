import json
from queue import Empty, Queue
import unittest
from unittest.mock import Mock, patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.module.notification import notification_routes
from app.module.notification.notification_routes import notification_bp
from app.shared.schemas.api_response_schema import ErrorResponse
from app.shared.schemas.notification_schema import (
    MockApproveResponse,
    NotificationSseEvent,
    NotificationUnreadCountResponse,
)
from app.shared.schemas.sse_schema import SseConnectedPayload


class NotificationRoutesTestCase(unittest.TestCase):
    @staticmethod
    def _sse_data(chunk: str) -> dict:
        return json.loads(chunk.split("data: ", 1)[1].strip())

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["JWT_SECRET_KEY"] = "notification-route-test-secret-with-32-plus-bytes"

        JWTManager(self.app)
        self.app.register_blueprint(notification_bp, url_prefix="/notifications")

        with self.app.app_context():
            token = create_access_token(identity="1")

        self.client = self.app.test_client()
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_mark_notification_as_read_returns_no_content_on_success(self):
        with patch(
            "app.module.notification.notification_routes.notification_service.mark_as_read",
            return_value=(None, 204),
        ) as mark_as_read:
            response = self.client.patch(
                "/notifications/9/read",
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(), b"")
        mark_as_read.assert_called_once_with(9, 1)

    def test_mark_notification_as_read_returns_error_response_when_missing(self):
        with patch(
            "app.module.notification.notification_routes.notification_service.mark_as_read",
            return_value=(ErrorResponse(error="Notification not found"), 404),
        ) as mark_as_read:
            response = self.client.patch(
                "/notifications/9/read",
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Notification not found"})
        mark_as_read.assert_called_once_with(9, 1)

    def test_mark_all_notifications_as_read_returns_no_content_on_success(self):
        with patch(
            "app.module.notification.notification_routes.notification_service.mark_all_as_read",
            return_value=(None, 204),
        ) as mark_all_as_read:
            response = self.client.patch(
                "/notifications/read-all",
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(), b"")
        mark_all_as_read.assert_called_once_with(1)

    def test_get_unread_count_returns_response_model_payload(self):
        with patch(
            "app.module.notification.notification_routes.notification_service.get_unread_count",
            return_value=(
                NotificationUnreadCountResponse(userId=1, unreadCount=4),
                200,
            ),
        ) as get_unread_count:
            response = self.client.get(
                "/notifications/unread-count",
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "userId": 1,
                "unreadCount": 4,
            },
        )
        get_unread_count.assert_called_once_with(1)

    def test_mock_approve_returns_response_model_payload(self):
        created = {
            "message": "Notification sent",
            "notification": {
                "id": 7,
                "userId": 5,
                "message": "Item 42 was approved by user 1.",
                "isRead": False,
                "createdAt": "2024-02-03 04:05:06",
            },
        }

        with patch(
            "app.module.notification.notification_routes.notification_service.create_notification",
            return_value=(created, 201),
        ) as create_notification:
            response = self.client.post(
                "/notifications/mock-approve",
                headers=self.auth_headers,
                json={"targetUserId": 5, "itemId": 42},
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json(),
            MockApproveResponse(
                message="Approve action mocked and notification sent",
                approverUserId=1,
                targetUserId=5,
                itemId=42,
                notification=created["notification"],
            ).model_dump(),
        )
        create_notification.assert_called_once_with(
            user_id=5,
            message="Item 42 was approved by user 1.",
        )

    def test_stream_notifications_emits_connected_and_notification_event(self):
        event_queue: Queue = Queue()
        event_queue.put(
            {
                "type": "notification.created",
                "notification": {
                    "id": 7,
                    "userId": 1,
                    "message": "approved",
                    "isRead": False,
                    "createdAt": "2024-02-03 04:05:06",
                },
            },
        )

        fake_hub = Mock()
        fake_hub.subscribe.return_value = ("conn-1", event_queue)

        with patch.object(notification_routes, "notification_stream") as notification_stream:
            notification_stream.notification_hub = fake_hub
            response = self.client.get(
                "/notifications/stream",
                headers=self.auth_headers,
                buffered=False,
            )

            stream = iter(response.response)
            connected_chunk = next(stream).decode("utf-8")
            notification_chunk = next(stream).decode("utf-8")
            response.close()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._sse_data(connected_chunk),
            SseConnectedPayload(message="connected").model_dump(),
        )
        self.assertEqual(
            self._sse_data(notification_chunk),
            NotificationSseEvent(
                type="notification.created",
                notification={
                    "id": 7,
                    "userId": 1,
                    "message": "approved",
                    "isRead": False,
                    "createdAt": "2024-02-03 04:05:06",
                },
            ).model_dump(),
        )
        fake_hub.subscribe.assert_called_once_with(1)
        fake_hub.unsubscribe.assert_called_once_with(1, "conn-1")

    def test_stream_notifications_keeps_ping_as_comment(self):
        event_queue = Mock()
        event_queue.get.side_effect = Empty()

        fake_hub = Mock()
        fake_hub.subscribe.return_value = ("conn-1", event_queue)

        with patch.object(notification_routes, "notification_stream") as notification_stream:
            notification_stream.notification_hub = fake_hub
            response = self.client.get(
                "/notifications/stream",
                headers=self.auth_headers,
                buffered=False,
            )

            stream = iter(response.response)
            next(stream)
            ping_chunk = next(stream).decode("utf-8")
            response.close()

        self.assertEqual(ping_chunk, ": ping\n\n")
        fake_hub.subscribe.assert_called_once_with(1)
        fake_hub.unsubscribe.assert_called_once_with(1, "conn-1")


if __name__ == "__main__":
    unittest.main()
