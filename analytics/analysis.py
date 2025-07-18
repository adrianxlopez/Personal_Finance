import pandas as pd 
import numpy as np

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