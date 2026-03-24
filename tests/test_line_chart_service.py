import json
import unittest
from unittest.mock import Mock, patch

from app.module.line_chart import line_chart_service
from app.shared.schemas.line_chart_schema import LineChartHistoryRequest


class LineChartServiceTestCase(unittest.TestCase):
    def test_fetch_history_returns_requested_series(self):
        rows_by_series = {
            "cpu": [
                json.dumps({"timestamp": 1710000000, "value": 20}),
                json.dumps({"timestamp": 1710000005, "value": 22}),
            ],
            "memory": [
                json.dumps({"timestamp": 1710000000, "value": 45}),
                json.dumps({"timestamp": 1710000005, "value": 46}),
            ],
        }

        with patch.object(
            line_chart_service.line_chart_redis_repository,
            "fetch_history_rows",
            return_value=rows_by_series,
        ) as fetch_history_rows:
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
        fetch_history_rows.assert_called_once_with(["cpu", "memory"], 1709999999, 1710000010)

    def test_fetch_history_tolerates_malformed_rows(self):
        rows_by_series = {
            "cpu": [
                "not-json",
                json.dumps({"timestamp": "bad", "value": 1}),
                json.dumps({"timestamp": 1710000000, "value": "n/a"}),
                json.dumps({"timestamp": 1710000005, "value": 18.5}),
            ],
        }

        with patch.object(
            line_chart_service.line_chart_redis_repository,
            "fetch_history_rows",
            return_value=rows_by_series,
        ) as fetch_history_rows:
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
        fetch_history_rows.assert_called_once_with(["cpu"], 1710000000, 1710000010)

    def test_fetch_history_returns_empty_series_for_empty_window(self):
        with patch.object(
            line_chart_service.line_chart_redis_repository,
            "fetch_history_rows",
            return_value={"cpu": [], "network": []},
        ) as fetch_history_rows:
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
        fetch_history_rows.assert_called_once_with(["cpu", "network"], 1, 2)

    def test_fetch_history_rejects_invalid_time_range(self):
        result, status = line_chart_service.fetch_history(
            LineChartHistoryRequest(start=2, end=1, series=["cpu"]),
        )

        self.assertEqual(status, 400)
        self.assertEqual(result.model_dump(), {"error": "start must be less than or equal to end"})

    def test_fetch_history_preserves_requested_series_without_normalization(self):
        with patch.object(
            line_chart_service.line_chart_redis_repository,
            "fetch_history_rows",
            return_value={
                "CPU": [],
                "cpu": [json.dumps({"timestamp": 1710000000, "value": 20})],
            },
        ) as fetch_history_rows:
            result, status = line_chart_service.fetch_history(
                LineChartHistoryRequest(
                    start=1710000000,
                    end=1710000010,
                    series=["CPU", "cpu", "cpu"],
                ),
            )

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "series": [
                    {"name": "CPU", "data": []},
                    {"name": "cpu", "data": [{"x": 1710000000, "y": 20.0}]},
                    {"name": "cpu", "data": [{"x": 1710000000, "y": 20.0}]},
                ],
            },
        )
        fetch_history_rows.assert_called_once_with(["CPU", "cpu"], 1710000000, 1710000010)


if __name__ == "__main__":
    unittest.main()
