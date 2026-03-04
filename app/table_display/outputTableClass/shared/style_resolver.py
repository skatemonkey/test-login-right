from .style_functions import STYLE_FUNCTIONS


def _default_style(style_settings):
    if not style_settings:
        return 0
    return style_settings.get("default", 0)


def _get_style_rule(style_settings, row, col):
    if not style_settings:
        return _default_style(style_settings)

    cell_rule = style_settings.get("cell", {}).get((row, col))
    if cell_rule is not None:
        return cell_rule

    row_rule = style_settings.get("row", {}).get(row)
    if row_rule is not None:
        return row_rule

    col_rule = style_settings.get("col", {}).get(col)
    if col_rule is not None:
        return col_rule

    return _default_style(style_settings)


def get_style(style_settings, row, col, value):
    rule = _get_style_rule(style_settings, row, col)

    if isinstance(rule, int):
        return rule

    if isinstance(rule, str):
        style_function = STYLE_FUNCTIONS.get(rule)
        if not style_function:
            return _default_style(style_settings)
        try:
            return int(style_function(value))
        except (TypeError, ValueError):
            return _default_style(style_settings)

    return _default_style(style_settings)
