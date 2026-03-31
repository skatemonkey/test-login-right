import unittest
from unittest.mock import patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.module.user.user_routes import user_bp
from app.shared.schemas.user_schema import UserOptionsResponse


class UserRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["JWT_SECRET_KEY"] = "user-route-test-secret-with-32-plus-bytes"

        JWTManager(self.app)
        self.app.register_blueprint(user_bp, url_prefix="/users")

        with self.app.app_context():
            token = create_access_token(identity="1")

        self.client = self.app.test_client()
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_get_user_options_returns_response_model_payload(self):
        with patch(
            "app.module.user.user_routes.user_service.get_user_options",
            return_value=(
                UserOptionsResponse(
                    [
                        {"userId": 2, "username": "alice"},
                        {"userId": 5, "username": "zoe"},
                    ],
                ),
                200,
            ),
        ) as get_user_options:
            response = self.client.get("/users/options", headers=self.auth_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [
                {"userId": 2, "username": "alice"},
                {"userId": 5, "username": "zoe"},
            ],
        )
        get_user_options.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
