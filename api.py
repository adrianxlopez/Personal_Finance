import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from polygon import RESTClient
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volume import VolumeWeightedAveragePrice
import time

# Load environment variables
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")

class Finance:
    def __init__(self, capital, ticker):
        self.capital = capital
        self.ticker = ticker
        self.df = None

    def get_data(self, ticker=None, market_hours=False, dates=None):
        """Fetch minute-level historical data for a ticker."""
        ticker = ticker or self.ticker
        filename = f"{ticker}_historical_data_{dates[0]}_to_{dates[1]}.csv"

        if os.path.exists(filename):
            print("📁 Found existing file, loading from disk...")
            self.df = pd.read_csv(filename, parse_dates=['timestamp'])
            return self.df

        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{dates[0]}/{dates[1]}"
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": 5000,
            "apiKey": API_KEY,
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            self.df = pd.DataFrame()
            return self.df

        data = response.json()
        if "results" not in data:
            print("No results found in the data.")
            self.df = pd.DataFrame()
            return self.df

        df = pd.DataFrame(data["results"])
        df['t'] = pd.to_datetime(df['t'], unit='ms', utc=True).dt.tz_convert('America/Los_Angeles').dt.tz_localize(None)
        df.rename(columns={
            't': 'timestamp',
            'v': 'volume',
            'vw': 'vwap',
            'o': 'open',
            'c': 'close',
            'h': 'high',
            'l': 'low',
            'n': 'transactions'
        }, inplace=True)

        if market_hours:
            market_open = pd.Timestamp('6:30:00').time()
            market_close = pd.Timestamp('13:00:00').time()
            df = df[(df['timestamp'].dt.time >= market_open) & (df['timestamp'].dt.time <= market_close)]

        # self.write_csv(df, ticker)
        self.df = df
        return df
    def get_filepath(self, ticker, df):
        start_date = df['timestamp'].min()
        end_date = df['timestamp'].max()

        # Extract year and month from start_date
        year = start_date.strftime("%Y")
        month = start_date.strftime("%m")
        file_date = start_date.strftime("%Y-%m-%d")

        # Build folder and filename
        folder_path = os.path.join(ticker, year, month)
        os.makedirs(folder_path, exist_ok=True)  # Ensure folder exists
        filename = os.path.join(folder_path, f"{file_date}.csv")

        return filename

    def write_csv(self):
        """Save DataFrame to CSV."""
        filename = self.get_filepath(self.ticker, self.df)
        self.df.to_csv(filename, index=False)
        print("✅ CSV file saved:", filename)


    def get_sma(self, window=14):
        """Fetch SMA indicator data from Polygon API."""
        url = f"https://api.polygon.io/v1/indicators/sma/{self.ticker}"
        params = {
            "timespan": "minute",
            "window": window,
            "series_type": "close",
            "order": "asc",
            "limit": 100,
            "apiKey": API_KEY
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Error fetching SMA:", response.text)
            return pd.DataFrame()

        values = response.json().get("results", {}).get("values", [])
        df = pd.DataFrame(values)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_convert('America/Los_Angeles').dt.tz_localize(None)
        df.rename(columns={'value': 'SMA'}, inplace=True)
        return df[['timestamp', 'SMA']]

    def get_rsi(self, window=14):
        """Fetch RSI indicator data from Polygon API."""
        url = f"https://api.polygon.io/v1/indicators/rsi/{self.ticker}"
        params = {
            "timespan": "minute",
            "window": window,
            "series_type": "close",
            "order": "asc",
            "limit": 100,
            "apiKey": API_KEY
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Error fetching RSI:", response.text)
            return pd.DataFrame()

        values = response.json().get("results", {}).get("values", [])
        df = pd.DataFrame(values)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_convert('America/Los_Angeles').dt.tz_localize(None)
        df.rename(columns={'value': 'RSI'}, inplace=True)
        return df[['timestamp', 'RSI']]

    def add_indicators(self, df):
        # Moving indicators
        sma_20 = SMAIndicator(close=df['close'], window=50)
        ema_20 = EMAIndicator(close=df['close'], window=50)

        # Relative Strength Index (RSI)
        rsi_14 = RSIIndicator(df['close'], window=14)

        # Volume Weighted Average Price (VWAP)
        VWAPIndicator = VolumeWeightedAveragePrice(
            high=df['high'], 
            low=df['low'], 
            close=df['close'], 
            volume=df['volume'], 
            window=14
        )
        # Append to dataframe
        df['SMA'] = sma_20.sma_indicator()
        df['EMA'] = ema_20.ema_indicator()
        df['RSI'] = rsi_14.rsi()
        df['VWAP'] = VWAPIndicator.vwap

        df['VWAP_pandas'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

        return df

    def add_signals(self, df):
        """Add buy/sell signals based on price crossing VWAP."""
        df['Buy'] = (df['close'] > df['vwap']) & (df['close'].shift(1) <= df['vwap'].shift(1))
        df['Sell'] = (df['close'] < df['vwap']) & (df['close'].shift(1) >= df['vwap'].shift(1))
        return df

    def plotting(self, data):
        """Plot close price, SMA, RSI, and buy/sell signals."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        ax1.plot(data['timestamp'], data['close'], label='Close Price')
        ax1.plot(data['timestamp'], data['SMA'], label='SMA', color="red")
        ax1.scatter(data[data['Buy']]['timestamp'], data[data['Buy']]['close'],
                    label='Buy Signal', marker='^', color='green', s=50)
        ax1.scatter(data[data['Sell']]['timestamp'], data[data['Sell']]['close'],
                    label='Sell Signal', marker='v', color='red', s=50)
        ax1.set_ylabel("Price")
        ax1.legend(loc="upper left")

        ax2.plot(data['timestamp'], data['RSI'], label='RSI', linestyle='--')
        ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(30, color='green', linestyle='--', alpha=0.5)
        ax2.set_ylabel("RSI")
        ax2.set_xlabel("Date")
        ax2.legend()
        ax2.set_title("14-Period RSI")

        plt.tight_layout()
        plt.show()

    def profitability(self, data, max_position_pct=0.25):
        """Simulate a basic trading strategy and calculate profitability."""
        initial_capital = self.capital
        data = data.dropna(subset=['SMA', 'RSI']).sort_values('timestamp').reset_index(drop=True)

        position = None
        trades = []
        profits = []
        capital = initial_capital
        portfolio_value = [capital]

        for _, row in data.iterrows():
            price = row['close']
            timestamp = row['timestamp']

            if row['Buy'] and position is None:
                position_size = capital * max_position_pct # dependent on portfolio size
                shares = position_size // price
                if shares > 0:
                    position = {'entry_price': price, 'shares': shares, 'entry_time': timestamp}
                    capital -= shares * price

            elif row['Sell'] and position is not None:
                proceeds = position['shares'] * price
                profit = proceeds - (position['shares'] * position['entry_price'])
                capital += proceeds
                trades.append({
                    'Buy Time': position['entry_time'],
                    'Buy Price': position['entry_price'],
                    'Sell Time': timestamp,
                    'Sell Price': price,
                    'Shares': position['shares'],
                    'Profit': profit,
                    'Capital': capital
                })
                profits.append(profit)
                position = None

            portfolio_value.append(capital + (position['shares'] * price if position else 0))

        trade_df = pd.DataFrame(trades)
        print("📊 Trades:\n", trade_df)
        print(f"💼 Final Capital: {capital:.2f}")
        print(f"📈 Portfolio Value: {portfolio_value[-1]:.2f}")
        print(f"Total Profits/Losses: {sum(profits):.2f}")
        return trade_df, portfolio_value

    def output(self, df):
        if ("VWAP" in df.columns) & ("VWAP_pandas" in df.columns):
            for _, row in df.iterrows():
                print(f"Volume: {row['volume']:,}, Open: {row['open']:.2f}, High: {row['high']:.2f}, Low: {row['low']:.2f}, close: {row['close']:.2f}, vwap: {row['vwap']:.2f}, VWAP: {row['VWAP']:.2f}, VWAP_pandas: {row['VWAP_pandas']:.2f}, SMA: {row['SMA']:.2f},")
        elif ("VWAP" in df.columns):
            for _, row in df.iterrows():
                print(f"Volume: {row['volume']:,}, Open: {row['open']:.2f}, High: {row['high']:.2f}, Low: {row['low']:.2f}, close: {row['close']:.2f}, vwap: {row['vwap']:.2f}, VWAP: {row['VWAP']:.2f},")
        else: 
            for _, row in df.iterrows():
                print(f"Volume: {row['volume']:,}, Open: {row['open']:.2f}, High: {row['high']:.2f}, Low: {row['low']:.2f}, close: {row['close']:.2f}, vwap: {row['vwap']:.2f}")

    def plotDifferences(self, df):
        # Create a figure and Axes 
        fig, (ax1,ax2) = plt.subplots(2,1, figsize=(12,8))

        #use the axes to plot 
        ax1.plot(df["timestamp"],df["vwap"], label = "API Generated VWAP", color = "red", linestyle='-')
        ax1.plot(df["timestamp"],df["VWAP"], label = "TA Generated VWAP", color = "blue", linestyle='--')
        ax1.set_xlabel("Time")
        ax1.set_ylabel("$")
        ax1.legend()
        ax1.grid()


        # second plot 
        ax2.plot(df["timestamp"],(df["vwap"]- df["VWAP"]).abs(), label = "VWAP Differences", color = "red")
        ax2.axhline(0, color = "black", linestyle = "--") #horizontal line at y = 0
        ax2.axhline(1.5, color = "red", linestyle = "dotted") #horizontal line at y = 1.5
        ax2.fill_between(
            df["timestamp"],
            1.5,
            7.5,
            color = "red",
            alpha = 0.3,
        )
        ax2.set_title("VWAP Differences")
        ax2.legend()
        ax2.grid()
        plt.tight_layout()
        plt.show()

    def extract(self, ticker, base_dir="."):
        import glob 
        pattern = os.path.join(base_dir, ticker, "*", "*", "*.csv")
        files = sorted(glob.glob(pattern))
        all_data = []
        for file in files: 
            df = pd.read_csv(file, parse_dates=['timestamp'])
            all_data.append(df)
        combined_df = pd.concat(all_data).sort_values("timestamp").reset_index(drop=True)
        return combined_df



def main():

    trader = Finance(capital=10000, ticker="SPY")
    # df = trader.get_data(dates=["2025-03-31", "2025-03-31"], market_hours=True)
    df = trader.extract(ticker="SPY")
    # trader.write_csv()

    # Generate business days only (excludes weekends)
    # dates = pd.date_range(start="2024-04-01", end="2025-03-30", freq='B')  # 'B' = business day
    # for date in dates:
    #     date_str = date.strftime('%Y-%m-%d')
    #     df = trader.get_data(dates=[date_str, date_str], market_hours=True)
    #     # Optional: Write to disk or analyze here
    #     print(f"📅 Pulled data for {date_str} - Rows: {len(df)}")
    #     if not df.empty: 
    #         trader.write_csv()
    #     else:
    #         print(f"No data for {date_str}")
    #     time.sleep(13)

    # if df.empty:
    #     return
    
    df = trader.add_indicators(df)
    # # trader.output(df)
    # # Finance.output(df)
    df = trader.add_signals(df)
    # trader.plotDifferences(df)

    # # Optional: Plotting
    trader.plotting(df)

    # # Profitability
    trader.profitability(df)

if __name__ == "__main__":
    main()
