import re

def extract_hashtags(text):
    return " ".join(re.findall(r"#\w+", text)) if isinstance(text, str) else ""