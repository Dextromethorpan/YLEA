"""
Sentiment and emotion analysis functions for YouTube Sentiment Analyzer
"""

from textblob import TextBlob


# Emotion keywords dictionary
EMOTION_KEYWORDS = {
    'joy': ['happy', 'joy', 'excited', 'cheerful', 'delighted', 'pleased', 'glad', 'wonderful', 'amazing',
            'fantastic'],
    'anger': ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed', 'frustrated', 'irritated', 'outraged'],
    'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous', 'panic', 'frightened'],
    'sadness': ['sad', 'depressed', 'miserable', 'unhappy', 'sorrowful', 'grief', 'melancholy', 'disappointed'],
    'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered', 'startled'],
    'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened', 'appalled', 'horrified'],
    'trust': ['trust', 'confident', 'secure', 'reliable', 'faith', 'believe', 'certain'],
    'anticipation': ['excited', 'eager', 'hopeful', 'optimistic', 'expecting', 'anticipating']
}


def analyze_sentiment(text):
    """Analyze sentiment using TextBlob"""
    if not text or text.strip() == '':
        return {'sentiment': 'neutral', 'polarity': 0.0, 'subjectivity': 0.0}

    blob = TextBlob(text)
    polarity = blob.polarity  # -1 (negative) to 1 (positive)
    subjectivity = blob.subjectivity  # 0 (objective) to 1 (subjective)

    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    return {
        'sentiment': sentiment,
        'polarity': polarity,
        'subjectivity': subjectivity
    }


def analyze_emotions(text):
    """Analyze emotions based on keyword matching"""
    if not text or text.strip() == '':
        return {emotion: 0.0 for emotion in EMOTION_KEYWORDS.keys()}

    text_lower = text.lower()
    emotion_scores = {}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(text_lower.count(keyword) for keyword in keywords)
        # Normalize by text length (per 1000 words)
        word_count = len(text.split())
        if word_count > 0:
            emotion_scores[emotion] = (score / word_count) * 1000
        else:
            emotion_scores[emotion] = 0.0

    return emotion_scores