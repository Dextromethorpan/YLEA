import os
import re
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from Functions.get_youtube_client import get_youtube_client
from Functions.extract_video_id_from_url import extract_video_id_from_url
from Functions.extract_hashtags import extract_hashtags

def enrich_video_csv_with_metadata(csv_path, api_key):
    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        print(f"⚠️ File is empty: {csv_path}. Skipping enrichment.")
        return csv_path

    if df.empty:
        print(f"⚠️ DataFrame is empty for file: {csv_path}. Skipping enrichment.")
        return csv_path

    if 'video_id' not in df.columns:
        if 'url' in df.columns:
            df['video_id'] = df['url'].apply(extract_video_id_from_url)
        else:
            raise ValueError("CSV must contain either 'video_id' or 'url' column.")

    youtube = get_youtube_client(api_key)

    subs_list = []
    age_list = []
    lang_list = []
    cat_id_list = []
    cat_name_list = []
    hashtags_list = []
    chan_desc_list = []
    category_map = {}

    for vid in df['video_id']:
        try:
            video_response = youtube.videos().list(
                part="snippet",
                id=vid
            ).execute()
            items = video_response.get('items', [])
            if not items:
                raise Exception("Video not found")

            snippet = items[0]['snippet']
            language = snippet.get('defaultLanguage') or snippet.get('language') or 'unknown'
            category_id = snippet.get('categoryId')
            title = snippet.get('title', '')
            description = snippet.get('description', '')
            hashtags = extract_hashtags(title + " " + description)
            channel_id = snippet['channelId']

            channel_response = youtube.channels().list(
                part="statistics,snippet",
                id=channel_id
            ).execute()
            chan_info = channel_response['items'][0]
            subs = int(chan_info['statistics'].get('subscriberCount', 0))
            created = chan_info['snippet']['publishedAt']
            created_dt = datetime.strptime(created, '%Y-%m-%dT%H:%M:%SZ')
            age_days = (datetime.utcnow() - created_dt).days
            channel_desc = chan_info['snippet'].get('description', '')

            if category_id and category_id not in category_map:
                cat_resp = youtube.videoCategories().list(
                    part="snippet",
                    id=category_id,
                    regionCode="US"
                ).execute()
                if cat_resp['items']:
                    category_map[category_id] = cat_resp['items'][0]['snippet']['title']
                else:
                    category_map[category_id] = "Unknown"

            subs_list.append(subs)
            age_list.append(age_days)
            lang_list.append(language)
            cat_id_list.append(category_id)
            cat_name_list.append(category_map.get(category_id, "Unknown"))
            hashtags_list.append(hashtags)
            chan_desc_list.append(channel_desc)

        except Exception as e:
            print(f"⚠️ Error with video {vid}: {e}")
            subs_list.append(None)
            age_list.append(None)
            lang_list.append(None)
            cat_id_list.append(None)
            cat_name_list.append(None)
            hashtags_list.append(None)
            chan_desc_list.append(None)

    df['subscriber_count'] = subs_list
    df['channel_age_days'] = age_list
    df['language'] = lang_list
    df['category_id'] = cat_id_list
    df['category_name'] = cat_name_list
    df['hashtags'] = hashtags_list
    df['channel_description'] = chan_desc_list

    df.to_csv(csv_path, index=False)
    print(f"Metadata added and saved to: {csv_path}")
    return csv_path
