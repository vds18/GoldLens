# GoldLens — Commodity Intelligence Dashboard

GoldLens is a data-driven research dashboard for analyzing MCX gold futures contracts using historical bhavcopy data. It helps users explore contract prices, relative-value spreads, statistical anomalies, term structure, and exploratory backtest results.

## Features

- **Historical Data Pipeline:** Combines and processes date-wise MCX bhavcopy CSV files.
- **Data Quality & Validation:** Checks missing prices, invalid dates, duplicate records, and contract coverage.
- **Contract Monitor:** Displays available gold futures contracts and historical data status.
- **Spread Analysis:** Compares normalized prices for contracts sharing the same trading date and expiry.
- **Anomaly Detection:** Identifies unusual historical spread movements using rolling statistical measures.
- **Term Structure Analysis:** Examines price relationships across contract expiries.
- **Exploratory Backtesting:** Reports completed trades, open positions, and illustrative spread-movement statistics.
- **Interactive Dashboard:** Presents the results through a Streamlit interface.

## Technology Stack

- Python
- Pandas and NumPy
- Streamlit
- Plotly, if used by the dashboard
- MCX bhavcopy CSV data

## Project Structure

```text
GoldLens/
├── README.md
└── backend/
    ├── app.py
    ├── combine_bhavcopy.py
    ├── historical_data.py
    ├── normalize_gold.py
    ├── data_quality.py
    ├── spread_analysis.py
    ├── anomaly_analysis.py
    ├── term_structure.py
    ├── backtest.py
    └── data/
        ├── raw/
        └── processed/
```

## Setup

1. Install Python 3.11 or a compatible version.
2. Clone the repository and navigate to the backend directory.
3. Create and activate a virtual environment.
4. Install the required packages from `requirements.txt`, if provided.
5. Place the required date-wise MCX bhavcopy CSV files in `data/raw/`.
6. Run the processing scripts in the required order.
7. Launch the dashboard:

```bash
python -m streamlit run app.py --server.port 8502
```

Open `http://localhost:8502` in your browser.

## Research Limitations

- Historical coverage depends on the available bhavcopy files.
- Price normalization is provisional and must be validated against official contract specifications.
- Spread comparisons are research indicators, not guaranteed arbitrage opportunities.
- Backtest results are exploratory spread-movement proxies, not verified executable trading returns.
- Realistic contract quantities, liquidity, brokerage, taxes, slippage, and expiry rules must be incorporated before making performance claims.

## Disclaimer

GoldLens is an educational and analytical research prototype. It is not financial advice and should not be used as the sole basis for investment or trading decisions.
