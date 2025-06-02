from googleapiclient.discovery import build
from datetime import datetime, timedelta, date
import pandas as pd
import isodate

# 📦 Function Imports
from Functions.get_youtube_client import get_youtube_client
from Functions.get_published_after_days_ago import get_published_after_days_ago
from Functions.get_sorted_recent_videos_df import get_sorted_recent_videos_df
from Functions.save_df_to_dated_folder import save_df_to_dated_folder
from Functions.enrich_video_csv_with_metadata import enrich_video_csv_with_metadata

# 🔐 YouTube API Key
YOUTUBE_API_KEY = '...'

# 🎬 Initialize YouTube API client
youtube = get_youtube_client(YOUTUBE_API_KEY)

# 🔁 Loop from day 1 to 90
for N in range(1, 25):
    print(f"\n Processing data for the last {N} day(s)...")

    # ⏱️ Get timestamp N days ago
    published_after = get_published_after_days_ago(N)

    # 📊 Extract & sort videos
    df = get_sorted_recent_videos_df(youtube, published_after, max_results=100)

    # 💾 Save CSV to a dated folder
    filename = save_df_to_dated_folder(df, N)

    # 🧠 Enrich CSV with metadata
    enriched_filename = enrich_video_csv_with_metadata(filename, YOUTUBE_API_KEY)

    print(f"✅ Finished processing for last {N} day(s): {enriched_filename}")

