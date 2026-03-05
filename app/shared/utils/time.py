from datetime import datetime, timezone

UTC0 = timezone.utc

def now_utc0():
    return datetime.now(UTC0)
