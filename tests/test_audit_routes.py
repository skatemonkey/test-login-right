import unittest
from unittest.mock import patch

from flask import Flask

from app.module.audit.audit_routes import audit_bp


class AuditRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.register_blueprint(audit_bp, url_prefix="/audit")
        self.client = self.app.test_client()

    def test_create_log_returns_no_content_on_success(self):
        with patch(
            "app.module.audit.audit_routes.audit_service.create_log",
            return_value=(None, 204),
        ) as create_log:
            response = self.client.post(
                "/audit/log",
                json={
                    "userId": 1,
                    "module": "audit",
                    "action": "create",
                    "device": "browser",
                    "details": {"source": "ui"},
                },
            )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(), b"")
        create_log.assert_called_once()


if __name__ == "__main__":
    unittest.main()
