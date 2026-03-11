import json
import unittest
from unittest.mock import Mock, patch

from app.module.line_chart.services import line_chart_service
from app.shared.schemas.line_chart_schema import LineChartHistoryRequest


class LineChartServiceTestCase(unittest.TestCase):
    def test_fetch_history_returns_requested_series(self):
        redis_client = Mock()
        redis_client.zrangebyscore.return_value = [
            json.dumps({"timestamp": 1710000000, "cpu": 20, "network": 120, "memory": 45}),
            json.dumps({"timestamp": 1710000005, "cpu": 22, "network": 125, "memory": 46}),
        ]

        with patch.object(line_chart_service.redis_ext, "get_redis", return_value=redis_client):
            result, status = line_chart_service.fetch_history(
                LineChartHistoryRequest(
                    start=1709999999,
                    end=1710000010,
                    series=["cpu", "memory"],
                ),
            )

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "series": [
                    {
                        "name": "cpu",
                        "data": [
                            {"x": 1710000000, "y": 20.0},
                            {"x": 1710000005, "y": 22.0},
                        ],
                    },
                    {
                        "name": "memory",
                        "data": [
                            {"x": 1710000000, "y": 45.0},
                            {"x": 1710000005, "y": 46.0},
                        ],
                    },
                ],
            },
        )

    def test_fetch_history_tolerates_malformed_rows(self):
        redis_client = Mock()
        redis_client.zrangebyscore.return_value = [
            "not-json",
            json.dumps({"timestamp": "bad", "cpu": 1}),
            json.dumps({"timestamp": 1710000000, "cpu": "n/a"}),
            json.dumps({"timestamp": 1710000005, "cpu": 18.5}),
        ]

        with patch.object(line_chart_service.redis_ext, "get_redis", return_value=redis_client):
            result, status = line_chart_service.fetch_history(
                LineChartHistoryRequest(
                    start=1710000000,
                    end=1710000010,
                    series=["cpu"],
                ),
            )

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "series": [
                    {
                        "name": "cpu",
                        "data": [{"x": 1710000005, "y": 18.5}],
                    },
                ],
            },
        )

    def test_fetch_history_returns_empty_series_for_empty_window(self):
        redis_client = Mock()
        redis_client.zrangebyscore.return_value = []

        with patch.object(line_chart_service.redis_ext, "get_redis", return_value=redis_client):
            result, status = line_chart_service.fetch_history(
                LineChartHistoryRequest(start=1, end=2, series=["cpu", "network"]),
            )

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "series": [
                    {"name": "cpu", "data": []},
                    {"name": "network", "data": []},
                ],
            },
        )

    def test_fetch_history_rejects_invalid_time_range(self):
        result, status = line_chart_service.fetch_history(
            LineChartHistoryRequest(start=2, end=1, series=["cpu"]),
        )

        self.assertEqual(status, 400)
        self.assertEqual(result, {"error": "start must be less than or equal to end"})


if __name__ == "__main__":
    unittest.main()
