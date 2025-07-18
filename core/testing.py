# def describe_person(name, age, **kwargs):
#     print(f"Name: {name}")
#     print(f"Age: {age}")

#     for key, value in kwargs.items():
#         print(f"{key.upper()}: {value}")

# #try it with diff keywords
# describe_person(
#     name="Adrian",
#     age=25,
#     hobby="Soccer",
#     city="Salinas",
#     occupation="Engineer"
# )
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_drawdowns(returns: pd.Series, is_cumulative=False):
    """
    Calculate drawdowns and durations from a series of returns.
    
    Parameters:
    - returns: pd.Series (daily/monthly/whatever frequency)
    - is_cumulative: if True, series is assumed to be cumulative already.
    
    Returns:
    - max_drawdown: float
    - duration: int (in time periods)
    - drawdown_df: DataFrame with drawdown details
    """
    if not is_cumulative:
        cumulative = (1 + returns).cumprod()
    else:
        cumulative = returns

    peak = cumulative.cummax()
    drawdown = cumulative / peak - 1

    # Find max drawdown
    max_drawdown = drawdown.min()
    end_date = drawdown.idxmin()
    start_date = cumulative[:end_date][cumulative[:end_date] == peak[end_date]].idxmax()
    duration = (end_date - start_date).days if isinstance(end_date, pd.Timestamp) else end_date - start_date

    # Combine into DataFrame
    drawdown_df = pd.DataFrame({
        'Cumulative': cumulative,
        'Peak': peak,
        'Drawdown': drawdown
    })

    return max_drawdown, duration, drawdown_df, start_date, end_date

# Example: Monthly returns
dates = pd.date_range("2023-01-01", periods=12, freq="ME")
returns = pd.Series([0.02, -0.01, 0.03, -0.04, 0.01, 0.02, -0.03, 0.01, 0.02, -0.02, 0.01, 0.03], index=dates)

max_dd, duration, dd_df, start, end = calculate_drawdowns(returns)

print(f"📉 Maximum Drawdown: {max_dd:.2%}")
print(f"⏳ Drawdown Duration: {duration} days or periods")


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