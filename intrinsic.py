import streamlit as st
import pandas as pd
import yfinance as yf

# Set page configuration (must be first command)


# Function to fetch S&P 500 stock symbols from Wikipedia
def get_sp500_stocks():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    
    # Extract stock symbols and names
    sp500_table = tables[0]
    sp500_symbols = sp500_table['Symbol'].tolist()
    sp500_names = sp500_table['Security'].tolist()

    return list(zip(sp500_symbols, sp500_names))  # Return a list of (symbol, name) tuples

# Function to calculate intrinsic value
def calculate_intrinsic_value(stock_symbol, discount_rate=0.1, growth_rate=0.05, years=5):
    stock = yf.Ticker(stock_symbol)
    earnings_per_share = stock.info.get("forwardEps", None)

    if earnings_per_share is None:
        return "EPS data not available"

    intrinsic_value = 0
    for i in range(1, years + 1):
        intrinsic_value += earnings_per_share * (1 + growth_rate) ** i / (1 + discount_rate) ** i

    return round(intrinsic_value, 2)

# Intrinsic Value Page
def intrinsic_value_page():
    st.header("📊 Intrinsic Value Calculator (DCF Method)")
    st.markdown("""
    
    **What is Intrinsic Value?**  
    Intrinsic value represents the **true worth** of a stock based on future cash flows, independent of market price.  
    It is often calculated using the **Discounted Cash Flow (DCF) model**.
    
    **Why is Intrinsic Value Important?**  
    ✅ Helps investors determine if a stock is **overvalued** or **undervalued**.  
    ✅ Essential for **long-term** investment decisions.  
    ✅ Used by fundamental analysts to **avoid market noise**.  

    **How to Use This Page:**  
    1️⃣ Select a stock from the dropdown.  
    2️⃣ Adjust the discount rate and growth rate.  
    3️⃣ Get the intrinsic value and compare it with the market price.  
    """, unsafe_allow_html=True)

    # Fetch S&P 500 stocks
    sp500_list = get_sp500_stocks()
    
    # Create a dictionary for stock symbol -> company name mapping
    stock_dict = {symbol: name for symbol, name in sp500_list}

    # Dropdown for stock selection (display name but use symbol)
    stock_symbol = st.selectbox("Select Stock Symbol:", options=stock_dict.keys(), format_func=lambda x: f"{x} - {stock_dict[x]}")

    # Discount rate and growth rate sliders
    discount_rate = st.slider("Discount Rate (%)", min_value=1, max_value=15, value=10, step=1) / 100
    growth_rate = st.slider("Growth Rate (%)", min_value=1, max_value=10, value=5, step=1) / 100

    # Calculate and display intrinsic value
    if stock_symbol:
        stock_name = stock_dict[stock_symbol]
        result = calculate_intrinsic_value(stock_symbol, discount_rate, growth_rate)
        
        st.subheader(f"📌 Stock: {stock_symbol} - {stock_name}")
        st.write(f"**Intrinsic Value:** ${result}")

# Call the function to display the page
intrinsic_value_page()
