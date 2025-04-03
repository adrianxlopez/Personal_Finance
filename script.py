import camelot
import pandas as pd
import matplotlib.pyplot as plt

def parse_financial_statements(pdf_path):
    """
    Extract tables from the PDF and try to assign them to
    income statement, balance sheet, and cash flow statement.
    """
    # Extract tables from all pages using a stream-based flavor (adjust if needed)
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
    
    income_statement = None
    balance_sheet = None
    cash_flow = None
    
    # Loop through all extracted tables and look for key words
    for table in tables:
        df = table.df
        # Convert the first row to lower case text for keyword matching
        header_text = ' '.join(df.iloc[0].str.lower())
        if 'income' in header_text and 'statement' in header_text:
            income_statement = df
        elif 'balance' in header_text and 'sheet' in header_text:
            balance_sheet = df
        elif 'cash' in header_text and 'flow' in header_text:
            cash_flow = df
            
    return income_statement, balance_sheet, cash_flow

def plot_metric_trend(statement_df, metric):
    """
    Finds a row containing the metric (e.g. "Revenue") in the statement DataFrame
    and plots its values across the columns (assumed to be years).
    """
    # Find the row that matches the metric name (case-insensitive search)
    row = statement_df[statement_df.iloc[:, 0].str.contains(metric, case=False, na=False)]
    if row.empty:
        print(f"Metric '{metric}' not found in the provided statement.")
        return

    # Assuming the first column is the metric name and the rest are yearly values:
    years = statement_df.columns[1:]
    try:
        # Convert values to float (adjust if formatting requires cleaning)
        values = row.iloc[0, 1:].astype(float)
    except ValueError:
        print("Could not convert metric values to float. Check your PDF formatting.")
        return

    plt.figure(figsize=(8, 5))
    plt.plot(years, values, marker='o')
    plt.title(f"{metric} Trend Over Time")
    plt.xlabel("Year")
    plt.ylabel(metric)
    plt.grid(True)
    plt.show()

def discounted_cash_flow_analysis(cash_flows, discount_rate=0.1, terminal_growth_rate=0.02):
    """
    Performs a basic DCF analysis given a list of free cash flows.
    cash_flows: list of forecast free cash flow numbers (assumed sequential by year).
    discount_rate: the discount rate (WACC, for example).
    terminal_growth_rate: the long-term growth rate for the terminal value.
    Returns the enterprise value based on the DCF model.
    """
    present_value = 0
    for i, cf in enumerate(cash_flows, start=1):
        present_value += cf / ((1 + discount_rate) ** i)
    
    # Calculate terminal value using the last year's cash flow
    last_cf = cash_flows[-1]
    terminal_value = last_cf * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    terminal_value_discounted = terminal_value / ((1 + discount_rate) ** len(cash_flows))
    
    total_value = present_value + terminal_value_discounted
    return total_value

if __name__ == "__main__":
    # Path to your company's financial PDF file
    pdf_path = "company_financials.pdf"  # Change this to your actual PDF file path
    
    # Parse the PDF to extract the financial statements
    income_statement, balance_sheet, cash_flow = parse_financial_statements(pdf_path)
    
    # Example: Plot a trend for a key metric (e.g. Revenue) from the income statement
    if income_statement is not None:
        print("Plotting Revenue trend from the income statement...")
        plot_metric_trend(income_statement, "Revenue")
    else:
        print("Income statement not found in the PDF.")
    
    # Example: Perform DCF analysis using free cash flow from the cash flow statement
    if cash_flow is not None:
        # Search for a row that includes "Free Cash Flow" (adjust as necessary)
        fcf_row = cash_flow[cash_flow.iloc[:, 0].str.contains("Free Cash Flow", case=False, na=False)]
        if not fcf_row.empty:
            try:
                # Assume that the free cash flow values are in columns 2 onward
                cash_flow_values = list(fcf_row.iloc[0, 1:].astype(float))
                dcf_value = discounted_cash_flow_analysis(cash_flow_values)
                print(f"Discounted Cash Flow (DCF) Value: {dcf_value:,.2f}")
            except ValueError:
                print("Error converting free cash flow values. Please verify the PDF formatting.")
        else:
            print("Free Cash Flow row not found in the cash flow statement.")
    else:
        print("Cash flow statement not found in the PDF.")
