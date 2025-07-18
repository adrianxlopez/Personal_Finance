import os
import requests
import pandas as pd
from dotenv import load_dotenv
from polygon import RESTClient
import glob
from datetime import date

# Load environment variables
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")


def get_data(ticker, start_date, market_hours=False, base_dir = "data"):
    """Fetch minute-level historical data for a ticker or load from disk if cached."""
    # Ensure start_date is a datetime object
    if isinstance(start_date, str):
        start_date_pd = pd.to_datetime(start_date)

    date_str = start_date_pd.strftime('%Y-%m-%d')
    year = start_date_pd.strftime('%Y')
    month = start_date_pd.strftime('%m')
    filename = os.path.join(base_dir,ticker,year, month,f"{date_str}.csv")

    # Do not want to use an API call if the file has already been created
    if os.path.exists(filename):
        print("📁 Found existing file, loading from disk...")
        return pd.read_csv(filename, parse_dates=['timestamp']) #Reads the .csv file with the data we need
    
    # Else, we will make an API request on the according ticker for the appropriate dates
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start_date}/{start_date}"
    
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 5000,
        "apiKey": API_KEY,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return pd.DataFrame()

    data = response.json()
    if "results" not in data:
        print("No results found in the data.")
        return pd.DataFrame()

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
    return df

def extract_csvs(ticker, base_dir="data"):
    """Extract and concatenate all CSVs for a given ticker from nested folders."""
    pattern = os.path.join(base_dir, ticker, "*", "*", "*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"⚠️ No files found for {ticker} in {base_dir}")
        return pd.DataFrame()

    all_data = [pd.read_csv(file, parse_dates=['timestamp']) for file in files]
    combined_df = pd.concat(all_data).sort_values("timestamp").reset_index(drop=True)
    return combined_df


def get_filepath(ticker, df):
    """Generate a structured file path based on timestamp in DataFrame."""
    start_date = df['timestamp'].min()
    year = start_date.strftime("%Y")
    month = start_date.strftime("%m")
    file_date = start_date.strftime("%Y-%m-%d")

    folder_path = os.path.join("data", ticker, year, month)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, f"{file_date}.csv")


def write_csv(ticker, df):
    """Save DataFrame to a structured CSV path."""
    filename = get_filepath(ticker, df)
    if os.path.exists(filename):
        print("Found exisiting file")
        return
    df.to_csv(filename, index=False)
    print("✅ CSV file saved:", filename)