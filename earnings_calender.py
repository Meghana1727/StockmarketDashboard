import streamlit as st
import pandas as pd
import yfinance as yf

# Function to fetch S&P 500 stock symbols from Wikipedia
def get_sp500_stocks():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    
    # The first table contains the list of S&P 500 companies
    sp500_table = tables[0]
    
    # Extract stock symbols and names
    sp500_symbols = sp500_table['Symbol'].tolist()
    sp500_names = sp500_table['Security'].tolist()  # Company names

    return list(zip(sp500_symbols, sp500_names))  # Return a list of tuples (symbol, name)

# Function to get earnings report for a selected stock
def get_earnings_report(stock_symbol, stock_name):
    stock = yf.Ticker(stock_symbol)
    earnings = stock.calendar

    if not earnings:
        return None  # Return None if no data available

    # Convert dictionary to DataFrame
    earnings_df = pd.DataFrame(earnings.items(), columns=["Event", "Date"])
    earnings_df["Date"] = earnings_df["Date"].astype(str)

    # Insert stock name in the first row
    stock_info_row = pd.DataFrame([["Stock Name", stock_name]], columns=["Event", "Date"])
    earnings_df = pd.concat([stock_info_row, earnings_df], ignore_index=True)

    return earnings_df

# Streamlit UI - Earnings Calendar Page
def earnings_calendar_page():
    st.header("📅 Earnings Calendar")
    
    st.markdown("""
      
    **What is an Earnings Calendar?**  
    An earnings calendar provides a schedule of when publicly traded companies **release their quarterly earnings reports**.  
    
    **Why is This Important?**  
    ✅ Earnings reports affect **stock prices** significantly.  
    ✅ Helps traders **time their investments**.  
    ✅ Compares company performance **quarter over quarter**.  
    
    **How to Use This Page:**  
    1️⃣ Select a stock symbol from the dropdown.  
    2️⃣ View upcoming earnings dates and analyst expectations.  
    3️⃣ Compare past earnings to **predict future trends**.  
    """, unsafe_allow_html=True)

    # Fetch S&P 500 stock symbols and names
    sp500_list = get_sp500_stocks()

    # Create a dictionary to map symbols to names
    stock_dict = {symbol: name for symbol, name in sp500_list}

    # Dropdown list for stock selection (display name but use symbol)
    stock_symbol = st.selectbox(
        "Select Stock Symbol:", 
        options=stock_dict.keys(), 
        format_func=lambda x: f"{x} - {stock_dict[x]}",
        key="unique_earnings_calendar_selectbox"  # Unique key added
    )
    
    # Fetch earnings data for the selected stock
    if stock_symbol:
        stock_name = stock_dict[stock_symbol]  # Get the company name
        earnings = get_earnings_report(stock_symbol, stock_name)

        if earnings is None:
            st.error("No earnings data available for this stock.")
        else:
            st.dataframe(earnings, width=800, height=400)


