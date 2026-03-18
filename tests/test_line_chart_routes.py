from queue import Queue
import unittest
from unittest.mock import Mock, patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.module.line_chart import line_chart_routes
from app.module.line_chart.line_chart_routes import line_chart_bp
from app.shared.schemas.line_chart_schema import LineChartHistoryResponse, LineChartPoint, LineChartSeries


class LineChartRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["JWT_SECRET_KEY"] = "line-chart-test-secret-with-32-plus-bytes"
        self.app.config["JWT_TOKEN_LOCATION"] = ["headers", "query_string"]
        self.app.config["JWT_QUERY_STRING_NAME"] = "access_token"
        self.app.config["JWT_QUERY_STRING_VALUE_PREFIX"] = ""

        JWTManager(self.app)
        self.app.register_blueprint(line_chart_bp, url_prefix="/line-chart")

        with self.app.app_context():
            self.token = create_access_token(identity="1")

        self.client = self.app.test_client()
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    def test_history_requires_authentication(self):
        response = self.client.post(
            "/line-chart/history",
            json={"start": 1, "end": 2, "series": ["cpu"]},
        )

        self.assertEqual(response.status_code, 401)

    def test_stream_requires_authentication(self):
        response = self.client.get("/line-chart/stream")

        self.assertEqual(response.status_code, 401)

    def test_history_route_returns_service_payload(self):
        response_payload = LineChartHistoryResponse(
            series=[
                LineChartSeries(name="cpu", data=[LineChartPoint(x=1710000000, y=10.0)]),
            ],
        )

        with patch.object(
            line_chart_routes.line_chart_service,
            "fetch_history",
            return_value=(response_payload, 200),
        ) as fetch_history:
            response = self.client.post(
                "/line-chart/history",
                json={"start": 1710000000, "end": 1710000060, "series": ["cpu"]},
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), response_payload.model_dump())
        fetch_history.assert_called_once()

    def test_stream_route_emits_connected_and_point_event(self):
        event_queue: Queue = Queue()
        event_queue.put({"timestamp": 1710000000, "values": {"cpu": 42.0}})

        fake_hub = Mock()
        fake_hub.subscribe.return_value = ("conn-1", event_queue)

        with patch.object(line_chart_routes.line_chart_stream_service, "line_chart_stream_hub", fake_hub):
            response = self.client.get(
                "/line-chart/stream?series=cpu,memory",
                headers=self.auth_headers,
                buffered=False,
            )

            stream = iter(response.response)
            connected_chunk = next(stream).decode("utf-8")
            point_chunk = next(stream).decode("utf-8")
            response.close()

        self.assertEqual(response.status_code, 200)
        self.assertIn("event: connected\n", connected_chunk)
        self.assertIn("\ndata: ", connected_chunk)
        self.assertTrue(connected_chunk.endswith("\n\n"))
        self.assertNotIn("\\ndata:", connected_chunk)
        self.assertIn("event: point\n", point_chunk)
        self.assertIn("\ndata: ", point_chunk)
        self.assertTrue(point_chunk.endswith("\n\n"))
        self.assertNotIn("\\ndata:", point_chunk)
        self.assertIn('"timestamp": 1710000000', point_chunk)
        fake_hub.subscribe.assert_called_once_with(["cpu", "memory"])
        fake_hub.ensure_listener_started.assert_called_once_with()
        fake_hub.unsubscribe.assert_called_once_with("conn-1")


if __name__ == "__main__":
    unittest.main()
