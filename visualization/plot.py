import matplotlib.pyplot as plt

def plot_price_with_indicators(df, ticker):

    """Plot price along with added indicators like MACD, SMA, etc."""
    fig, axs = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Price and SMA/EMA
    axs[0].plot(df['timestamp'], df['close'], label='Close', color='black')
    if 'sma' in df:
        axs[0].plot(df['timestamp'], df['sma'], label='SMA', color='blue')
    if 'ema' in df:
        axs[0].plot(df['timestamp'], df['ema'], label='EMA', color='orange')
    axs[0].set_title(f"{ticker} Price with SMA/EMA")
    axs[0].legend()
    axs[0].grid(True)

    # RSI
    if 'rsi' in df:
        axs[1].plot(df['timestamp'], df['rsi'], label='RSI', color='purple')
        axs[1].axhline(70, color='red', linestyle='--')
        axs[1].axhline(30, color='green', linestyle='--')
        axs[1].set_title("RSI")
        axs[1].legend()
        axs[1].grid(True)

    # MACD
    if 'macd' in df and 'macd_signal' in df:
        axs[2].plot(df['timestamp'], df['macd'], label='MACD', color='blue')
        axs[2].plot(df['timestamp'], df['macd_signal'], label='Signal', color='red')
        axs[2].set_title("MACD")
        axs[2].legend()
        axs[2].grid(True)

    plt.tight_layout()
    plt.show()

def plot_signals(df):
    plt.figure(figsize=(12,8))
    plt.plot(df['timestamp'], df['close'], label = "Price Action", color = "black")
    plt.plot(df['timestamp'], df['sma50'], label='SMA 50', color='blue')
    plt.plot(df['timestamp'], df['sma200'], label='SMA 200', color='orange')
    if 'signal' not in df:
        print("Run strategy first!")
        return
    # buy markers
    buys = df[df['signal'] == 1]
    plt.scatter(buys['timestamp'], buys['close'], label = "Buy Signal", marker="^", color = "green", s = 100)

    # sell markers 
    sells = df[df['signal'] == -1]
    plt.scatter(sells['timestamp'], sells['close'], label = "Sell Signal", marker="v", color = "red", s = 100)
    plt.title("Buy/Sell Signals on Price")
    plt.xlabel("Timestamp")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_equity_curve(df):
    plt.figure(figsize=(12,8))
    plt.plot(df['timestamp'], df['equity'], label='Equity Curve', color='purple')
    plt.title("Equity Curve")
    plt.xlabel("Timestamp")
    plt.ylabel("Portfolio Value")
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()
    return

def plotMDD(max_dd, dd_df, start, end):
    dd_df['Drawdown'].plot(title='Drawdown Over Time', figsize=(10,4), ylabel='Drawdown')
    plt.axhline(y=max_dd, color='red', linestyle='--', label='Max Drawdown')
    plt.axvline(x=start, color = "blue", linestyle='--', label='Max Drawdown Start')
    plt.axvline(x=end, color = "blue", linestyle='--', label='Max Drawdown Stop')
    # Fill the drawdown period
    plt.axvspan(start, end, color="red", alpha=0.1)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()
