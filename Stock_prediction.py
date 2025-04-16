import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import warnings
import os

from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

warnings.filterwarnings("ignore")


def download_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Download historical stock data using yfinance
    """
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            raise ValueError("No data found for the specified ticker or date range.")
        return df
    except Exception as e:
        raise RuntimeError(f"Error fetching data: {e}")


def predict_with_arima(df: pd.DataFrame, steps: int = 30) -> pd.Series:
    """
    Predict future stock prices using ARIMA
    """
    try:
        model = ARIMA(df['Close'], order=(5, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        return forecast
    except Exception as e:
        raise RuntimeError(f"ARIMA prediction failed: {e}")


def predict_with_lstm(df: pd.DataFrame, steps: int = 30) -> pd.Series:
    """
    Predict future stock prices using LSTM
    """
    try:
        data = df['Close'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        X_train = []
        y_train = []
        for i in range(60, len(scaled_data)):
            X_train.append(scaled_data[i-60:i, 0])
            y_train.append(scaled_data[i, 0])

        X_train, y_train = np.array(X_train), np.array(y_train)
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
        model.add(LSTM(50))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')

        model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)

        last_60_days = scaled_data[-60:]
        future_preds = []
        for _ in range(steps):
            X_test = np.reshape(last_60_days, (1, 60, 1))
            pred = model.predict(X_test)[0][0]
            future_preds.append(pred)
            last_60_days = np.append(last_60_days[1:], [[pred]], axis=0)

        predicted_prices = scaler.inverse_transform(np.array(future_preds).reshape(-1, 1)).flatten()
        return pd.Series(predicted_prices)
    except Exception as e:
        raise RuntimeError(f"LSTM prediction failed: {e}")


def plot_predictions(original_df: pd.DataFrame, predicted_series: pd.Series, model_name: str):
    """
    Plot original and predicted data using matplotlib and return the figure
    """
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(original_df['Close'], label='Historical Prices')
        future_index = pd.date_range(start=original_df.index[-1] + pd.Timedelta(days=1), periods=len(predicted_series))
        ax.plot(future_index, predicted_series, label=f'{model_name} Forecast', linestyle='--')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title(f'{model_name} Stock Price Prediction')
        ax.legend()
        ax.grid(True)
        return fig
    except Exception as e:
        raise RuntimeError(f"Error plotting predictions: {e}")