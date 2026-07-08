from datetime import datetime

def utc(time: datetime) -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ')