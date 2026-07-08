from datetime import timedelta

def iso8601(td):
    days = td.days
    seconds = td.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    duration = "P"
    if days > 0:
        duration += f"{days}D"
    if hours > 0 or minutes > 0 or seconds > 0:
        duration += "T"
        if hours > 0:
            duration += f"{hours}H"
        if minutes > 0:
            duration += f"{minutes}M"
        if seconds > 0:
            duration += f"{seconds}S"
    return duration