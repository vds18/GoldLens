# GoldLens — Commodity Intelligence Dashboard

**An interactive research dashboard for MCX gold futures analysis.**

GoldLens transforms historical MCX bhavcopy data into actionable research insights through contract monitoring, data quality validation, spread analysis, anomaly detection, term structure analysis, and exploratory backtesting.

### 🚀 Live Demo

**[Launch GoldLens Dashboard](https://goldlens-bpf4to3y9kflvhw6lznksq.streamlit.app)**

**[View Source Code on GitHub](https://github.com/vds18/GoldLens)**

---

## ✨ Features

- **Contract Monitor:** Explore supported gold futures contracts — GOLDM, GOLDTEN, GOLDGUINEA, and GOLDPETAL.
- **Historical Data Analysis:** Process and analyze historical MCX bhavcopy data.
- **Data Quality & Validation:** Inspect missing prices, duplicate records, historical coverage, and contract-level data quality.
- **Spread Analysis:** Compare normalized prices across supported gold futures contracts.
- **Anomaly Detection:** Identify unusual historical spread movements using statistical measures.
- **Term Structure Analysis:** Examine price relationships across contract expiries.
- **Exploratory Backtesting:** Review simulated spread movements, trade records, and backtest reports where available.
- **Interactive Dashboard:** Explore analytical outputs through a Streamlit-based interface.

## 🛠️ Tech Stack

- **Language:** Python
- **Data Processing:** Pandas, NumPy
- **Dashboard:** Streamlit
- **Visualization:** Plotly (where used)
- **Data Source:** MCX bhavcopy CSV files
- **Version Control:** Git and GitHub
- **Deployment:** Streamlit Community Cloud

## 📊 Current Data Snapshot

The deployed prototype currently displays:

| Metric | Value |
|---|---:|
| Supported gold contracts | 4 |
| Historical trading dates | 34 |
| Historical data through | 19 October 2026 |
| Historical records | 816 |

These figures reflect the current dashboard snapshot and may change when the underlying dataset is updated.

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

- Python 3.11 or a compatible version
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
pip install -r backend/requirements.txt
```

### 4. Launch the dashboard

```powershell
cd backend
python -m streamlit run app.py --server.port 8502
```

Open **http://localhost:8502** in your browser.

Ensure the required processed data files are available in `backend/data/processed/` before launching the application.

## 🔬 Research Limitations

- Historical coverage depends on the available source data.
- Contract normalization and expiry conventions require validation against official contract specifications.
- Statistical anomalies indicate unusual historical movements, not necessarily profitable opportunities.
- Backtesting results are exploratory and should not be interpreted as verified trading performance.
- Transaction costs, brokerage, taxes, slippage, liquidity, contract quantities, and execution constraints must be considered before evaluating real-world performance.
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

[GitHub](https://github.com/vds18)

---

*Built to explore commodity market data through transparent, data-driven analysis.*
