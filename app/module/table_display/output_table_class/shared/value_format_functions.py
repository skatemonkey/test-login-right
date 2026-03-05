def _to_float(value):
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def format_func_1(value):
    numeric_value = _to_float(value)
    if numeric_value is None or abs(numeric_value) < 1000:
        return value

    if numeric_value.is_integer():
        return f"{int(numeric_value):,}"

    return f"{numeric_value:,.10f}".rstrip("0").rstrip(".")


VALUE_FORMAT_FUNCTIONS = {
    1: format_func_1
}
