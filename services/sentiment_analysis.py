import requests
import os
from dotenv import load_dotenv
from textblob import TextBlob

load_dotenv()

class SentimentAnalysisService:
    def __init__(self):
        self.arya_key = os.getenv('ARYA_API_KEY')

    def analyze_news_sentiment(self, news_data):
        """Analyze sentiment from news headlines"""
        if not news_data:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'sentiment_details': []
            }

        sentiments = []
        for news in news_data:
            if isinstance(news, dict) and 'title' in news:
                blob = TextBlob(news['title'])
                sentiment_score = blob.sentiment.polarity
                sentiment = 'bullish' if sentiment_score > 0.1 else 'bearish' if sentiment_score < -0.1 else 'neutral'
                
                sentiments.append({
                    'title': news['title'],
                    'sentiment': sentiment,
                    'score': sentiment_score
                })

        if not sentiments:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'sentiment_details': []
            }

        avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
        overall_sentiment = 'bullish' if avg_score > 0.1 else 'bearish' if avg_score < -0.1 else 'neutral'

        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': avg_score,
            'sentiment_details': sentiments
        }

    def get_sentiment_icon(self, sentiment):
        """Get emoji icon for sentiment"""
        icons = {
            'bullish': '📈',
            'bearish': '📉',
            'neutral': '➡️'
        }
        return icons.get(sentiment, '➡️')

    def get_sentiment_color(self, sentiment):
        """Get color for sentiment"""
        colors = {
            'bullish': '#00FF00',
            'bearish': '#FF0000',
            'neutral': '#808080'
        }
        return colors.get(sentiment, '#808080') 