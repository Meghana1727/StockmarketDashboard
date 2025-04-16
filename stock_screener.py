import streamlit as st
import pandas as pd
import yfinance as yf


# Function to fetch S&P 500 stock symbols from Wikipedia
def get_sp500_stocks():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    
    # Extract stock symbols and names
    sp500_table = tables[0]
    sp500_symbols = sp500_table['Symbol'].tolist()
    sp500_names = sp500_table['Security'].tolist()

    return list(zip(sp500_symbols, sp500_names))  # Return a list of (symbol, name) tuples

# Stock Screener Page
def stock_screener_page():
    
    st.markdown("""
    ## 📊 Stock Screener  
    **What is a Stock Screener?**  
    A stock screener helps filter stocks based on key financial metrics. This tool helps **investors and traders** find the best opportunities.  
    
    **Filters Available:**  
    ✅ **P/E Ratio** – Measures how expensive a stock is compared to earnings.  
    ✅ **EPS Growth** – Identifies companies with **rising profits**.  
    ✅ **Dividend Yield** – Finds stocks with attractive **dividends**.  
    ✅ **Volume Trends** – Helps spot stocks with **high trading activity**.  
    
    **How to Use This Page:**  
    1️⃣ Select a stock from the dropdown.  
    2️⃣ View key financial metrics.  
    3️⃣ Analyze the stock for investment.  
    """, unsafe_allow_html=True)

    # Fetch S&P 500 stocks
    sp500_list = get_sp500_stocks()
    
    # Create a dictionary for stock symbol -> company name mapping
    stock_dict = {symbol: name for symbol, name in sp500_list}

    # Dropdown for stock selection (display name but use symbol)
    stock_symbol = st.selectbox("Select Stock Symbol:", options=stock_dict.keys(), format_func=lambda x: f"{x} - {stock_dict[x]}", key="stock_selectbox")

    # Fetch stock data
    if stock_symbol:
        stock_name = stock_dict[stock_symbol]
        stock = yf.Ticker(stock_symbol)
        info = stock.info

        if not info:
            st.error("Stock data not found!")
            return

        # Extract financial metrics
        pe_ratio = info.get("trailingPE", "N/A")
        eps_growth = info.get("earningsQuarterlyGrowth", "N/A")
        dividend_yield = info.get("dividendYield", "N/A")
        avg_volume = info.get("averageVolume", "N/A")

        # Display stock name
        st.subheader(f"📌 Stock: {stock_symbol} - {stock_name}")

        # Display metrics
        st.write(f"**P/E Ratio:** {pe_ratio}")
        st.write(f"**EPS Growth (Quarterly):** {eps_growth}")
        st.write(f"**Dividend Yield:** {dividend_yield}")
        st.write(f"**Avg. Trading Volume:** {avg_volume}")

        # Highlight if stock is undervalued
        if pe_ratio != "N/A" and isinstance(pe_ratio, (int, float)) and pe_ratio < 15:
            st.success("✅ Stock is undervalued based on P/E ratio!")

# Run the stock screener 