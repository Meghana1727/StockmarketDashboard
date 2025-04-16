# sector.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from constant import SECTORS

def fetch_sector_performance_details(sector_stocks):
    """
    Fetch detailed performance data for stocks in a sector.
    
    Returns a DataFrame with more comprehensive stock information.
    """
    performance_data = []
    
    for stock in sector_stocks:
        try:
            ticker = yf.Ticker(stock)
            
            # Fetch historical data
            data = ticker.history(period="1mo")
            if data.empty:
                continue
            
            # Calculate performance
            performance = ((data['Close'][-1] - data['Close'][0]) / data['Close'][0]) * 100
            
            # Fetch additional company info
            info = ticker.info
            market_cap = info.get('marketCap', 0)
            
            performance_data.append({
                'Stock': stock,
                'Performance': performance,
                'Market Cap': market_cap,
                'Company Name': info.get('longName', stock)
            })
        except Exception as e:
            st.warning(f"Could not fetch data for {stock}: {e}")
    
    return pd.DataFrame(performance_data)

def sector_heatmap(selected_sector):
    """
    Create an interactive treemap visualization for sector performance.
    """
    st.header(f"{selected_sector} Sector Performance Treemap")
    
    # Get stocks for the selected sector
    sector_stocks = SECTORS.get(selected_sector, [])
    
    # Fetch performance data
    df = fetch_sector_performance_details(sector_stocks)
    
    if df.empty:
        st.error(f"No performance data available for {selected_sector} sector.")
        return
    
    # Create interactive treemap
    fig = px.treemap(
        df, 
        path=['Company Name'],  # Use company names for labels
        values='Market Cap',    # Size of rectangles based on market cap
        color='Performance',    # Color intensity based on performance
        color_continuous_scale='RdYlGn',  # Red (negative) to Green (positive) color scale
        custom_data=['Stock', 'Performance', 'Market Cap']  # Additional info for hover
    )
    
    # Customize hover template
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>' +
                      'Stock: %{customdata[0]}<br>' +
                      'Performance: %{customdata[1]:.2f}%<br>' +
                      'Market Cap: $%{customdata[2]:,.0f}<extra></extra>'
    )
    
    # Update layout
    fig.update_layout(
        title=f'{selected_sector} Sector Performance Treemap',
        width=800,
        height=600
    )
    
    # Display the treemap
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance Table
    st.subheader("Performance Details")
    df['Performance'] = df['Performance'].apply(lambda x: f"{x:.2f}%")
    df['Market Cap'] = df['Market Cap'].apply(lambda x: f"${x:,.0f}")
    df = df[['Stock', 'Company Name', 'Performance', 'Market Cap']]
    st.dataframe(df, use_container_width=True)