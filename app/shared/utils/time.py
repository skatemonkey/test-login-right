from datetime import datetime, timezone

UTC0 = timezone.utc
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def now_utc0():
    return datetime.now(UTC0)


def format_datetime(value: datetime | None) -> str:
    return value.strftime(DATETIME_FORMAT) if value else ""
