from collections.abc import Generator
import json
from queue import Empty

from flask import Blueprint, Response, jsonify, stream_with_context
from flask_jwt_extended import jwt_required
from flask_pydantic import validate

from app.module.line_chart import line_chart_service, line_chart_stream_service
from app.shared.schemas.line_chart_schema import LineChartHistoryRequest, LineChartStreamQuery

line_chart_bp = Blueprint("line_chart", __name__)


@line_chart_bp.post("/history")
@jwt_required()
@validate()
def get_history(body: LineChartHistoryRequest):
    result, status = line_chart_service.fetch_history(body)
    return _jsonify_result(result, status)


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
            yield _to_sse(event="connected", data={"message": "connected"})

            while True:
                try:
                    payload = event_queue.get(timeout=20)
                    yield _to_sse(event="point", data=payload)
                except Empty:
                    yield ": ping\n\n"
        finally:
            line_chart_stream_service.line_chart_stream_hub.unsubscribe(connection_id)

    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response


def _jsonify_result(result, status: int):
    if hasattr(result, "model_dump"):
        return jsonify(result.model_dump()), status
    return jsonify(result), status


def _to_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
