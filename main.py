from core.finance import Finance
from analytics.strategies  import sma_crossover
from utils.backtesting import Backtester
from visualization.plot import plot_signals, plot_equity_curve, plotMDD

if __name__ == "__main__":
    f = Finance("SPY", "2025-05-01", "2025-05-01")
    f.load_data(market_hours=True)

    if f.df is not None and not f.df.empty:
        f.save()
    else:
        print("⚠️ No data returned.")

    f.extract_history()
    
    
    f.add_indicators()
    # f.plot()
    f.run_strategy(sma_crossover)
    # print(f.df.head)
    # plot_signals(f.df)
    bt = Backtester(f.df)
    bt.run()
    stats = bt.calculate_trade_stats()
    more_stats = bt.calculateMDD()
    plotMDD(more_stats["Max Drawdown"], 
            more_stats["Drawdown Details"],
            more_stats["Drawdown Start"],
            more_stats["Drawdown End"])
    # max_dd, dd_df, start, end
    # plot_signals(bt.df)
    # # Find the locations where we encounter a buy signal
    # for i in range(1,len(f.df)):
    #     if f.df.loc[i-1, f"sma{50}"] < f.df.loc[i-1, f"sma{200}"] and f.df.loc[i, f"sma{50}"] > f.df.loc[i, f"sma{200}"]:
    #         print(f.df.loc[i])
    
    
    # plot_equity_curve(bt.df)
    
    # df_backtest = bt.run()

    # if df2 is not None and not df2.empty:
    #     print(df2.head)
    # else:
    #     print("Error!")

    # f.add_indicators()