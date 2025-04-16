import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Function to fetch S&P 500 stock symbols from Wikipedia
def get_sp500_stocks():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    
    # The first table contains the list of S&P 500 companies
    sp500_table = tables[0]
    
    # Extract stock symbols
    sp500_symbols = sp500_table['Symbol'].tolist()

    return sp500_symbols  # Return list of S&P 500 symbols

# Function to fetch options data for a given stock
def get_options_data(stock_symbol):
    stock = yf.Ticker(stock_symbol)
    options_dates = stock.options  # Get available expiration dates
    selected_date = st.selectbox("Select Expiration Date", options_dates)
    
    # Get the options chain for the selected expiration date
    options_chain = stock.option_chain(selected_date)
    
    # Extract calls and puts data
    calls = options_chain.calls
    puts = options_chain.puts

    # Return the call and put data for further processing
    return calls, puts, selected_date

# Function to create visualizations for the options data
def plot_options_data(calls, puts):
    # Plotting open interest, implied volatility, and strike prices
    fig = go.Figure()

    # Add Call options plot
    fig.add_trace(go.Scatter(
        x=calls['strike'], 
        y=calls['openInterest'], 
        mode='lines+markers',
        name="Call Open Interest",
        line=dict(dash='dot'),
        marker=dict(symbol='circle', color='blue', size=8)
    ))

    # Add Put options plot
    fig.add_trace(go.Scatter(
        x=puts['strike'], 
        y=puts['openInterest'], 
        mode='lines+markers',
        name="Put Open Interest",
        line=dict(dash='dot'),
        marker=dict(symbol='circle', color='red', size=8)
    ))

    # Update layout and labels
    fig.update_layout(
        title="Options Open Interest vs Strike Prices",
        xaxis_title="Strike Price",
        yaxis_title="Open Interest",
        template="plotly_dark",
        legend=dict(x=0.8, y=0.9)
    )

    return fig

# Function to display options data and visualization
def stock_options_page():
    st.header("📈 Stock Options Chain")
    st.markdown("""
    **What is an Options Chain?**  
    An options chain lists all available options contracts for a specific stock, including both call and put options with strike prices and expiration dates.  
    
    **How to Use This Page:**  
    1️⃣ Select a stock symbol from the dropdown.  
    2️⃣ Select the expiration date.  
    3️⃣ View the visualized data showing open interest for call and put options.
    """)

    # Fetch the list of S&P 500 stock symbols
    sp500_symbols = get_sp500_stocks()

    # Dropdown list for stock selection
    stock_symbol = st.selectbox("Select Stock Symbol:", sp500_symbols)  # Dropdown of S&P 500 stocks
    
    if stock_symbol:
        # Get options data for the selected stock symbol
        calls, puts, selected_date = get_options_data(stock_symbol)

        # Display selected expiration date
        st.write(f"Showing options data for {stock_symbol} with expiration date: {selected_date}")

        # Display options chain tables
        st.write("### Call Options")
        st.dataframe(calls)
        st.write("### Put Options")
        st.dataframe(puts)

        # Plot the options data (Open Interest vs. Strike Price)
        st.write("### Options Open Interest Visualization")
        fig = plot_options_data(calls, puts)
        st.plotly_chart(fig)
