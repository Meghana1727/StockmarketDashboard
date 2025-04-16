import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table", {"id": "constituents"})
    df = pd.read_html(StringIO(str(table)))[0]  # Fixing the FutureWarning
    return df[['Symbol', 'GICS Sector']]

def fetch_financials(ticker):
    try:
        stock = yf.Ticker(ticker)
        income_statement = stock.income_stmt
        if income_statement is None or income_statement.empty:
            return None, None
        latest_quarter, prev_quarter = income_statement.columns[:2]
        latest_eps = income_statement.at["Diluted EPS", latest_quarter] if "Diluted EPS" in income_statement.index else 0
        prev_eps = income_statement.at["Diluted EPS", prev_quarter] if "Diluted EPS" in income_statement.index else 0
        eps_growth = ((latest_eps - prev_eps) / (prev_eps if prev_eps != 0 else 1)) * 100
        return latest_eps, eps_growth
    except Exception:
        return None, None

def compare_all_stocks():
    sp500_data = get_sp500_tickers()
    results = []
    for index, row in sp500_data.iterrows():
        symbol, sector = row['Symbol'], row['GICS Sector']
        latest_eps, eps_growth = fetch_financials(symbol)
        if latest_eps is not None:
            results.append({
                "Symbol": symbol,
                "Sector": sector,
                "Latest EPS": latest_eps,
                "EPS Growth (%)": round(eps_growth, 2)
            })
    return pd.DataFrame(results)

def trend_prediction():
    st.subheader("📊 Quarterly EPS Trend Prediction")

    with st.spinner("Analyzing S&P 500 earnings data..."):
        sp500_df = compare_all_stocks()

    if not sp500_df.empty:
        st.success("Data loaded successfully!")
        col1, col2 = st.columns(2)

        with col1:
            st.write("### 🚀 Top 10 EPS Gainers")
            st.dataframe(sp500_df.sort_values(by="EPS Growth (%)", ascending=False).head(10))

        with col2:
            st.write("### 📉 Top 10 EPS Losers")
            st.dataframe(sp500_df.sort_values(by="EPS Growth (%)", ascending=True).head(10))

        st.download_button(
            label="📥 Download Full EPS Report",
            data=sp500_df.to_csv(index=False),
            file_name="sp500_eps_growth.csv",
            mime="text/csv"
        )
    else:
        st.warning("No earnings data found. Please try again later.")
