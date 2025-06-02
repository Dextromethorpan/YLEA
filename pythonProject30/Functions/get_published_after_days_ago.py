from datetime import datetime, timedelta, date

def get_published_after_days_ago(days):
    return (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"