"""
Video processing functions for YouTube Sentiment Analyzer
"""

import pandas as pd
import re
import time
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    if pd.isna(url) or str(url).strip() == '':
        return None

    url = str(url).strip()

    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'  # Direct video ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_transcript(video_id):
    """Get transcript for a YouTube video"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([entry['text'] for entry in transcript_list])
        return transcript_list, full_transcript
    except Exception as e:
        print(f"  ❌ Could not retrieve transcript for video {video_id}: {str(e)}")
        return None, None


def analyze_video_segments(transcript_list, analyze_sentiment_func, analyze_emotions_func):
    """Analyze sentiment and emotions for video segments"""
    if not transcript_list:
        return []

    segment_size = 30  # seconds
    segments = []
    current_segment = []
    current_start = 0

    for entry in transcript_list:
        if not current_segment:
            current_start = entry['start']

        current_segment.append(entry['text'])

        # Create segment every 30 seconds or at end
        if entry['start'] - current_start >= segment_size or entry == transcript_list[-1]:
            segment_text = ' '.join(current_segment)
            sentiment_analysis = analyze_sentiment_func(segment_text)
            emotion_analysis = analyze_emotions_func(segment_text)

            segments.append({
                'start_time': current_start,
                'end_time': entry['start'] + entry.get('duration', 0),
                'text': segment_text,
                'sentiment': sentiment_analysis['sentiment'],
                'polarity': sentiment_analysis['polarity'],
                'subjectivity': sentiment_analysis['subjectivity'],
                **emotion_analysis
            })

            current_segment = []

    return segments


def process_single_video(video_id, row_number, row_data, analyze_sentiment_func, analyze_emotions_func):
    """Process a single video"""
    try:
        # Get transcript
        transcript_list, full_transcript = get_video_transcript(video_id)

        if not full_transcript:
            return None

        # Overall analysis
        overall_sentiment = analyze_sentiment_func(full_transcript)
        overall_emotions = analyze_emotions_func(full_transcript)

        # Segment analysis
        segments = analyze_video_segments(transcript_list, analyze_sentiment_func, analyze_emotions_func)

        # Store results
        video_result = {
            'row_number': row_number,
            'video_id': video_id,
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'overall_sentiment': overall_sentiment,
            'overall_emotions': overall_emotions,
            'segments': segments,
            'total_segments': len(segments),
            'video_length': max([s['end_time'] for s in segments]) if segments else 0,
            'word_count': len(full_transcript.split()),
            'original_row_data': dict(row_data)  # Store original CSV data
        }

        print(f"  ✅ Success! Sentiment: {overall_sentiment['sentiment'].upper()}, Segments: {len(segments)}")
        return video_result

    except Exception as e:
        print(f"  ❌ Error processing video {video_id}: {str(e)}")
        return None