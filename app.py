import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from services.market_data import MarketDataService
from services.sentiment_analysis import SentimentAnalysisService

load_dotenv()

st.set_page_config(
    page_title="CronusAGI Financial Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #181C20; color: #E0E6ED; }
    .stTextInput>div>div>input { background-color: #23272B; color: #E0E6ED; }
    .stButton>button, .stRadio [role='radio'] { background-color: #1A2233; color: #E0E6ED; }
    .stRadio [aria-checked='true'] { color: #1A8CFF !important; font-weight: bold; }
    .dashboard-card {
        background: linear-gradient(135deg, #23272B 80%, #1A8CFF11 100%);
        border-radius: 12px;
        box-shadow: 0 2px 8px #0002;
        padding: 1.5rem 1.2rem 1.2rem 1.2rem;
        margin-bottom: 1.2rem;
    }
    .metric-badge {
        display: inline-block;
        padding: 0.2em 0.7em;
        border-radius: 8px;
        font-size: 1em;
        font-weight: 600;
        margin-left: 0.5em;
    }
    .bullish { background: #0e6efd22; color: #1A8CFF; }
    .bearish { background: #ff003322; color: #FF0033; }
    .neutral { background: #88888822; color: #CCCCCC; }
    .news-item {
        background: #23272B;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.7rem;
        box-shadow: 0 1px 4px #0001;
    }
    .news-title { color: #1A8CFF; font-size: 1.1em; font-weight: 600; }
    .news-link { color: #1A8CFF; text-decoration: underline; }
    .divider { border-top: 1px solid #222C; margin: 1.5rem 0 1rem 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='display: flex; align-items: center; gap: 1rem;'>
    <span style='font-size:2.2rem;'>📈</span>
    <span style='font-size:2.1rem; font-weight:700; letter-spacing:0.5px;'>CronusAGI Financial Intelligence Engine</span>
</div>
<span style='color:#1A8CFF; font-size:1.1rem;'>Institutional Market Analysis & Predictive Signals</span>
""", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

market_service = MarketDataService()
sentiment_service = SentimentAnalysisService()

with st.sidebar:
    st.header("Input Parameters")
    asset_type = st.selectbox(
        "Asset Type",
        ["Stock", "Cryptocurrency"]
    )
    
    if asset_type == "Stock":
        symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)")
    else:
        symbol = st.text_input("Enter Cryptocurrency Symbol (e.g., BTC)")

    time_ranges = {
        "1D": 1,
        "5D": 5,
        "1M": 30,
        "6M": 182,
        "YTD": "ytd",
        "1Y": 365,
        "5Y": 1825,
        "Max": "max"
    }
    selected_range = st.radio("Time Range", list(time_ranges.keys()), index=2, horizontal=True)

if symbol:
    from datetime import datetime, timedelta
    end_date = datetime.now()
    if time_ranges[selected_range] == "ytd":
        start_date = datetime(end_date.year, 1, 1)
    elif time_ranges[selected_range] == "max":
        start_date = datetime(1990, 1, 1)
    else:
        start_date = end_date - timedelta(days=time_ranges[selected_range])

    with st.spinner("Fetching market data and signals..."):
        if asset_type == "Stock":
            data = market_service.get_stock_data(symbol, start_date, end_date)
        else:
            data = market_service.get_crypto_data(symbol, start_date, end_date)
        data = market_service.calculate_technical_indicators(data)
        news = market_service.get_news(symbol)
        sentiment = sentiment_service.analyze_news_sentiment(news)

    if data is not None and not data.empty:
        col1, col2, col3 = st.columns([2,2,1])
        with col1:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.subheader("Price & Bands")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price',
                increasing_line_color='#1A8CFF', decreasing_line_color='#FF0033'))
            fig.add_trace(go.Scatter(x=data.index, y=data['BB_Upper'], mode='lines', name='BB Upper', line=dict(color='#1A8CFF', width=1, dash='dot')))
            fig.add_trace(go.Scatter(x=data.index, y=data['BB_Middle'], mode='lines', name='BB Middle', line=dict(color='#888', width=1)))
            fig.add_trace(go.Scatter(x=data.index, y=data['BB_Lower'], mode='lines', name='BB Lower', line=dict(color='#1A8CFF', width=1, dash='dot')))
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                plot_bgcolor='#181C20', paper_bgcolor='#181C20', font_color='#E0E6ED',
                height=370, margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.subheader("Technical Indicators")
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='#1A8CFF')))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#FF0033")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00FF00")
            fig_rsi.update_layout(
                title="RSI (14)", plot_bgcolor='#181C20', paper_bgcolor='#181C20', font_color='#E0E6ED', height=150, margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_rsi, use_container_width=True)
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='#1A8CFF')))
            fig_macd.add_trace(go.Scatter(x=data.index, y=data['Signal_Line'], mode='lines', name='Signal', line=dict(color='#FF0033')))
            fig_macd.add_trace(go.Bar(x=data.index, y=data['MACD_Histogram'], name='Histogram', marker_color='#888'))
            fig_macd.update_layout(
                title="MACD", plot_bgcolor='#181C20', paper_bgcolor='#181C20', font_color='#E0E6ED', height=150, margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_macd, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.subheader("Signals & Metrics")
            current_price = data['Close'].iloc[-1]
            price_change = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            rsi_value = data['RSI'].iloc[-1]
            rsi_signal = "Overbought" if rsi_value > 70 else "Oversold" if rsi_value < 30 else "Neutral"
            macd_value = data['MACD'].iloc[-1]
            signal_value = data['Signal_Line'].iloc[-1]
            macd_signal = "Bullish" if macd_value > signal_value else "Bearish"
            momentum_value = data['Momentum'].iloc[-1]
            momentum_signal = "Bullish" if momentum_value > 0 else "Bearish"
            icon_map = {"Bullish": "📈", "Bearish": "📉", "Overbought": "🔥", "Oversold": "🧊", "Neutral": "➖"}
            st.metric(
                label="Current Price",
                value=f"${current_price:.2f}",
                delta=f"{price_change:.2f}%"
            )
            st.markdown(f"RSI: <span class='metric-badge {rsi_signal.lower()}' title='Relative Strength Index'>{icon_map.get(rsi_signal, '➖')} {rsi_value:.2f} ({rsi_signal})</span>", unsafe_allow_html=True)
            st.markdown(f"MACD: <span class='metric-badge {macd_signal.lower()}' title='MACD Signal'>{icon_map.get(macd_signal, '➖')} {macd_value:.2f} ({macd_signal})</span>", unsafe_allow_html=True)
            st.markdown(f"Momentum: <span class='metric-badge {momentum_signal.lower()}' title='10-day Momentum'>{icon_map.get(momentum_signal, '➖')} {momentum_value:.2f}% ({momentum_signal})</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.subheader("Technical Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### Moving Averages")
            st.write(f"SMA20: ${data['SMA20'].iloc[-1]:.2f}")
            st.write(f"SMA50: ${data['SMA50'].iloc[-1]:.2f}")
            ma_signal = "Bullish" if data['SMA20'].iloc[-1] > data['SMA50'].iloc[-1] else "Bearish"
            st.markdown(f"Signal: <span class='metric-badge {ma_signal.lower()}'>{ma_signal}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown("### Bollinger Bands")
            st.write(f"Upper Band: ${data['BB_Upper'].iloc[-1]:.2f}")
            st.write(f"Middle Band: ${data['BB_Middle'].iloc[-1]:.2f}")
            st.write(f"Lower Band: ${data['BB_Lower'].iloc[-1]:.2f}")
            bb_signal = "Overbought" if current_price > data['BB_Upper'].iloc[-1] else "Oversold" if current_price < data['BB_Lower'].iloc[-1] else "Neutral"
            st.markdown(f"Signal: <span class='metric-badge {bb_signal.lower()}'>{bb_signal}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown("### Volume Analysis")
            avg_volume = data['Volume'].mean()
            current_volume = data['Volume'].iloc[-1]
            volume_change = ((current_volume - avg_volume) / avg_volume) * 100
            st.write(f"Current Volume: {current_volume:,.0f}")
            st.write(f"Average Volume: {avg_volume:,.0f}")
            st.write(f"Volume Change: {volume_change:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.subheader("News and Sentiment Analysis")
        if news:
            for n in news:
                try:
                    if isinstance(n, dict):
                        st.markdown(f"""
                        <div class="news-item">
                            <div class="news-title">{n.get('title', 'No title available')}</div>
                            <p>{n.get('text', '')[:200]}...</p>
                            <a class="news-link" href="{n.get('url', '#')}" target="_blank">Read more</a>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error displaying news item: {str(e)}")
        else:
            st.markdown("<div style='text-align:center; color:#888;'><span style='font-size:2.5rem;'>📰</span><br>News data requires a paid API subscription.<br>Please upgrade your API key to view news.</div>", unsafe_allow_html=True)
        if sentiment and sentiment.get('overall_sentiment'):
            icon = sentiment_service.get_sentiment_icon(sentiment['overall_sentiment'])
            color = sentiment_service.get_sentiment_color(sentiment['overall_sentiment'])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Overall Sentiment: {icon} {sentiment['overall_sentiment'].capitalize()}</h3>
                <p>Sentiment Score: {sentiment.get('sentiment_score', 0):.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Sentiment analysis requires news data. Please upgrade your API key to view sentiment analysis.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("No data available for the selected symbol. Please check the symbol and try again.")
else:
    st.info("Please enter a symbol to begin analysis")
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#888;'>CronusAGI Financial Intelligence Engine | MVP Version</div>", unsafe_allow_html=True) 