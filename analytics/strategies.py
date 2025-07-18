from analytics.indicators import sma, ema, rsi, vwap, macd
def sma_crossover(df, window1=50, window2=200, risk_pct=0.01, reward_pct = 0.02):
    ''' Will read a dataframe containing historical data and generate two distinct SMA calculations based on a tickers 
        price action, specifically the closing price of a ticker. When the SMA with a smaller window is greater than 
        the SMA with the larger window the market is believed to be in an uptrend, and when the opposite happens the market is believed to be in a downtrend.'''
    # Add two distinct SMA indicators 
    df[f"sma{window1}"] = sma(df, period=window1)
    df[f"sma{window2}"] = sma(df, period=window2)
    in_position = False
    entry_price = stop_loss = take_profit = None
    df["signal"] = 0

    for i in range(1, len(df)):
        fast_prev = df.loc[i - 1, f"sma{window1}"]
        slow_prev = df.loc[i - 1, f"sma{window2}"]
        fast_curr = df.loc[i, f"sma{window1}"]
        slow_curr = df.loc[i, f"sma{window2}"]

        if not in_position:
            if fast_prev < slow_prev and fast_curr > slow_curr:
                df.at[i, "signal"] = 1
                entry_price = df.loc[i, "close"]
                stop_loss = entry_price * (1 - risk_pct)
                take_profit = entry_price * (1 + reward_pct)
                in_position = True
        else:
            current_price = df.loc[i, "close"]
            if stop_loss is None or take_profit is None:
                print("⚠️ No valid entry price. Skipping.")
                continue

            if (current_price <= stop_loss) or (current_price >= take_profit) or (fast_prev > slow_prev and fast_curr < slow_curr):
                df.at[i, "signal"] = -1
                entry_price = stop_loss = take_profit = None
                in_position = False

    return df
