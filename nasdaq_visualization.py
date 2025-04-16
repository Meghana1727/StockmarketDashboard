import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

# Function to fetch Nasdaq 100 tickers from Wikipedia
def get_nasdaq_100_tickers():
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    tables = pd.read_html(url)
    nasdaq_table = tables[4]  # 4th table contains the Nasdaq 100 companies

    # Extracting tickers
    tickers = nasdaq_table['Ticker'].tolist()
    return tickers

# Function to fetch stock sector information dynamically
def get_stock_sector(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.info.get("sector", "Unknown")  # Get sector
    except Exception as e:
        return "Unknown"

# Function to categorize Nasdaq stocks by sector
def categorize_stocks_by_sector():
    tickers = get_nasdaq_100_tickers()
    sector_dict = {}

    # Loop through all tickers and categorize by sector
    for ticker in tickers:
        sector = get_stock_sector(ticker)
        if sector not in sector_dict:
            sector_dict[sector] = []
        sector_dict[sector].append(ticker)

    return sector_dict

# Function to fetch stock data
def get_stock_data(symbol, period):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)  # Fetch historical data based on user-selected period
    return df

# Function to plot candlestick chart
def plot_candlestick(df, symbol):
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Candlesticks"
        )
    ])
    fig.update_layout(title=f"{symbol} Candlestick Chart", xaxis_title="Date", yaxis_title="Price")
    return fig

# Streamlit UI for Nasdaq Visualization
def nasdaq_visualization():
    st.header("📊 Nasdaq Stock Candlestick Charts")

    # Get categorized stocks by sector
    sector_stocks = categorize_stocks_by_sector()

    # Dropdown for sector selection
    sector = st.selectbox("Select Sector:", list(sector_stocks.keys()))
    
    # Dropdown for stock selection within the selected sector
    stock_symbol = st.selectbox("Select Stock:", sector_stocks[sector])

    # Dropdown for period selection
    period = st.selectbox("Select Time Period:", ["1mo", "3mo", "6mo", "1y", "10y"])

    # Fetch stock data and plot chart
    if stock_symbol:
        df = get_stock_data(stock_symbol, period)
        if df.empty:
            st.error("No data available for this stock.")
        else:
            fig = plot_candlestick(df, stock_symbol)
            st.plotly_chart(fig)



