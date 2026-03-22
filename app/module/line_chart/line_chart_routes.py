from collections.abc import Generator
from queue import Empty

from flask import Blueprint, Response, stream_with_context
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from app.module.line_chart import line_chart_service, line_chart_stream_service
from app.shared.schemas.line_chart_schema import (
    LineChartHistoryRequest,
    LineChartSsePoint,
    LineChartStreamQuery,
)
from app.shared.schemas.sse_schema import SseConnectedPayload
from app.shared.utils import api_util
from app.shared.utils.sse_util import to_sse

line_chart_bp = Blueprint("line_chart", __name__)


@line_chart_bp.post("/history")
@jwt_required()
@validate()
def get_history(body: LineChartHistoryRequest):
    result, status = line_chart_service.fetch_history(body)
    return api_util.model_response(result, status)


@line_chart_bp.get("/stream")
@jwt_required()
@validate()
def stream_updates(query: LineChartStreamQuery):
    selected_series = line_chart_service.parse_series_query(query.series)
    connection_id, event_queue = line_chart_stream_service.line_chart_stream_hub.subscribe(selected_series)
    line_chart_stream_service.line_chart_stream_hub.ensure_listener_started()

    @stream_with_context
    def event_stream() -> Generator[str, None, None]:
        try:
            yield to_sse(
                event="connected",
                data=SseConnectedPayload(message="connected"),
            )

            while True:
                try:
                    payload = event_queue.get(timeout=20)
                    yield to_sse(
                        event="point",
                        data=LineChartSsePoint.model_validate(payload),
                    )
                except Empty:
                    yield ": ping\n\n"
        finally:
            line_chart_stream_service.line_chart_stream_hub.unsubscribe(connection_id)

    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response
