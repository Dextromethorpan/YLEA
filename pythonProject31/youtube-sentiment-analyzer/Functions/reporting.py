"""
Reporting functions for YouTube Sentiment Analyzer
"""

import os
import pandas as pd
from datetime import datetime
from collections import defaultdict


def generate_report(results, csv_file_path, output_folder):
    """Generate a comprehensive text report"""
    if not results:
        print("❌ No results to report")
        return

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("YOUTUBE VIDEO SENTIMENT ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Source CSV: {os.path.basename(csv_file_path)}")
    report_lines.append(f"Total Videos Analyzed: {len(results)}")

    # Overall Statistics
    report_lines.append("\n" + "-" * 50)
    report_lines.append("OVERALL STATISTICS")
    report_lines.append("-" * 50)

    sentiment_distribution = defaultdict(int)
    total_segments = 0
    total_words = 0
    total_duration = 0

    for result in results:
        sentiment_distribution[result['overall_sentiment']['sentiment']] += 1
        total_segments += len(result['segments'])
        total_words += result['word_count']
        total_duration += result['video_length']

    report_lines.append(f"Total Segments Analyzed: {total_segments:,}")
    report_lines.append(f"Total Words Processed: {total_words:,}")
    report_lines.append(f"Total Duration: {total_duration / 3600:.1f} hours")
    report_lines.append(f"Average Video Length: {total_duration / len(results) / 60:.1f} minutes")
    report_lines.append(f"Average Words per Video: {total_words / len(results):.0f}")

    report_lines.append("\nSentiment Distribution:")
    for sentiment, count in sentiment_distribution.items():
        percentage = (count / len(results)) * 100
        report_lines.append(f"  {sentiment.capitalize()}: {count} videos ({percentage:.1f}%)")

    # Emotion Analysis
    report_lines.append("\n" + "-" * 50)
    report_lines.append("EMOTION ANALYSIS")
    report_lines.append("-" * 50)

    emotion_totals = defaultdict(float)
    for result in results:
        for emotion, score in result['overall_emotions'].items():
            emotion_totals[emotion] += score

    sorted_emotions = sorted(emotion_totals.items(), key=lambda x: x[1], reverse=True)
    report_lines.append("Average Emotion Scores (ranked by intensity):")
    for emotion, total_score in sorted_emotions:
        avg_score = total_score / len(results)
        report_lines.append(f"  {emotion.capitalize():>12}: {avg_score:>6.2f}")

    # Top and Bottom Videos
    report_lines.append("\n" + "-" * 50)
    report_lines.append("NOTABLE VIDEOS")
    report_lines.append("-" * 50)

    # Most positive
    most_positive = max(results, key=lambda x: x['overall_sentiment']['polarity'])
    report_lines.append(f"Most Positive Video:")
    report_lines.append(f"  Video ID: {most_positive['video_id']}")
    report_lines.append(f"  Polarity: {most_positive['overall_sentiment']['polarity']:.3f}")
    report_lines.append(f"  URL: {most_positive['url']}")

    # Most negative
    most_negative = min(results, key=lambda x: x['overall_sentiment']['polarity'])
    report_lines.append(f"\nMost Negative Video:")
    report_lines.append(f"  Video ID: {most_negative['video_id']}")
    report_lines.append(f"  Polarity: {most_negative['overall_sentiment']['polarity']:.3f}")
    report_lines.append(f"  URL: {most_negative['url']}")

    # Most emotional (highest total emotion scores)
    most_emotional = max(results, key=lambda x: sum(x['overall_emotions'].values()))
    total_emotion = sum(most_emotional['overall_emotions'].values())
    report_lines.append(f"\nMost Emotional Video:")
    report_lines.append(f"  Video ID: {most_emotional['video_id']}")
    report_lines.append(f"  Total Emotion Score: {total_emotion:.2f}")
    report_lines.append(f"  URL: {most_emotional['url']}")

    # Print and save report
    report_text = "\n".join(report_lines)
    print(report_text)

    # Save report to file in output folder
    report_filename = os.path.join(output_folder, f'sentiment_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"\n📄 Report saved as: {report_filename}")

    return report_filename


def save_results(results, emotion_keywords, output_folder):
    """Save all results to CSV files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed segment analysis in output folder
    segment_df = create_segment_table(results, emotion_keywords)
    segment_filename = os.path.join(output_folder, f'sentiment_segments_{timestamp}.csv')
    segment_df.to_csv(segment_filename, index=False)
    print(f"💾 Segment analysis saved as: {segment_filename}")

    # Save overall video results in output folder
    overall_results = []
    for result in results:
        overall_data = {
            'row_number': result['row_number'],
            'video_id': result['video_id'],
            'url': result['url'],
            'video_length_seconds': round(result['video_length'], 1),
            'video_length_minutes': round(result['video_length'] / 60, 1),
            'total_segments': result['total_segments'],
            'word_count': result['word_count'],
            'overall_sentiment': result['overall_sentiment']['sentiment'],
            'polarity': round(result['overall_sentiment']['polarity'], 3),
            'subjectivity': round(result['overall_sentiment']['subjectivity'], 3)
        }

        # Add emotion scores
        for emotion, score in result['overall_emotions'].items():
            overall_data[f'{emotion}_score'] = round(score, 3)

        overall_results.append(overall_data)

    overall_df = pd.DataFrame(overall_results)
    overall_filename = os.path.join(output_folder, f'overall_sentiment_results_{timestamp}.csv')
    overall_df.to_csv(overall_filename, index=False)
    print(f"💾 Overall results saved as: {overall_filename}")

    return segment_filename, overall_filename


def create_segment_table(results, emotion_keywords):
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