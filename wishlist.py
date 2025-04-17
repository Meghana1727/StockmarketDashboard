import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from news import get_stock_news
import time

# Import from db_config.py
from db_config import get_connection_status, client, db, connected

# ✅ Initialize wishlist collection based on connection status
def initialize_collection():
    if connected and db:
        return db["wishlist"]
    return None

# Global variable for in-memory fallback
in_memory_wishlists = {}

# ✅ Fetch user wishlist from MongoDB or fallback storage
def get_wishlist(username):
    if not username:
        return []
    
    try:
        # Try MongoDB first if connected
        if connected:
            wishlist_collection = initialize_collection()
            user_wishlist = wishlist_collection.find_one({"username": username})
            return user_wishlist["stocks"] if user_wishlist else []
        else:
            # Use in-memory fallback
            return in_memory_wishlists.get(username, [])
    except Exception as e:
        print(f"Error fetching wishlist: {e}")
        return []

# ✅ Update wishlist in MongoDB or fallback storage
def update_wishlist(username, stocks):
    if not username:
        return False
    
    try:
        # Try MongoDB first if connected
        if connected:
            wishlist_collection = initialize_collection()
            wishlist_collection.update_one(
                {"username": username},
                {"$set": {"stocks": stocks}},
                upsert=True
            )
        else:
            # Use in-memory fallback
            in_memory_wishlists[username] = stocks
        return True
    except Exception as e:
        print(f"Error updating wishlist: {e}")
        # Fall back to in-memory if MongoDB fails
        in_memory_wishlists[username] = stocks
        return True

# ✅ Fetch stock data for wishlist items
def get_wishlist_stock_data(wishlist):
    stock_data = {}
    for stock in wishlist:
        try:
            df = yf.Ticker(stock).history(period="1d", interval="1h")  # Today's hourly data
            if not df.empty:
                df.reset_index(inplace=True)
                df["Datetime"] = pd.to_datetime(df["Datetime"])
                stock_data[stock] = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]
        except Exception as e:
            print(f"Error fetching data for {stock}: {e}")
    return stock_data

# ✅ Fetch news for wishlist stocks
def get_wishlist_news(wishlist):
    news_data = {}
    for stock in wishlist:
        try:
            news_articles = get_stock_news(stock)
            if news_articles:
                news_data[stock] = news_articles[:3]
        except Exception as e:
            print(f"Error fetching news for {stock}: {e}")
    return news_data

# ✅ Function to render wishlist page
def wishlist_page():
    st.title("🌟 Your Wishlist")
    
    # Check if user is logged in
    if "username" not in st.session_state or not st.session_state.username:
        st.warning("Please log in to view your wishlist")
        return
    
    # Show storage mode
    if not connected:
        st.info("⚠️ Using temporary storage mode. Your wishlist will not persist between sessions.")
    
    username = st.session_state.username
    wishlist = get_wishlist(username)
    
    # Add stock to wishlist section
    with st.expander("➕ Add Stock to Wishlist"):
        new_stock = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL):", key="new_stock").upper()
        if st.button("Add Stock", key="add_stock"):
            if new_stock:
                # Validate stock symbol
                try:
                    tick = yf.Ticker(new_stock)
                    info = tick.info
                    if "regularMarketPrice" in info and info["regularMarketPrice"] is not None:
                        if new_stock not in wishlist:
                            wishlist.append(new_stock)
                            update_wishlist(username, wishlist)
                            st.success(f"{new_stock} added to your wishlist!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning(f"{new_stock} is already in your wishlist")
                    else:
                        st.error(f"Invalid stock symbol: {new_stock}")
                except Exception as e:
                    st.error(f"Error validating stock symbol: {e}")
            else:
                st.warning("Please enter a stock symbol")
    
    if wishlist:
        # Display stocks in wishlist
        st.subheader("📋 Your tracked stocks")
        stock_list = ", ".join(wishlist)
        st.write(f"Currently tracking: {stock_list}")
        
        # Get stock data and display charts
        with st.spinner("Loading stock data..."):
            stock_data = get_wishlist_stock_data(wishlist)
        
        for stock, df in stock_data.items():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.write(f"### 📈 {stock} - Today's Trend")
                
                if not df.empty:
                    # Calculate current price and daily change
                    current_price = df["Close"].iloc[-1]
                    price_change = df["Close"].iloc[-1] - df["Close"].iloc[0]
                    percent_change = (price_change / df["Close"].iloc[0]) * 100
                    
                    # Display price info
                    st.metric(
                        label=f"{stock} Price", 
                        value=f"${current_price:.2f}", 
                        delta=f"{price_change:.2f} ({percent_change:.2f}%)"
                    )
                    
                    # Create and display the chart
                    fig = px.line(
                        df, 
                        x="Datetime", 
                        y="Close",
                        title=f"{stock} - Stock Trend",
                        labels={"Close": "Price ($)", "Datetime": "Time"}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data available for {stock}")
            
            with col2:
                # Remove button in the side column
                if st.button(f"❌ Remove", key=f"remove_{stock}"):
                    wishlist.remove(stock)
                    update_wishlist(username, wishlist)
                    st.success(f"{stock} removed from wishlist!")
                    time.sleep(1)
                    st.rerun()
        
        # Display news for stocks in wishlist
        st.subheader("📰 Latest News")
        with st.spinner("Loading news..."):
            news_data = get_wishlist_news(wishlist)
        
        if news_data:
            for stock, articles in news_data.items():
                st.write(f"### 📰 {stock} News")
                if articles:
                    for i, news in enumerate(articles):
                        with st.container():
                            st.write(f"**{news['headline']}**")
                            st.write(f"Source: {news.get('source', 'Unknown')} | [Read More]({news['url']})")
                            if i < len(articles) - 1:
                                st.divider()
                else:
                    st.info(f"No recent news found for {stock}")
        else:
            st.info("No news data available for your wishlist stocks")
    else:
        st.info("Your wishlist is empty. Add stocks to track their latest updates!")

# ✅ Notification System for Stock Alerts
def stock_notifications():
    if "username" not in st.session_state or not st.session_state.username:
        return
        
    username = st.session_state.username
    wishlist = get_wishlist(username)
    
    if wishlist:
        stock_data = get_wishlist_stock_data(wishlist)
        for stock, df in stock_data.items():
            if not df.empty and len(df) > 1:
                if df["Close"].iloc[-1] > df["Close"].iloc[-2]:
                    percent_change = ((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2]) * 100
                    if percent_change > 1.0:  # Only notify for significant changes (>1%)
                        st.toast(f"🚀 {stock} up {percent_change:.2f}%! Price: ${df['Close'].iloc[-1]:.2f}")
                elif df["Close"].iloc[-1] < df["Close"].iloc[-2]:
                    percent_change = ((df["Close"].iloc[-2] - df["Close"].iloc[-1]) / df["Close"].iloc[-2]) * 100
                    if percent_change > 1.0:  # Only notify for significant changes (>1%)
                        st.toast(f"📉 {stock} down {percent_change:.2f}%! Price: ${df['Close'].iloc[-1]:.2f}")
