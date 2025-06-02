"""
Visualization functions for YouTube Sentiment Analyzer
"""

import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import defaultdict
import numpy as np
import os


def create_visualizations(results, emotion_keywords, output_folder):
    """Create comprehensive visualizations"""
    if not results:
        print("❌ No results to visualize")
        return

    print("📊 Creating visualizations...")

    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")

    # Create a large figure with multiple subplots
    fig = plt.figure(figsize=(20, 16))

    # 1. Overall Sentiment Distribution
    plt.subplot(3, 3, 1)
    sentiment_counts = defaultdict(int)
    for result in results:
        sentiment_counts[result['overall_sentiment']['sentiment']] += 1

    colors = {'positive': 'green', 'negative': 'red', 'neutral': 'gray'}
    pie_colors = [colors.get(sentiment, 'blue') for sentiment in sentiment_counts.keys()]

    plt.pie(sentiment_counts.values(), labels=sentiment_counts.keys(),
            autopct='%1.1f%%', colors=pie_colors)
    plt.title('Overall Sentiment Distribution\nAcross All Videos')

    # 2. Sentiment Polarity Distribution
    plt.subplot(3, 3, 2)
    all_polarities = [result['overall_sentiment']['polarity'] for result in results]
    plt.hist(all_polarities, bins=15, alpha=0.7, color='skyblue', edgecolor='black')
    plt.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Neutral')
    plt.xlabel('Sentiment Polarity')
    plt.ylabel('Number of Videos')
    plt.title('Distribution of Sentiment Polarity')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 3. Average Emotion Scores
    plt.subplot(3, 3, 3)
    emotion_averages = defaultdict(list)

    for result in results:
        for emotion in emotion_keywords.keys():
            emotion_averages[emotion].append(result['overall_emotions'][emotion])

    emotions = list(emotion_averages.keys())
    avg_scores = [np.mean(emotion_averages[emotion]) for emotion in emotions]

    bars = plt.bar(emotions, avg_scores, alpha=0.8)
    plt.title('Average Emotion Scores\nAcross All Videos')
    plt.xlabel('Emotions')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45)

    # Color bars based on intensity
    max_score = max(avg_scores) if avg_scores else 1
    for bar, score in zip(bars, avg_scores):
        intensity = score / max_score if max_score > 0 else 0
        bar.set_color(plt.cm.Reds(intensity))

    plt.grid(True, alpha=0.3, axis='y')

    # 4. Video Length vs Sentiment
    plt.subplot(3, 3, 4)
    video_lengths = [result['video_length'] / 60 for result in results]  # Convert to minutes
    polarities = [result['overall_sentiment']['polarity'] for result in results]
    sentiments = [result['overall_sentiment']['sentiment'] for result in results]

    color_map = {'positive': 'green', 'negative': 'red', 'neutral': 'gray'}
    colors = [color_map[sentiment] for sentiment in sentiments]

    plt.scatter(video_lengths, polarities, c=colors, alpha=0.7, s=60)
    plt.xlabel('Video Length (minutes)')
    plt.ylabel('Sentiment Polarity')
    plt.title('Video Length vs Sentiment')
    plt.grid(True, alpha=0.3)

    # Add legend
    for sentiment, color in color_map.items():
        plt.scatter([], [], c=color, label=sentiment.capitalize())
    plt.legend()

    # 5. Emotion Heatmap (Top videos)
    plt.subplot(3, 3, 5)
    n_videos_to_show = min(10, len(results))
    emotion_matrix = []
    video_labels = []

    for i, result in enumerate(results[:n_videos_to_show]):
        video_labels.append(f"Video {i + 1}")
        emotion_row = [result['overall_emotions'][emotion] for emotion in emotions]
        emotion_matrix.append(emotion_row)

    if emotion_matrix:
        sns.heatmap(emotion_matrix,
                    xticklabels=emotions,
                    yticklabels=video_labels,
                    annot=True,
                    fmt='.1f',
                    cmap='YlOrRd',
                    cbar_kws={'label': 'Emotion Intensity'})
        plt.title(f'Emotion Intensity Heatmap\n(First {n_videos_to_show} Videos)')
        plt.xticks(rotation=45)

    # 6. Sentiment Timeline (Sample videos)
    plt.subplot(3, 3, 6)
    sample_videos = results[:5]  # Show first 5 videos

    for i, result in enumerate(sample_videos):
        if result['segments']:
            times = [s['start_time'] / 60 for s in result['segments']]  # Convert to minutes
            polarities = [s['polarity'] for s in result['segments']]
            plt.plot(times, polarities, label=f"Video {i + 1}", marker='o', markersize=4, alpha=0.7)

    plt.xlabel('Time (minutes)')
    plt.ylabel('Sentiment Polarity')
    plt.title('Sentiment Timeline\n(Sample Videos)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)

    # 7. Word Count vs Emotions
    plt.subplot(3, 3, 7)
    word_counts = [result['word_count'] for result in results]
    joy_scores = [result['overall_emotions']['joy'] for result in results]

    plt.scatter(word_counts, joy_scores, alpha=0.6, s=60, color='gold')
    plt.xlabel('Word Count')
    plt.ylabel('Joy Score')
    plt.title('Video Length (Words) vs Joy')
    plt.grid(True, alpha=0.3)

    # 8. Subjectivity vs Polarity
    plt.subplot(3, 3, 8)
    all_polarities = []
    all_subjectivities = []
    all_sentiments = []

    for result in results:
        all_polarities.append(result['overall_sentiment']['polarity'])
        all_subjectivities.append(result['overall_sentiment']['subjectivity'])
        all_sentiments.append(result['overall_sentiment']['sentiment'])

    colors = [color_map[sentiment] for sentiment in all_sentiments]
    plt.scatter(all_polarities, all_subjectivities, c=colors, alpha=0.7, s=60)
    plt.xlabel('Sentiment Polarity')
    plt.ylabel('Subjectivity')
    plt.title('Sentiment vs Subjectivity')
    plt.grid(True, alpha=0.3)

    # 9. Top Emotions Bar Chart
    plt.subplot(3, 3, 9)
    emotion_totals = defaultdict(float)
    for result in results:
        for emotion, score in result['overall_emotions'].items():
            emotion_totals[emotion] += score

    sorted_emotions = sorted(emotion_totals.items(), key=lambda x: x[1], reverse=True)
    emotions_sorted = [item[0] for item in sorted_emotions]
    scores_sorted = [item[1] / len(results) for item in sorted_emotions]  # Average

    bars = plt.bar(emotions_sorted, scores_sorted, alpha=0.8)
    plt.title('Average Emotion Scores\n(Ranked)')
    plt.xlabel('Emotions')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45)

    # Color gradient
    for i, bar in enumerate(bars):
        bar.set_color(plt.cm.viridis(i / len(bars)))

    plt.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # Save the plot in output folder
    output_filename = os.path.join(output_folder, f'youtube_sentiment_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"📊 Visualization saved as: {output_filename}")
    plt.show()

    return output_filename