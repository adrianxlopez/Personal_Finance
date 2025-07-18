from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volume import VolumeWeightedAveragePrice
from ta.trend import MACD
import pandas as pd

def sma(df, period=20, price_col="close"):
    '''Simple Moving Average'''
    sma = SMAIndicator(close=df[price_col], window=period)
    return sma.sma_indicator()


def ema(df, period=20, price_col="close"):
    '''Exponential Moving Average'''
    ema = EMAIndicator(close=df[price_col], window=period)
    return ema.ema_indicator()

def rsi(df, period=14, price_col="close"):
    '''Relative Strength Indicator'''
    rsi = RSIIndicator(close=df[price_col], window=period)
    return rsi.rsi()

def vwap(df, period=14):
    # Volume Weighted Average Price (VWAP)
    VWAPIndicator = VolumeWeightedAveragePrice(
        high=df['high'], 
        low=df['low'], 
        close=df['close'], 
        volume=df['volume'], 
        window=period
    )
    return VWAPIndicator.vwap

def macd(df, price_col="close"):
    """MACD and Signal Line."""
    macd_obj = MACD(close=df[price_col])
    return pd.DataFrame({
        "macd": macd_obj.macd(),
        "macd_signal": macd_obj.macd_signal()
    })
