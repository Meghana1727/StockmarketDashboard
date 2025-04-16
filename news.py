import streamlit as st
import requests

# 🔹 Replace with your Finnhub API Key
FINNHUB_API_KEY = "cv74ra9r01qsq464svq0cv74ra9r01qsq464svqg"

# 🔹 Function to Fetch Latest Stock News
def get_stock_news(symbol):
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2024-01-01&to=2025-12-31&token={FINNHUB_API_KEY}"
    
    try:
        response = requests.get(url)
        news_data = response.json()
        
        if isinstance(news_data, list) and len(news_data) > 0:
            return news_data[:30]  # Get latest 30 news articles
        else:
            return []
    except Exception as e:
        return []

