# GoldLens — Commodity Intelligence Dashboard

**An interactive research dashboard for MCX gold futures analysis.**

GoldLens transforms historical MCX bhavcopy data into research insights through contract monitoring, data quality validation, spread analysis, statistical anomaly detection, term structure analysis, and exploratory backtesting.

🔗 **[Launch Live Dashboard](https://goldlens-bpf4to3y9kflvhw6lznksq.streamlit.app/)** · **[View Source Code](https://github.com/vds18/GoldLens)**

---

## ✨ Features

- **Contract Monitor:** Explore four supported gold futures contracts: `GOLDM`, `GOLDTEN`, `GOLDGUINEA`, and `GOLDPETAL`.
- **Historical Data Analysis:** Process and analyze historical MCX bhavcopy data.
- **Data Quality & Validation:** Inspect missing prices, duplicate records, historical coverage, and contract-level data quality.
- **Spread Analysis:** Compare normalized prices across supported gold futures contracts.
- **Statistical Anomaly Detection:** Identify unusual historical spread movements using historical statistical measures.
- **Term Structure Analysis:** Examine price relationships across contract expiries.
- **Exploratory Backtesting:** Review simulated spread movements, trade records, and backtest reports where available.
- **Interactive Visualizations:** Explore analytical outputs through a Streamlit dashboard.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Data processing | Pandas, NumPy |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Data source | MCX bhavcopy CSV files |
| Version control | Git, GitHub |
| Deployment | Streamlit Community Cloud |

## 📊 Current Data Snapshot

The current prototype's documented historical snapshot is:

| Metric | Value |
|---|---:|
| Supported gold contracts | 4 |
| Historical trading dates | 34 |
| Latest data date | 19 October 2026 |
| Historical records | 816 |

These figures describe the current dataset snapshot and may change as the underlying data is updated. GoldLens analyzes historical data; it does not claim to provide live market prices.

## 🔍 Analytical Workflow

1. **Load** historical MCX bhavcopy CSV files.
2. **Validate** records, dates, prices, duplicates, and contract coverage.
3. **Analyze** price relationships across supported contracts.
4. **Detect** unusual spread movements against historical baselines.
5. **Explore** term structure and backtesting outputs.
6. **Interpret** results with attention to data limitations and research assumptions.

## 📁 Project Structure

```text
GoldLens/
├── README.md
└── backend/
    ├── app.py
    ├── requirements.txt
    ├── data_loader.py
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

## ⚙️ Run Locally

### Prerequisites

- Python 3.11 or another version compatible with the project's dependencies
- Git

### 1. Clone the repository

```bash
git clone https://github.com/vds18/GoldLens.git
cd GoldLens
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r backend/requirements.txt
```

### 4. Prepare the data

Ensure the required raw and processed data files are present in the expected locations under `backend/data/`. Follow the repository's data-processing scripts and the paths configured in the application.

### 5. Launch the dashboard

From the repository root:

```powershell
python -m streamlit run backend/app.py --server.port 8502
```

Open [http://localhost:8502](http://localhost:8502) in your browser.

## 🔬 Research Limitations

- Historical coverage depends on the available source data.
- Contract normalization and expiry conventions require validation against official contract specifications.
- Statistical anomalies indicate unusual historical movements; they do not establish profitable trading opportunities.
- Backtesting results are exploratory and should not be interpreted as verified trading performance.
- Transaction costs, brokerage, taxes, slippage, liquidity, contract quantities, and execution constraints matter when assessing real-world performance.
- Historical results do not guarantee future outcomes.

## 🗺️ Roadmap

- Expand historical data coverage.
- Improve contract and expiry validation.
- Strengthen backtesting with realistic transaction costs and execution assumptions.
- Add further analytical metrics and interactive visualizations.
- Improve testing, documentation, and deployment reliability.

## ⚠️ Disclaimer

GoldLens is an educational and analytical research prototype. It is not financial advice, does not guarantee trading profits, and should not be used as the sole basis for investment or trading decisions.

## 👩‍💻 Author

**Vanshika Dutt Srivastava**

[GitHub Profile](https://github.com/vds18) · [GoldLens Repository](https://github.com/vds18/GoldLens)

---

*Built to explore commodity market data through transparent, data-driven analysis.*
