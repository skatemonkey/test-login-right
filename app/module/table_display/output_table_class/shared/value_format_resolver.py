from app.module.table_display.output_table_class.shared.value_format_functions import VALUE_FORMAT_FUNCTIONS


def _get_value_rule(value_format_settings, row, col):
    if not value_format_settings:
        return None

    cell_rule = value_format_settings.get("cell", {}).get((row, col))
    if cell_rule is not None:
        return cell_rule

    row_rule = value_format_settings.get("row", {}).get(row)
    if row_rule is not None:
        return row_rule

    col_rule = value_format_settings.get("col", {}).get(col)
    if col_rule is not None:
        return col_rule

    return value_format_settings.get("default")


def get_value(value_format_settings, row, col, value):
    rule = _get_value_rule(value_format_settings, row, col)
    if rule is None:
        return str(value)

    format_function = VALUE_FORMAT_FUNCTIONS.get(rule)
    if not format_function:
        return str(value)

    try:
        return str(format_function(value))
    except Exception:
        return str(value)
