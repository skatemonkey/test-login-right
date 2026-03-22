import unittest

from flask import Flask

from app.shared.schemas.api_response_schema import ErrorResponse
from app.shared.utils import api_util


class ApiUtilTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True

    def test_api_response_serializes_pydantic_payload(self):
        with self.app.app_context():
            response, status = api_util.model_response(
                ErrorResponse(error="Something went wrong"),
                400,
            )

        self.assertEqual(status, 400)
        self.assertEqual(response.get_json(), {"error": "Something went wrong"})

    def test_api_model_response_returns_empty_response_for_none_payload(self):
        with self.app.app_context():
            response = api_util.model_response(None, 204)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(), b"")

    def test_api_model_response_returns_empty_response_for_no_content_status(self):
        with self.app.app_context():
            response = api_util.model_response(None, 304)

        self.assertEqual(response.status_code, 304)
        self.assertEqual(response.get_data(), b"")

    def test_api_json_response_returns_plain_payload(self):
        with self.app.app_context():
            response, status = api_util.json_response(
                {"message": "ok"},
                200,
            )

        self.assertEqual(status, 200)
        self.assertEqual(response.get_json(), {"message": "ok"})

    def test_api_json_response_returns_empty_response_for_none_payload(self):
        with self.app.app_context():
            response = api_util.json_response(None, 204)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(), b"")

    def test_api_json_response_returns_empty_response_for_no_content_status(self):
        with self.app.app_context():
            response = api_util.json_response({"message": "ignored"}, 304)

        self.assertEqual(response.status_code, 304)
        self.assertEqual(response.get_data(), b"")


if __name__ == "__main__":
    unittest.main()
