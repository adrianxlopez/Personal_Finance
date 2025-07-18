from utils.io import get_data, write_csv, extract_csvs
from analytics.indicators import sma, ema, rsi, vwap, macd
from visualization.plot import plot_price_with_indicators, plot_signals, plot_equity_curve
from analytics.strategies import sma_crossover
import pandas as pd

class Finance:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.df = None
        self.indicators_added = []

    def load_data(self, market_hours=False):
        df = get_data(self.ticker, self.start_date, market_hours)
        if df is not None and not df.empty:
            self.df = df
            print(f"✅ Successfully loaded data for {self.ticker} {len(self.df)} rows.")

    
    def add_indicators(self, indicators=None):
        """
        Add selected indicators to the DataFrame.

        :param indicators: List of indicator names to add.
        """
        if self.df is None:
            raise ValueError("❌ No data loaded.")

        # Default to add all indicators if none are specified
        if indicators is None:
            indicators = ['sma', 'ema', 'rsi', 'vwap', 'macd']

        # Add indicators based on the list provided
        for indicator in indicators:
            if indicator == 'sma':
                self.df['sma'] = sma(self.df, 20)
                self.indicators_added.append('sma')
            elif indicator == 'ema':
                self.df['ema'] = ema(self.df, 20)
                self.indicators_added.append('ema')
            elif indicator == 'rsi':
                self.df['rsi'] = rsi(self.df, 14)
                self.indicators_added.append('rsi')
            elif indicator == 'vwap':
                self.df['vwap'] = vwap(self.df, 14)
                self.indicators_added.append('vwap')
            elif indicator == 'macd':
                macd_df = macd(self.df)
                self.df = pd.concat([self.df, macd_df], axis=1)
                self.indicators_added.append('macd')
            else:
                print(f"⚠️ Unknown indicator: {indicator}")
        
        print(f"✅ Indicators added: {', '.join(self.indicators_added)}")

    def get_indicators(self):
        """Return a list of added indicators."""
        return self.indicators_added
        
    def run_backtest(self):
        pass

    def save(self):
        if self.df is not None and not self.df.empty:
            write_csv(self.ticker, self.df)

    def extract_history(self, base_dir="data"):
        '''Load Historical data into one single dataframe'''
        df = extract_csvs(self.ticker, base_dir)
        if df is not None and not df.empty:
            self.df = df
            print(f"Historical data loaded for {self.ticker}. {len(df)} rows.")
        else:
            print(f"No Historical data was found for {self.ticker}")
    
    def plot(self):
        if self.df is None or self.df.empty:
            print("No data to plot.")
            return
        plot_price_with_indicators(self.df, self.ticker)

    def run_strategy(self, strategy_fn, **kwargs):
        if self.df is None or self.df.empty:
            raise ValueError("DataFrame is empty. Load data first.")
        self.df = strategy_fn(self.df, **kwargs)