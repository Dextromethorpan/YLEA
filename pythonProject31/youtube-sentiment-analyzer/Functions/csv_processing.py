"""
CSV processing functions for YouTube Sentiment Analyzer
"""

import pandas as pd
import time
from .video_processing import extract_video_id, process_single_video


def is_csv_empty(df):
    """Check if the CSV is empty or contains no processable data"""
    if df.empty:
        print("❌ CSV file is empty (no rows)")
        return True
    
    # Find video ID/URL column
    possible_columns = ['video_id', 'url', 'video_url', 'youtube_url', 'link', 'Video ID', 'URL', 'Video URL']
    video_column = None

    for col in possible_columns:
        if col in df.columns:
            video_column = col
            break

    if video_column is None:
        print("❌ No video ID/URL column found")
        return True
    
    # Check if all video ID/URL entries are empty or NaN
    valid_entries = df[video_column].dropna()
    valid_entries = valid_entries[valid_entries.astype(str).str.strip() != '']
    
    if len(valid_entries) == 0:
        print("❌ CSV contains no valid video IDs/URLs")
        return True
    
    print(f"✅ CSV contains {len(valid_entries)} valid video entries")
    return False


def load_csv_and_process(csv_file_path, analyze_sentiment_func, analyze_emotions_func):
    """Load CSV file and process all videos"""
    try:
        print(f"📁 Loading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        print(f"✅ CSV loaded successfully. Found {len(df)} rows.")

    except Exception as e:
        print(f"❌ Error loading CSV file: {str(e)}")
        return False, []

    # Check if CSV is empty
    if is_csv_empty(df):
        return False, []

    # Try to find video ID/URL column
    possible_columns = ['video_id', 'url', 'video_url', 'youtube_url', 'link', 'Video ID', 'URL', 'Video URL']
    video_column = None

    print(f"📋 Available columns: {list(df.columns)}")

    for col in possible_columns:
        if col in df.columns:
            video_column = col
            break

    if video_column is None:
        print("❌ Could not find video ID/URL column. Please ensure your CSV has one of these columns:")
        print("   video_id, url, video_url, youtube_url, link, Video ID, URL, Video URL")
        return False, []

    print(f"🎯 Using column '{video_column}' for video IDs/URLs")

    # Process each video
    successful_videos = 0
    failed_videos = 0
    results = []

    for idx, row in df.iterrows():
        video_url_or_id = row[video_column]

        # Extract video ID
        video_id = extract_video_id(video_url_or_id)

        if not video_id:
            print(f"⚠️  Row {idx + 1}: Could not extract video ID from '{video_url_or_id}'")
            failed_videos += 1
            continue

        print(f"🎬 Processing video {idx + 1}/{len(df)}: {video_id}")

        video_result = process_single_video(video_id, idx + 1, row, analyze_sentiment_func, analyze_emotions_func)
        
        if video_result:
            results.append(video_result)
            successful_videos += 1
        else:
            failed_videos += 1

        # Small delay to be respectful to YouTube's servers
        time.sleep(0.5)

    print(f"\n📊 Processing Summary:")
    print(f"   ✅ Successful: {successful_videos}")
    print(f"   ❌ Failed: {failed_videos}")
    
    if successful_videos + failed_videos > 0:
        print(f"   📈 Success Rate: {(successful_videos / (successful_videos + failed_videos) * 100):.1f}%")

    return successful_videos > 0, results


def create_sentiment_table(results, emotion_keywords):
    """Create a table showing sentiment and emotion per segment"""
    all_segments = []

    for result in results:
        for i, segment in enumerate(result['segments']):
            segment_data = {
                'video_id': result['video_id'],
                'video_url': result['url'],
                'segment_number': i + 1,
                'start_time': round(segment['start_time'], 1),
                'end_time': round(segment['end_time'], 1),
                'duration': round(segment['end_time'] - segment['start_time'], 1),
                'sentiment': segment['sentiment'],
                'polarity': round(segment['polarity'], 3),
                'subjectivity': round(segment['subjectivity'], 3)
            }

            # Add emotion scores
            for emotion in emotion_keywords.keys():
                segment_data[f'{emotion}_score'] = round(segment.get(emotion, 0), 3)

            all_segments.append(segment_data)

    return pd.DataFrame(all_segments)