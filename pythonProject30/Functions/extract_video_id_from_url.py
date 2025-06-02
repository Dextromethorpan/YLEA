import re

def extract_video_id_from_url(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", str(url))
    return match.group(1) if match else None