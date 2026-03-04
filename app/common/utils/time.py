from datetime import datetime, timezone, timedelta

UTC0 = timezone.utc

def now_utc0():
    return datetime.now(UTC0)