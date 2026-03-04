from datetime import datetime, timezone, timedelta

UTC8 = timezone(timedelta(hours=8))

def now_utc8():
    return datetime.now(UTC8)