from dotenv import load_dotenv
import os
import requests
import pandas as pd
from Visualization.plot import plot


#load environment variables
load_dotenv()
API_KEY = os.getenv("FMP_API_KEY")

def DCF_Advanced(filename, ticker=None):
    url = f"https://financialmodelingprep.com/stable/custom-discounted-cash-flow?symbol={ticker}&apikey={API_KEY}"
    
    if os.path.exists(filename):
        print("File Exists...")
        df = read(filename)
        return df
    
    response = requests.get(url)

    if response.status_code != 200: 
        print("Error: Status Code {response.status_code}")

    try: 
        data = response.json()
    except ValueError:
        print("Error: Failed to decode JSON.")
        return None 
    
    df = pd.DataFrame(data)
    df_adjusted = format(df)
    return df_adjusted

def Valuation(df, growth_override= None, wacc_override= None):
    # Optional overrides
    if wacc_override:
        df["wacc"] = wacc_override
    if growth_override:
        df["longTermGrowthRate"] = growth_override

    try:
        equity_value = df["equityValue"].iloc[0]
        diluted_shares = df["dilutedSharesOutstanding"].iloc[0]
        equity_value_per_share = equity_value / diluted_shares  # back to absolute value
        current_price = df["price"].iloc[0]
        valuation_status = "Undervalued" if equity_value_per_share > current_price else "Overvalued"
        if valuation_status == "Undervalued":
            df["difference"] = round((equity_value_per_share - current_price),2)
        else:
            df["difference"] = round((current_price - equity_value_per_share),2)
    except Exception as e:
        print(f"Error computing valuation: {e}")
        equity_value_per_share = None
        current_price = None
        valuation_status = "Unknown"

    df['valuation_status'] = valuation_status
    return df
    
def write(df, ticker):
    file = f"{ticker}_Financials.csv"
    if not df.empty or not df == None:        
        df.to_csv(file, index=False)
        print(f"Successfully wrote {file}")

def read(filename):
    if os.path.exists(filename):
        print("Found File!..")
        df = pd.read_csv(filename)
        return df
def format(df):
    columns_to_scale= ['revenue', 'ebitda',
                       'ebit', 'depreciation', 
                       'totalCash', 'receivables',
                       'inventories', 'capitalExpenditure',
                       'dilutedSharesOutstanding', 'totalDebt',
                       'totalEquity','totalCapital',
                       'taxRateCash', 'ebiat', 'ufcf', 'sumPvUfcf',
                       'terminalValue', 'presentTerminalValue', 'netDebt',
                       'equityValue', 'freeCashFlowT1']
    
    for col in columns_to_scale:
        if col in df.columns:
            df[col] = df[col] / 1000000
    df[columns_to_scale] = df[columns_to_scale].round(2)
    return df



if __name__ == "__main__":
    filepath = "/Users/adrianlopez/Personal/Personal_Finance/AAPL_Financials.csv"
    df = DCF_Advanced(filepath, ticker="AAPL")
    write(df, ticker = "AAPL")

    # df = read("/Users/adrianlopez/Personal/Personal_Finance/AAPL_Financials.csv")
    # # df = format(df)
    # write(df, "AAPL")
    plot(df, "revenue")