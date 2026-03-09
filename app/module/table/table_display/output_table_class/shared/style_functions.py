def _to_float(value):
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def condition_func_1(value):
    numeric_value = _to_float(value)
    if numeric_value is None:
        return 5
    return 6 if numeric_value > 10 else 5


STYLE_FUNCTIONS = {
    "condition_func_1": condition_func_1
}
