from collections.abc import Iterable
import json

from app.module.line_chart import line_chart_redis_repository
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
        return {"error": "start must be less than or equal to end"}, 400

    selected_series = normalize_series(body.series)
    rows = line_chart_redis_repository.fetch_history_rows(body.start, body.end)

    points_by_series: dict[str, list[LineChartPoint]] = {
        series_name: []
        for series_name in selected_series
    }

    for row in rows:
        sample = _parse_sample(row)
        if not sample:
            continue

        timestamp = number_utils.to_int_or_none(sample.get("timestamp"))
        if timestamp is None:
            continue

        for series_name in selected_series:
            value = number_utils.to_float_or_none(sample.get(series_name))
            if value is None:
                continue
            points_by_series[series_name].append(
                LineChartPoint(x=timestamp, y=value),
            )

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


def _parse_sample(raw_row: str) -> dict | None:
    try:
        payload = json.loads(raw_row)
    except (TypeError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None

    return payload
