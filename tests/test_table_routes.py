import unittest

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.module.table.table_routes import table_bp


class TableRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["JWT_SECRET_KEY"] = "table-route-test-secret-with-32-plus-bytes"

        JWTManager(self.app)
        self.app.register_blueprint(table_bp, url_prefix="/tables")

        with self.app.app_context():
            token = create_access_token(identity="1")

        self.client = self.app.test_client()
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_get_table_layout_returns_shared_error_response_for_invalid_id(self):
        response = self.client.get("/tables/layout/999", headers=self.auth_headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Invalid table_id"})

    def test_get_table_data_returns_shared_error_response_for_invalid_id(self):
        response = self.client.get("/tables/data/999", headers=self.auth_headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Invalid table_id"})


if __name__ == "__main__":
    unittest.main()
