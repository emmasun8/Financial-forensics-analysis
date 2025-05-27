import pandas as pd
import matplotlib.pyplot as plt

files = {
    'SHOP': 'SHOP_financials.xlsx',
    'M': 'M_financials.xlsx',
}

def safe_get(df, key):
    # Handles case-insensitive lookup and fuzzy matching
    options = [key, key.upper(), key.lower(), key.title()]
    for opt in options:
        if opt in df.index:
            return df.loc[opt]
    # Try fuzzy match
    matches = [idx for idx in df.index if key.lower() in idx.lower()]
    if matches:
        return df.loc[matches[0]]
    raise KeyError(f"{key} not found in DataFrame index. Available: {df.index.tolist()}")

for ticker, filepath in files.items():
    print(f"\n=== {ticker} Report ===")
    xl = pd.ExcelFile(filepath)
    is_ = xl.parse('Income Statement')
    bs = xl.parse('Balance Sheet')
    cf = xl.parse('Cash Flow')
    is_.set_index(is_.columns[0], inplace=True)
    bs.set_index(bs.columns[0], inplace=True)
    cf.set_index(cf.columns[0], inplace=True)

    # Periods for plotting
    periods = is_.columns.astype(str)

    # BALANCE SHEET: Use exact row names from your screenshot
    # For Current Assets: Current Assets = Working Capital + Current Liabilities
    working_capital = safe_get(bs, 'Working Capital')
    current_liabilities = safe_get(bs, 'Current Liabilities')
    current_assets = working_capital + current_liabilities

    total_liab = safe_get(bs, 'Total Liabilities Net Minority Interest')
    # You can also use 'Common Stock Equity' if you want
    total_equity = safe_get(bs, 'Stockholders Equity')

    # INCOME STATEMENT & CASH FLOW
    total_revenue = safe_get(is_, 'Total Revenue')
    net_income = safe_get(is_, 'Net Income')
    op_cf = safe_get(cf, 'Operating Cash Flow')

    # Key Ratios
    current_ratio = current_assets / current_liabilities
    debt_equity = total_liab / total_equity
    net_profit_margin = net_income / total_revenue
    op_cf_net_income = op_cf / net_income

    # Collect ratios for table/chart
    ratios = pd.DataFrame({
        'Current Ratio': current_ratio,
        'Debt/Equity': debt_equity,
        'Net Profit Margin': net_profit_margin,
        'Op CF / Net Income': op_cf_net_income
    })

    # Print ratios
    print("\nKey Ratios (by period):")
    print(ratios.round(2).T)

    # RED FLAGS
    print("\nPotential Red Flags:")
    if current_ratio.iloc[-1] < current_ratio.iloc[0]:
        print("- Declining liquidity (Current Ratio decreasing)")
    if debt_equity.iloc[-1] > debt_equity.iloc[0]:
        print("- Rising leverage (Debt/Equity increasing)")
    if (net_profit_margin < 0).any():
        print("- Negative profit margin in one or more periods")
    elif net_profit_margin.iloc[-1] < net_profit_margin.iloc[0]:
        print("- Shrinking net profit margin")
    if (op_cf_net_income < 1).sum() >= 2:
        print("- Operating cash flow often below net income (earnings quality)")

    # Line Chart: Revenue & Net Income
    plt.figure(figsize=(8, 4))
    plt.plot(periods, total_revenue, marker='o', label='Total Revenue')
    plt.plot(periods, net_income, marker='o', label='Net Income')
    plt.title(f"{ticker}: Revenue & Net Income Trend")
    plt.xlabel("Period")
    plt.ylabel("USD")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{ticker}_revenue_net_income.png')
    plt.close()

    # Key Ratios Trend
    ratios.plot(marker='o', figsize=(8, 5))
    plt.title(f"{ticker}: Key Ratios Trend")
    plt.xlabel("Period")
    plt.ylabel("Ratio")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{ticker}_key_ratios.png')
    plt.close()

    # Bar Chart: Debt vs Equity
    plt.figure(figsize=(7, 4))
    plt.bar(periods, total_liab, label='Total Liabilities', alpha=0.7)
    plt.bar(periods, total_equity, label='Total Equity', alpha=0.7, bottom=total_liab)
    plt.title(f"{ticker}: Debt vs Equity")
    plt.xlabel("Period")
    plt.ylabel("USD")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{ticker}_debt_equity.png')
    plt.close()

    print(f"Charts saved: {ticker}_revenue_net_income.png, {ticker}_key_ratios.png, {ticker}_debt_equity.png")
    print("\n--- End of Report ---\n")
