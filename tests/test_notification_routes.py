import unittest
from unittest.mock import patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.module.notification.notification_routes import notification_bp
from app.shared.schemas.api_response_schema import ErrorResponse
from app.shared.schemas.notification_schema import NotificationUnreadCountResponse


class NotificationRoutesTestCase(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
