from collections.abc import Iterable
import json

from app.module.line_chart import line_chart_redis_repository
from app.shared.schemas.api_response_schema import ErrorResponse
from app.shared.schemas.line_chart_schema import (
    LineChartHistoryRequest,
    LineChartHistoryResponse,
    LineChartPoint,
    LineChartSeries,
)
from app.shared.utils import number_utils

DEFAULT_SERIES = ("cpu", "network", "memory")


def fetch_history(body: LineChartHistoryRequest):
    if body.start > body.end:
        return ErrorResponse(error="start must be less than or equal to end"), 400

    selected_series = list(body.series)
    unique_series = list(dict.fromkeys(selected_series))
    rows_by_series = line_chart_redis_repository.fetch_history_rows(unique_series, body.start, body.end)

    points_by_series = {
        series_name: _parse_points(rows_by_series.get(series_name, []))
        for series_name in unique_series
    }

    response = LineChartHistoryResponse(
        series=[
            LineChartSeries(name=series_name, data=points_by_series[series_name])
            for series_name in selected_series
        ],
    )
    return response, 200


def normalize_series(series: Iterable[str] | None) -> list[str]:
    candidates = list(series or DEFAULT_SERIES)
    normalized: list[str] = []
    seen: set[str] = set()

    for item in candidates:
        value = str(item).strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)

    if normalized:
        return normalized

    return list(DEFAULT_SERIES)


def parse_series_query(raw_series: str | None) -> list[str]:
    if not raw_series:
        return normalize_series(None)
    return normalize_series(raw_series.split(","))


def _parse_points(rows: list[str]) -> list[LineChartPoint]:
    points: list[LineChartPoint] = []

    for row in rows:
        point = _parse_point(row)
        if point is not None:
            points.append(point)

    return points


def _parse_point(raw_row: str) -> LineChartPoint | None:
    try:
        payload = json.loads(raw_row)
    except (TypeError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None

    timestamp = number_utils.to_int_or_none(payload.get("timestamp"))
    value = number_utils.to_float_or_none(payload.get("value"))
    if timestamp is None or value is None:
        return None

    return LineChartPoint(x=timestamp, y=value)
