from collections.abc import Iterable

from app.module.line_chart import line_chart_redis_repository
from app.shared.schemas.api_response_schema import ErrorResponse
from app.shared.schemas.line_chart_schema import (
    LineChartHistoryRequest,
    LineChartHistoryResponse,
)

DEFAULT_SERIES = ("cpu", "network", "memory")


def fetch_history(body: LineChartHistoryRequest):
    if body.start > body.end:
        return ErrorResponse(error="start must be less than or equal to end"), 400

    response = LineChartHistoryResponse(
        series=line_chart_redis_repository.fetch_history_series(body.series, body.start, body.end),
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
