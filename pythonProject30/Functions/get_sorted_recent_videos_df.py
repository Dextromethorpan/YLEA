import pandas as pd
import isodate
from googleapiclient.errors import HttpError

def get_sorted_recent_videos_df(youtube, published_after, max_results=100):
    video_ids = []
    next_page_token = None

    print(" Searching for recent videos...")
    while len(video_ids) < max_results:
        try:
            search_response = youtube.search().list(
                part="snippet",
                type="video",
                order="date",
                maxResults=50,
                publishedAfter=published_after,
                pageToken=next_page_token
            ).execute()

            video_ids.extend([item['id']['videoId'] for item in search_response['items']])
            next_page_token = search_response.get("nextPageToken")

            if not next_page_token:
                break
        except HttpError as e:
            print(f" Search API error: {e}")
            break

    video_ids = video_ids[:max_results]
    print(f" Found {len(video_ids)} video IDs.")

    # --- Get video details ---
    videos_data = []

    print(" Fetching video details...")
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        try:
            details_response = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch_ids)
            ).execute()
        except HttpError as e:
            print(f" Error fetching details for batch: {e}")
            continue

        for video in details_response.get("items", []):
            try:
                duration = isodate.parse_duration(video["contentDetails"]["duration"]).total_seconds()
                if duration < 120:  # skip videos shorter than 2 minutes
                    continue

                videos_data.append({
                    "title": video["snippet"]["title"],
                    "channel": video["snippet"]["channelTitle"],
                    "publishedAt": video["snippet"]["publishedAt"],
                    "duration_min": round(duration / 60, 2),
                    "views": int(video["statistics"].get("viewCount", 0)),
                    "likes": int(video["statistics"].get("likeCount", 0)),
                    "comments": int(video["statistics"].get("commentCount", 0)),
                    "url": f"https://www.youtube.com/watch?v={video['id']}"
                })
            except Exception as e:
                print(f" Skipping video due to error: {e}")

    if not videos_data:
        print(" No valid videos found.")
        return pd.DataFrame()

    #  Convert to DataFrame and sort by views
    df = pd.DataFrame(videos_data)
    df = df.sort_values(by="views", ascending=False).reset_index(drop=True)
    print(f" Returning DataFrame with {len(df)} videos.")
    return df
