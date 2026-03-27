import unittest
from unittest.mock import patch

from app.module.line_chart import line_chart_service
from app.shared.registry.line_chart_series_registry import AVAILABLE_SERIES
from app.shared.schemas.line_chart_schema import LineChartHistoryRequest, LineChartPoint, LineChartSeries


class LineChartServiceTestCase(unittest.TestCase):
    def test_parse_series_query_defaults_to_available_series(self):
        self.assertEqual(line_chart_service.parse_series_query(None), list(AVAILABLE_SERIES))
        self.assertEqual(
            line_chart_service.parse_series_query(None),
            ["cpu", "network", "memory", "btc", "abc"],
        )

    def test_fetch_history_returns_requested_series(self):
        history_series = [
            LineChartSeries(
                name="cpu",
                data=[
                    LineChartPoint(x=1710000000, y=20.0),
                    LineChartPoint(x=1710000005, y=22.0),
                ],
            ),
            LineChartSeries(
                name="memory",
                data=[
                    LineChartPoint(x=1710000000, y=45.0),
                    LineChartPoint(x=1710000005, y=46.0),
                ],
            ),
        ]

        with patch.object(
            line_chart_service.line_chart_redis_repository,
            "fetch_history_series",
            return_value=history_series,
        ) as fetch_history_series:
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
        fetch_history_series.assert_called_once_with(["cpu", "memory"], 1709999999, 1710000010)

    def test_fetch_history_returns_empty_series_for_empty_window(self):
        with patch.object(
            line_chart_service.line_chart_redis_repository,
            "fetch_history_series",
            return_value=[
                LineChartSeries(name="cpu", data=[]),
                LineChartSeries(name="network", data=[]),
            ],
        ) as fetch_history_series:
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
        fetch_history_series.assert_called_once_with(["cpu", "network"], 1, 2)

    def test_fetch_history_rejects_invalid_time_range(self):
        result, status = line_chart_service.fetch_history(
            LineChartHistoryRequest(start=2, end=1, series=["cpu"]),
        )

        self.assertEqual(status, 400)
        self.assertEqual(result.model_dump(), {"error": "start must be less than or equal to end"})

    def test_fetch_history_wraps_repository_series_without_normalization(self):
        with patch.object(
            line_chart_service.line_chart_redis_repository,
            "fetch_history_series",
            return_value=[
                LineChartSeries(name="CPU", data=[]),
                LineChartSeries(name="cpu", data=[LineChartPoint(x=1710000000, y=20.0)]),
                LineChartSeries(name="cpu", data=[LineChartPoint(x=1710000000, y=20.0)]),
            ],
        ) as fetch_history_series:
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
        fetch_history_series.assert_called_once_with(["CPU", "cpu", "cpu"], 1710000000, 1710000010)


if __name__ == "__main__":
    unittest.main()
