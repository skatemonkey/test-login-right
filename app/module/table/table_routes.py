from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.module.table.table_display.table_registry import TABLE_CLASSES
from app.shared.schemas.api_response_schema import ErrorResponse
from app.shared.utils import api_util

table_bp = Blueprint("table", __name__)


@table_bp.get("/layout/<int:table_id>")
@jwt_required()
def get_table_layout(table_id: int):
    table_class = TABLE_CLASSES.get(table_id)
    if not table_class:
        return api_util.model_response(ErrorResponse(error="Invalid table_id"), 404)
    return api_util.json_response(table_class().convert_to_json_layout(), 200)


@table_bp.get("/data/<int:table_id>")
@jwt_required()
def get_table_data(table_id: int):
    table_class = TABLE_CLASSES.get(table_id)
    if not table_class:
        return api_util.model_response(ErrorResponse(error="Invalid table_id"), 404)
    return api_util.json_response(table_class().convert_to_json_data(), 200)
