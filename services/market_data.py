import pandas as pd
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class MarketDataService:
    def __init__(self):
        self.polygon_key = os.getenv('POLYGON_API_KEY')
        self.fmp_key = os.getenv('FMP_API_KEY')

    def get_stock_data(self, symbol, start_date, end_date):
        """Fetch stock data using Polygon API"""
        try:
            url = (
                f"https://api.polygon.io/v2/aggs/ticker/{symbol.upper()}/range/1/day/"
                f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                f"?adjusted=true&sort=asc&limit=5000&apiKey={self.polygon_key}"
            )
            response = requests.get(url)
            data = response.json()
            if 'results' not in data:
                print(f"Polygon API error: {data}")
                return None
            df = pd.DataFrame(data['results'])
            df['t'] = pd.to_datetime(df['t'], unit='ms')
            df.set_index('t', inplace=True)
            df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
        except Exception as e:
            print(f"Error fetching stock data from Polygon: {e}")
            return None

    def get_crypto_data(self, symbol, start_date, end_date):
        """Fetch crypto data using Polygon API (vs USD)"""
        try:
            url = (
                f"https://api.polygon.io/v2/aggs/ticker/X:{symbol.upper()}USD/range/1/day/"
                f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                f"?adjusted=true&sort=asc&limit=5000&apiKey={self.polygon_key}"
            )
            response = requests.get(url)
            data = response.json()
            if 'results' not in data:
                print(f"Polygon API error: {data}")
                return None
            df = pd.DataFrame(data['results'])
            df['t'] = pd.to_datetime(df['t'], unit='ms')
            df.set_index('t', inplace=True)
            df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
        except Exception as e:
            print(f"Error fetching crypto data from Polygon: {e}")
            return None

    def get_news(self, symbol):
        """Fetch news data using FMP API"""
        try:
            url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=5&apikey={self.fmp_key}"
            response = requests.get(url)
            data = response.json()
            
            if isinstance(data, dict) and 'Error Message' in data:
                print(f"FMP API subscription error: {data['Error Message']}")
                return []
            
            if isinstance(data, list):
                processed_news = []
                for item in data:
                    if isinstance(item, dict):
                        processed_item = {
                            'title': item.get('title', 'No title available'),
                            'url': item.get('url', '#'),
                            'publishedDate': item.get('publishedDate', ''),
                            'text': item.get('text', '')
                        }
                        processed_news.append(processed_item)
                return processed_news
            return []
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def calculate_technical_indicators(self, data):
        """Calculate basic technical indicators"""
        if data is None or data.empty:
            return None

        data['SMA20'] = data['Close'].rolling(window=20).mean()
        data['SMA50'] = data['Close'].rolling(window=50).mean()

        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['MACD_Histogram'] = data['MACD'] - data['Signal_Line']

        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        data['BB_Upper'] = data['BB_Middle'] + 2 * data['Close'].rolling(window=20).std()
        data['BB_Lower'] = data['BB_Middle'] - 2 * data['Close'].rolling(window=20).std()

        data['Momentum'] = data['Close'].pct_change(periods=10) * 100

        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()

        return data 