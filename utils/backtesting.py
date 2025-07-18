from analytics.analysis import calculate_drawdowns
class Backtester: 
    def __init__(self, df, initial_cash=10000, fee=0.01):
        self.df = df.copy()
        self.cash = initial_cash
        self.position = 0
        self.fee = fee
        self.trades = []
        self.equity_curve = []


    def run(self):
        for i, row in self.df.iterrows():
            price = row['close']
            signal = row.get('signal', 0)

            # Buy
            if signal == 1 and self.position == 0:
                self.position = self.cash / (price * (1 - self.fee))
                self.cash = 0
                self.trades.append((row['timestamp'], 'BUY', price))

            # Sell
            elif signal == -1 and self.position > 0:
                self.cash = self.position * price * (1 - self.fee)
                self.position = 0
                self.trades.append((row['timestamp'], 'SELL', price))

            # Record equity
            equity = self.cash if self.position == 0 else self.position * price
            self.equity_curve.append(equity)

        self.df['equity'] = self.equity_curve
        return self.df
    
    def calculate_trade_stats(self):
        entry_price = None
        profits = []

        for timestamp, action, price in self.trades:
            if action == 'BUY':
                entry_price = price
            elif action == 'SELL' and entry_price is not None:
                profits.append(price - entry_price)
                entry_price = None

        total_profit = sum(profits)
        num_trades = len(profits)
        win_rate = sum(p > 0 for p in profits) / num_trades if num_trades > 0 else 0

        return {
            "Total Profit": round(total_profit,2),
            "Number of Trades": num_trades,
            "Average Profit": round(total_profit / num_trades, 2) if num_trades > 0 else 0,
            "Win Rate": round(win_rate * 100, 2),
        }

    def calculateMDD(self):
        equity_series = self.df['equity']
        returns = equity_series.pct_change().dropna()
        # Call external drawdown calculator
        max_dd, duration, dd_df, start_date, end_date = calculate_drawdowns(returns)

        print(f"📉 Max Drawdown: {max_dd:.2%}")
        print(f"📆 Drawdown Duration: {duration} days")
        return {
        "Max Drawdown": max_dd,
        "Drawdown Duration": duration,
        "Drawdown Start": start_date,
        "Drawdown End": end_date,
        "Drawdown Details": dd_df,
    }
