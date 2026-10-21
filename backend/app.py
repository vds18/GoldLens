
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"
NORMALIZED_FILE = DATA_DIR / "normalized_gold.csv"
SPREAD_FILE = DATA_DIR / "gold_spreads.csv"
HISTORY_FILE = DATA_DIR / "historical_gold.csv"
QUALITY_FILE = DATA_DIR / "data_quality_report.csv"
OPEN_POSITIONS_FILE = DATA_DIR / "backtest_open_positions.csv"

st.set_page_config(
    page_title="GoldLens | Market Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Design system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --gold: #E7BD68;
    --bg: #090E19;
    --panel: #111827;
    --border: #263247;
    --muted: #94A3B8;
    --white: #F1F5F9;
}

.stApp {
    background: var(--bg);
    color: var(--white);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(9, 14, 25, 0.95);
}

[data-testid="stSidebar"] {
    background: #0D1422;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--white) !important;
    letter-spacing: -0.5px;
}

h1 { font-size: 2.35rem !important; }
h2 { font-size: 1.35rem !important; }
h3 { font-size: 1.05rem !important; }

p, label, [data-testid="stMarkdownContainer"] {
    color: #CBD5E1;
}

.goldlens-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--gold);
    letter-spacing: 2px;
}

.hero {
    background: linear-gradient(115deg, #151F31 0%, #101827 65%, #242015 100%);
    border: 1px solid #344155;
    border-radius: 18px;
    padding: 27px 30px;
    margin: 8px 0 24px 0;
}

.eyebrow {
    color: var(--gold);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.15rem;
    font-weight: 700;
    color: #F8FAFC;
    margin: 9px 0 5px 0;
}

.hero-subtitle {
    color: #AAB8CC;
    font-size: 0.95rem;
}

.metric-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    min-height: 112px;
}

.metric-label {
    font-size: 0.76rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-top: 10px;
}

.metric-note {
    color: var(--gold);
    font-size: 0.76rem;
    margin-top: 4px;
}

.section-label {
    color: var(--gold);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

div[data-testid="stPlotlyChart"],
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

.stAlert {
    border-radius: 10px;
}

div[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 15px 18px;
}

div[data-testid="stMetricLabel"] {
    color: var(--muted);
}

div[data-testid="stMetricValue"] {
    color: var(--gold);
}

hr {
    border-color: var(--border);
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

/* ---------- GoldLens UI polish ---------- */

/* Dark contract selector */
[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div > div {
    background: #111827 !important;
    border: 1px solid #344155 !important;
    border-radius: 10px !important;
}

[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: #263247 !important;
    border: 1px solid #E7BD68 !important;
    border-radius: 6px !important;
}

[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
    color: #F8FAFC !important;
}

/* More consistent sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1422 0%, #0A101C 100%);
}

[data-testid="stSidebar"] hr {
    margin-top: 1.3rem;
    margin-bottom: 1.3rem;
    border-color: #263247;
}

/* Premium buttons */
.stButton > button,
.stDownloadButton > button {
    border: 1px solid #E7BD68 !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #F5D99A !important;
    transform: translateY(-1px);
}

/* Refined section hierarchy */
.section-label {
    margin-top: 1.8rem;
    margin-bottom: 0.45rem;
    color: #E7BD68;
}

[data-testid="stPlotlyChart"],
[data-testid="stDataFrame"] {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Clearer chart text and legends */
.js-plotly-plot .plotly .legend text {
    fill: #CBD5E1 !important;
}

.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text {
    fill: #94A3B8 !important;
}

/* Responsive spacing */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 20px;
        border-radius: 14px;
    }

    .hero-title {
        font-size: 1.75rem;
    }

    .metric-value {
        font-size: 1.35rem;
    }
}

/* ---------- GoldLens header and KPI polish ---------- */

.hero {
    background:
        radial-gradient(ellipse at top right, rgba(231, 189, 104, 0.13), transparent 45%),
        linear-gradient(135deg, #111C2E 0%, #0C1422 70%);
    border: 1px solid #344155;
    border-radius: 18px;
    padding: 30px 32px;
    margin-bottom: 28px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
}

.hero-title {
    color: #F8FAFC;
    font-size: 2.25rem;
    font-weight: 750;
    letter-spacing: -0.035em;
    line-height: 1.15;
    margin-bottom: 10px;
}

.hero-subtitle {
    color: #A8B4C7;
    font-size: 1rem;
    line-height: 1.65;
    max-width: 760px;
}

.metric-card {
    background: linear-gradient(145deg, #141F31, #101827);
    border: 1px solid #2D3B50;
    border-radius: 14px;
    padding: 20px 22px;
    min-height: 112px;
    transition: border-color 0.2s ease, transform 0.2s ease;
}

.metric-card:hover {
    border-color: #B9954D;
    transform: translateY(-2px);
}

.metric-label {
    color: #A8B4C7;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.metric-value {
    color: #F8FAFC;
    font-size: 1.8rem;
    font-weight: 700;
    margin-top: 9px;
    line-height: 1.2;
}

.metric-caption {
    color: #8B9AB0;
    font-size: 0.8rem;
    margin-top: 6px;
}

@media (max-width: 768px) {
    .hero {
        padding: 22px;
    }

    .hero-title {
        font-size: 1.8rem;
    }

    .metric-card {
        padding: 15px;
    }

    .metric-value {
        font-size: 1.4rem;
    }
}

</style>
""", unsafe_allow_html=True)


# ---------- Load data ----------
st.sidebar.markdown(
    '<div class="goldlens-brand">◈ GOLDLENS</div>',
    unsafe_allow_html=True,
)
st.sidebar.caption("COMMODITY INTELLIGENCE")
st.sidebar.divider()

if not NORMALIZED_FILE.exists():
    st.error("normalized_gold.csv is missing. Run normalize_gold.py first.")
    st.stop()

df = pd.read_csv(NORMALIZED_FILE)

required = [
    "Date", "Symbol", "Expiry Date", "Close", "NormalizedPrice10g"
]
missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Required columns missing: {missing}")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], errors="coerce")
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
df["NormalizedPrice10g"] = pd.to_numeric(
    df["NormalizedPrice10g"], errors="coerce"
)

df = df.dropna(
    subset=["Date", "Expiry Date", "Symbol", "NormalizedPrice10g"]
)
df = df[df["NormalizedPrice10g"] > 0]

if df.empty:
    st.error("No valid normalized prices are available.")
    st.stop()

symbols = sorted(df["Symbol"].unique())

selected_symbols = st.sidebar.multiselect(
    "CONTRACTS",
    options=symbols,
    default=symbols,
)

view = df[df["Symbol"].isin(selected_symbols)].copy()

if view.empty:
    st.info("Select at least one contract from the sidebar.")
    st.stop()

latest_date = view["Date"].max()
latest = view[view["Date"] == latest_date].copy()
latest = latest.sort_values(["Symbol", "Expiry Date"])


# ---------- Historical data status ----------

if HISTORY_FILE.exists():
    history_df = pd.read_csv(HISTORY_FILE, low_memory=False)
    history_df["Date"] = pd.to_datetime(
        history_df["Date"], errors="coerce"
    )

    history_dates = history_df["Date"].nunique()
    history_latest = history_df["Date"].max()
else:
    history_df = pd.DataFrame()
    history_dates = 0
    history_latest = pd.NaT

st.sidebar.divider()
st.sidebar.markdown("**DATA STATUS**")
st.sidebar.caption(f"Latest snapshot: {latest_date:%d %b %Y}")
st.sidebar.caption(f"Contracts available: {len(symbols)}")
st.sidebar.caption(f"Trading dates loaded: {history_dates}")

if pd.notna(history_latest):
    st.sidebar.caption(
        f"Historical data through: {history_latest:%d %b %Y}"
    )

st.sidebar.caption("Source: Local MCX bhavcopy CSV")
st.sidebar.divider()
st.sidebar.caption("GoldLens • Research prototype")


# ---------- Header ----------
st.markdown("""
<div class="hero">
    <div class="eyebrow">MCX · BULLION MARKETS · RESEARCH TERMINAL</div>
    <div class="hero-title">GoldLens <span style="color:#E7BD68;">◈</span></div>
    <div class="hero-subtitle">
        Contract intelligence. Relative value. Expiry-aware market analysis.
    </div>
</div>
""", unsafe_allow_html=True)


if history_dates < 30:
    st.warning(
        f"RESEARCH MODE · {history_dates} trading dates available. "
        "Historical performance is not yet validated. "
        "Spread differences are exploratory, not verified trading signals."
    )
else:
    st.info(
        f"RESEARCH MODE · {history_dates} trading dates loaded. "
        "Validate contract quotation conventions and execution costs "
        "before interpreting strategy results."
    )


# ---------- KPI cards ----------
def metric_card(label, value, note):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


k1, k2, k3, k4 = st.columns(4)

with k1:
    metric_card("Market date", latest_date.strftime("%d %b %Y"), "Latest available snapshot")

with k2:
    metric_card("Contracts", str(latest["Symbol"].nunique()), "Selected instruments")

with k3:
    metric_card("Expiry records", str(len(latest)), "Selected contract-expiry rows")

with k4:
    metric_card(
        "History depth",
        str(history_dates),
        "Unique trading dates",
    )

# ---------- Price chart ----------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">01 / Market overview</div>', unsafe_allow_html=True)
st.header("Gold futures curve")
st.caption(
    "Purity-adjusted reference prices per 10g. "
    "The lines represent different contracts and expiries, not a single tradable instrument."
)

chart = px.line(
    latest,
    x="Expiry Date",
    y="NormalizedPrice10g",
    color="Symbol",
    markers=True,
    custom_data=["Close"],
    color_discrete_sequence=["#E7BD68", "#6EA8FE", "#55D6BE", "#C4A7E7"],
    labels={
        "Expiry Date": "Contract expiry",
        "NormalizedPrice10g": "Reference price (₹ / 10g)",
        "Symbol": "Contract",
        "Close": "Raw close",
    },
)

chart.update_traces(
    line=dict(width=2.5),
    marker=dict(size=8),
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Expiry: %{x|%d %b %Y}<br>"
        "Reference price: ₹%{y:,.2f}<br>"
        "Raw close: %{customdata[0]:,.2f}<extra></extra>"
    ),
)

chart.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#CBD5E1"),
    margin=dict(l=15, r=15, t=25, b=15),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    xaxis=dict(showgrid=False, linecolor="#263247"),
    yaxis=dict(
        gridcolor="#263247",
        tickprefix="₹",
        tickformat=",.0f",
    ),
    hoverlabel=dict(bgcolor="#111827", font_color="#F8FAFC"),
)

st.plotly_chart(chart, width="stretch")


# ---------- Contract table ----------
st.markdown('<div class="section-label">02 / Instrument details</div>', unsafe_allow_html=True)
st.header("Contract monitor")

columns = [
    c for c in [
        "Symbol", "Expiry Date", "Close", "QuotedGrams",
        "ContractPurity", "NormalizedPrice10g",
        "Volume(Lots)", "Open Interest(Lots)",
    ] if c in latest.columns
]

table = latest[columns].copy()
table = table.rename(columns={
    "Symbol": "Contract",
    "Expiry Date": "Expiry",
    "Close": "Raw close",
    "QuotedGrams": "Quoted grams",
    "ContractPurity": "Purity",
    "NormalizedPrice10g": "Reference ₹/10g",
    "Volume(Lots)": "Volume (lots)",
    "Open Interest(Lots)": "Open interest",
})

table["Expiry"] = table["Expiry"].dt.strftime("%d %b %Y")

st.dataframe(
    table,
    width="stretch",
    hide_index=True,
    height=420,
    column_config={
        "Reference ₹/10g": st.column_config.NumberColumn(
            "Reference price (₹/10g)",
            format="₹%.2f",
        ),
        "Raw close": st.column_config.NumberColumn(
            "Raw close (₹)",
            format="₹%.2f",
        ),
        "Volume (lots)": st.column_config.NumberColumn(
            "Volume (lots)",
            format="%d",
        ),
        "Open interest": st.column_config.NumberColumn(
            "Open interest (lots)",
            format="%d",
        ),
    },
)

# ---------- Data Quality & Validation ----------
st.markdown(
    '<div class="section-label">03 / DATA INTEGRITY</div>',
    unsafe_allow_html=True,
)
st.header("Data quality & validation")
st.caption(
    "A transparent audit of historical coverage, missing values, "
    "and contract-level data quality."
)

quality_history = pd.read_csv(HISTORY_FILE) if HISTORY_FILE.exists() else pd.DataFrame()
quality_report = pd.read_csv(QUALITY_FILE) if QUALITY_FILE.exists() else pd.DataFrame()

if not quality_history.empty:
    quality_history["Date"] = pd.to_datetime(
        quality_history["Date"], errors="coerce"
    )

    history_dates_quality = quality_history["Date"].nunique()
    history_rows_quality = len(quality_history)

    duplicate_count = (
        quality_history.duplicated(
            subset=["Date", "Symbol", "Expiry Date"]
        ).sum()
        if all(c in quality_history.columns for c in ["Date", "Symbol", "Expiry Date"])
        else None
    )

    missing_closes = (
        pd.to_numeric(quality_history["Close"], errors="coerce").isna().sum()
        if "Close" in quality_history.columns
        else None
    )

    q1, q2, q3, q4 = st.columns(4)

    q1.metric("Historical rows", f"{history_rows_quality:,}")
    q2.metric("Trading dates", history_dates_quality)
    q3.metric(
        "Missing closes",
        "N/A" if missing_closes is None else f"{missing_closes:,}",
    )
    q4.metric(
        "Duplicate records",
        "N/A" if duplicate_count is None else f"{duplicate_count:,}",
    )

    if history_dates_quality < 30:
        st.warning(
            f"Research limitation: {history_dates_quality} trading dates "
            "are available. This is enough to test the data pipeline, "
            "but not to establish reliable strategy performance."
        )

    if duplicate_count == 0 and missing_closes == 0:
        st.success(
            "Basic checks passed: no duplicate date-symbol-expiry records "
            "or missing closing prices were detected."
        )

    st.markdown("#### Contract coverage")

    coverage = (
        quality_history.groupby("Symbol")
        .agg(
            Rows=("Symbol", "size"),
            TradingDates=("Date", "nunique"),
        )
        .reset_index()
        .rename(columns={
            "Symbol": "Contract",
            "Rows": "Records",
            "TradingDates": "Trading dates",
        })
    )

    st.dataframe(coverage, hide_index=True, width="stretch")

else:
    st.warning(
        "Historical dataset is unavailable or empty. "
        "Run historical_data.py before reviewing data quality."
    )

if not quality_report.empty:
    st.markdown("#### Detailed audit by contract")
    st.dataframe(
        quality_report,
        hide_index=True,
        width="stretch",
    )
else:
    st.info(
        "Detailed contract audit not found. Run "
        "`python data_quality.py` to generate it."
    )


# ---------- Spread analysis ----------

# ---------- Relative-value analysis ----------
st.markdown(
    '<div class="section-label">03 / RELATIVE VALUE</div>',
    unsafe_allow_html=True,
)
st.header("Cross-contract spread monitor")
st.caption(
    "Compare normalized prices for contracts sharing the same observation "
    "date and expiry. A large difference is a research lead, not a trade signal."
)

if SPREAD_FILE.exists():
    spreads = pd.read_csv(SPREAD_FILE)

    required_spread_cols = [
        "Date", "Expiry Date", "ContractA", "ContractB",
        "PriceA", "PriceB", "Spread_Rs_per_10g",
        "Spread_Percent_of_Mid",
    ]
    missing_spread_cols = [
        c for c in required_spread_cols if c not in spreads.columns
    ]

    if missing_spread_cols:
        st.error(
            "The spread file is missing required columns: "
            + ", ".join(missing_spread_cols)
            + ". Rerun spread_analysis.py."
        )
    elif spreads.empty:
        st.info("No same-expiry comparisons are available.")
    else:
        spreads["Date"] = pd.to_datetime(
            spreads["Date"], errors="coerce"
        )
        spreads["Expiry Date"] = pd.to_datetime(
            spreads["Expiry Date"], errors="coerce"
        )

        numeric_cols = [
            "PriceA", "PriceB", "Spread_Rs_per_10g",
            "Spread_Percent_of_Mid",
        ]
        for col in numeric_cols:
            spreads[col] = pd.to_numeric(
                spreads[col], errors="coerce"
            )

        spreads = spreads.dropna(
            subset=[
                "Date", "Expiry Date", "PriceA", "PriceB",
                "Spread_Rs_per_10g", "Spread_Percent_of_Mid",
            ]
        )

        spreads = spreads[
            spreads["ContractA"].isin(selected_symbols)
            & spreads["ContractB"].isin(selected_symbols)
        ].copy()

        if spreads.empty:
            st.info(
                "No eligible same-expiry pairs for the selected contracts."
            )
        else:
            # Positive/negative shows direction; absolute spread ranks size.
            spreads["AbsoluteSpreadPercent"] = (
                spreads["Spread_Percent_of_Mid"].abs()
            )
            spreads["ContractPair"] = (
                spreads["ContractA"] + " vs " + spreads["ContractB"]
            )
            spreads = spreads.sort_values(
                "AbsoluteSpreadPercent", ascending=False
            ).reset_index(drop=True)

            # This is a data-review status, not a buy/sell recommendation.
            spreads["ReviewStatus"] = "Investigate"
            spreads["ReviewNote"] = (
                "Historical anomaly not established"
            )

            top = spreads.iloc[0]
            a, b, c = st.columns(3)

            with a:
                metric_card(
                    "Largest observed gap",
                    f"{top['AbsoluteSpreadPercent']:.3f}%",
                    "Absolute spread in this snapshot",
                )

            with b:
                metric_card(
                    "Contract pair",
                    str(top["ContractPair"]),
                    f"Expiry: {top['Expiry Date']:%d %b %Y}",
                )

            with c:
                metric_card(
                    "Price difference",
                    f"₹{abs(top['Spread_Rs_per_10g']):,.2f}",
                    "Per 10g reference basis",
                )

            st.markdown("#### Spread ranking")
            st.caption(
                "Ranked by absolute percentage difference. "
                "The sign is retained in the detailed table."
            )

            ranking = px.bar(
                spreads,
                x="ContractPair",
                y="AbsoluteSpreadPercent",
                color="ContractPair",
                hover_data={
                    "Expiry Date": True,
                    "Spread_Percent_of_Mid": ":.4f",
                    "Spread_Rs_per_10g": ":,.2f",
                    "AbsoluteSpreadPercent": ":.4f",
                },
                color_discrete_sequence=[
                    "#E7BD68", "#6EA8FE", "#55D6BE",
                    "#C4A7E7", "#E89A78", "#8BC5D6",
                ],
                labels={
                    "ContractPair": "Contract pair",
                    "AbsoluteSpreadPercent": "Absolute spread (%)",
                    "Spread_Percent_of_Mid": "Signed spread (%)",
                    "Spread_Rs_per_10g": "Signed difference (₹ / 10g)",
                },
            )

            ranking.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="DM Sans, sans-serif",
                    color="#CBD5E1",
                ),
                showlegend=False,
                margin=dict(l=15, r=15, t=25, b=55),
                xaxis=dict(
                    showgrid=False,
                    tickangle=-20,
                ),
                yaxis=dict(
                    gridcolor="#263247",
                    ticksuffix="%",
                    rangemode="tozero",
                ),
            )
            st.plotly_chart(ranking, use_container_width=True)

            st.markdown("#### Pair-by-pair details")

            display = spreads[
                [
                    "Date", "Expiry Date", "ContractA", "ContractB",
                    "PriceA", "PriceB", "Spread_Rs_per_10g",
                    "Spread_Percent_of_Mid", "ReviewStatus", "ReviewNote",
                ]
            ].rename(columns={
                "Date": "Observation date",
                "Expiry Date": "Shared expiry",
                "ContractA": "Contract A",
                "ContractB": "Contract B",
                "PriceA": "Price A (₹/10g)",
                "PriceB": "Price B (₹/10g)",
                "Spread_Rs_per_10g": "A − B (₹/10g)",
                "Spread_Percent_of_Mid": "Signed spread (%)",
                "ReviewStatus": "Status",
                "ReviewNote": "Interpretation",
            })

            display["Observation date"] = (
                display["Observation date"].dt.strftime("%d %b %Y")
            )
            display["Shared expiry"] = (
                display["Shared expiry"].dt.strftime("%d %b %Y")
            )

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )

            st.info(
                "Interpretation: positive A − B means Contract A has the "
                "higher normalized reference price; negative means it has "
                "the lower price. These are cross-contract price differences, "
                "not verified arbitrage opportunities. Quote conventions, "
                "purity, liquidity, costs, and historical behavior must be "
                "validated before any strategy evaluation."
            )
else:
    st.info(
        "Spread data is not available. Run python spread_analysis.py "
        "from the backend folder first."
    )

# ---------- Historical anomaly detection ----------
st.markdown(
    '<div class="section-label">04 / STATISTICAL SURVEILLANCE</div>',
    unsafe_allow_html=True,
)
st.header("Historical spread anomalies")
st.caption(
    "Rolling 20-observation baseline; requires at least 15 prior observations "
    "for the same contract pair and expiry. Today's observation is excluded "
    "from its own baseline."
)

ANOMALY_FILE = DATA_DIR / "spread_anomalies.csv"

if not ANOMALY_FILE.exists():
    st.info("Run python anomaly_analysis.py to generate anomaly results.")
else:
    anomalies = pd.read_csv(ANOMALY_FILE)

    if anomalies.empty:
        st.info("No same-expiry pair observations are available.")
    else:
        anomalies["Date"] = pd.to_datetime(
            anomalies["Date"], errors="coerce"
        )
        anomalies["Expiry Date"] = pd.to_datetime(
            anomalies["Expiry Date"], errors="coerce"
        )

        anomalies = anomalies[
            anomalies["ContractA"].isin(selected_symbols)
            & anomalies["ContractB"].isin(selected_symbols)
        ].copy()

        if anomalies.empty:
            st.info("No anomaly records match the selected contracts.")
        else:
            latest_anomalies = anomalies[
                anomalies["Date"] == anomalies["Date"].max()
            ].copy()

            enough_history = (
                pd.to_numeric(
                    latest_anomalies["HistoryCount"], errors="coerce"
                ).fillna(0) >= 15
            )
            flagged = latest_anomalies[
                latest_anomalies["Status"] == "Investigate anomaly"
            ]

            a, b, c = st.columns(3)

            with a:
                metric_card(
                    "Pairs evaluated",
                    str(len(latest_anomalies)),
                    "Latest observation date",
                )

            with b:
                metric_card(
                    "History ready",
                    f"{int(enough_history.sum())}/{len(latest_anomalies)}",
                    "Pairs with sufficient baseline",
                )

            with c:
                metric_card(
                    "Flagged for review",
                    str(len(flagged)),
                    "Statistical alerts, not trade signals",
                )

            if not enough_history.any():
                st.warning(
                    "INSUFFICIENT HISTORY — GoldLens needs at least 15 prior "
                    "same-expiry observations per pair before calculating "
                    "a historical z-score. Current flags are not available."
                )
            elif not flagged.empty:
                st.warning(
                    "Potential statistical anomalies detected. Validate "
                    "quotes, contract terms, liquidity and transaction costs."
                )
            else:
                st.success(
                    "No spreads crossed the configured statistical threshold "
                    "among pairs with sufficient history."
                )

            display_cols = [
                "Date", "Expiry Date", "ContractA", "ContractB",
                "SpreadPercent", "HistoricalMean", "ZScore",
                "HistoryCount", "Status",
            ]
            display_cols = [
                c for c in display_cols if c in latest_anomalies.columns
            ]

            display = latest_anomalies[display_cols].copy()
            display = display.rename(columns={
                "Date": "Observation date",
                "Expiry Date": "Shared expiry",
                "ContractA": "Contract A",
                "ContractB": "Contract B",
                "SpreadPercent": "Current spread (%)",
                "HistoricalMean": "Prior mean (%)",
                "ZScore": "Z-score",
                "HistoryCount": "Prior observations",
                "Status": "Review status",
            })

            for col in ["Observation date", "Shared expiry"]:
                if col in display.columns:
                    display[col] = pd.to_datetime(
                        display[col], errors="coerce"
                    ).dt.strftime("%d %b %Y")

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "A z-score measures how far the current spread is from its "
                "historical mean in standard-deviation units. The 2.0 "
                "threshold is a configurable research heuristic, not a "
                "validated trading rule."
            )

# ---------- Term structure analysis ----------
st.markdown(
    '<div class="section-label">05 / TERM STRUCTURE</div>',
    unsafe_allow_html=True,
)
st.header("Gold futures term structure")
st.caption(
    "Compare normalized prices across expiry dates within each contract. "
    "Calendar spreads are descriptive, not trading signals."
)

TERM_FILE = DATA_DIR / "term_structure.csv"

if not TERM_FILE.exists():
    st.info("Run python term_structure.py to generate term-structure data.")
else:
    term = pd.read_csv(TERM_FILE)

    if term.empty:
        st.info("No adjacent-expiry comparisons are available.")
    else:
        term["Date"] = pd.to_datetime(term["Date"], errors="coerce")
        term["NearExpiry"] = pd.to_datetime(
            term["NearExpiry"], errors="coerce"
        )
        term["FarExpiry"] = pd.to_datetime(
            term["FarExpiry"], errors="coerce"
        )

        for col in [
            "NearPrice10g", "FarPrice10g",
            "CalendarSpreadRsPer10g", "CalendarSpreadPercent",
        ]:
            term[col] = pd.to_numeric(term[col], errors="coerce")

        term = term[
            term["Symbol"].isin(selected_symbols)
        ].dropna(
            subset=[
                "Date", "NearExpiry", "FarExpiry",
                "NearPrice10g", "FarPrice10g",
            ]
        ).copy()

        if term.empty:
            st.info("No term-structure data for the selected contracts.")
        else:
            latest_term_date = term["Date"].max()
            latest_term = term[
                term["Date"] == latest_term_date
            ].copy()

            st.markdown("#### Price curve by contract")

            curve_data = latest_term.melt(
                id_vars=["Symbol", "NearExpiry", "FarExpiry"],
                value_vars=["NearPrice10g", "FarPrice10g"],
                var_name="PriceType",
                value_name="ReferencePrice",
            )

            curve_data["Expiry"] = curve_data.apply(
                lambda row: (
                    row["NearExpiry"]
                    if row["PriceType"] == "NearPrice10g"
                    else row["FarExpiry"]
                ),
                axis=1,
            )
            curve_data = curve_data.drop_duplicates(
                subset=["Symbol", "Expiry", "ReferencePrice"]
            )

            # Build a unique expiry-price series per contract.
            near_points = latest_term[
                ["Symbol", "NearExpiry", "NearPrice10g"]
            ].rename(columns={
                "NearExpiry": "Expiry",
                "NearPrice10g": "ReferencePrice",
            })
            far_points = latest_term[
                ["Symbol", "FarExpiry", "FarPrice10g"]
            ].rename(columns={
                "FarExpiry": "Expiry",
                "FarPrice10g": "ReferencePrice",
            })

            curve_data = pd.concat(
                [near_points, far_points], ignore_index=True
            ).drop_duplicates(
                subset=["Symbol", "Expiry"], keep="last"
            ).sort_values(["Symbol", "Expiry"])

            curve = px.line(
                curve_data,
                x="Expiry",
                y="ReferencePrice",
                color="Symbol",
                markers=True,
                color_discrete_sequence=[
                    "#E7BD68", "#6EA8FE", "#55D6BE", "#C4A7E7"
                ],
                labels={
                    "Expiry": "Contract expiry",
                    "ReferencePrice": "Normalized reference price (₹ / 10g)",
                    "Symbol": "Contract",
                },
            )
            curve.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", color="#CBD5E1"),
                margin=dict(l=15, r=15, t=20, b=15),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#263247", tickprefix="₹"),
                legend=dict(orientation="h", y=1.12, x=0),
            )
            st.plotly_chart(curve, use_container_width=True)

            st.markdown("#### Adjacent-expiry calendar spreads")

            spread_curve = px.bar(
                latest_term,
                x="NearExpiry",
                y="CalendarSpreadPercent",
                color="Symbol",
                barmode="group",
                hover_data=[
                    "FarExpiry",
                    "CalendarSpreadRsPer10g",
                    "DaysBetweenExpiries",
                    "CurveShape",
                ],
                color_discrete_sequence=[
                    "#E7BD68", "#6EA8FE", "#55D6BE", "#C4A7E7"
                ],
                labels={
                    "NearExpiry": "Near expiry",
                    "CalendarSpreadPercent": "Spread (%)",
                    "Symbol": "Contract",
                    "FarExpiry": "Far expiry",
                    "CalendarSpreadRsPer10g": "Spread (₹ / 10g)",
                    "DaysBetweenExpiries": "Days between expiries",
                    "CurveShape": "Curve shape",
                },
            )
            spread_curve.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", color="#CBD5E1"),
                margin=dict(l=15, r=15, t=20, b=15),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#263247", ticksuffix="%"),
                legend=dict(orientation="h", y=1.12, x=0),
            )
            spread_curve.add_hline(
                y=0, line_dash="dash", line_color="#94A3B8"
            )
            st.plotly_chart(spread_curve, use_container_width=True)

            st.markdown("#### Expiry-pair details")

            term_table = latest_term[[
                "Symbol", "NearExpiry", "FarExpiry",
                "DaysBetweenExpiries", "NearPrice10g", "FarPrice10g",
                "CalendarSpreadRsPer10g", "CalendarSpreadPercent",
                "CurveShape",
            ]].rename(columns={
                "Symbol": "Contract",
                "NearExpiry": "Near expiry",
                "FarExpiry": "Far expiry",
                "DaysBetweenExpiries": "Days apart",
                "NearPrice10g": "Near price (₹/10g)",
                "FarPrice10g": "Far price (₹/10g)",
                "CalendarSpreadRsPer10g": "Spread (₹/10g)",
                "CalendarSpreadPercent": "Spread (%)",
                "CurveShape": "Curve shape",
            })

            term_table["Near expiry"] = term_table[
                "Near expiry"
            ].dt.strftime("%d %b %Y")
            term_table["Far expiry"] = term_table[
                "Far expiry"
            ].dt.strftime("%d %b %Y")

            st.dataframe(
                term_table,
                use_container_width=True,
                hide_index=True,
            )

            st.info(
                "This is a term-structure snapshot for the latest available "
                "date. Historical roll-down returns and strategy performance "
                "require multiple trading dates and realistic costs."
            )

# ---------- Backtesting & Strategy Evaluation ----------
st.markdown(
    '<div class="section-label">06 / STRATEGY EVALUATION</div>',
    unsafe_allow_html=True,
)
st.header("Backtesting & strategy evaluation")
st.caption(
    "Evaluate historical spread behavior with transparent assumptions. "
    "Results remain preliminary until sufficient historical data is available."
)

BACKTEST_REPORT = DATA_DIR / "backtest_report.csv"
BACKTEST_TRADES = DATA_DIR / "backtest_trades.csv"

if not BACKTEST_REPORT.exists():
    st.info("Backtest report not found. Run `python backtest.py` first.")
else:
    report_df = pd.read_csv(BACKTEST_REPORT)

    if report_df.empty:
        st.warning("The backtest report is empty.")
    else:
        report = report_df.iloc[0]

        status = str(report.get("Status", "Unknown"))
        trading_dates = int(report.get("TradingDates", 0))
        pair_observations = int(report.get("PairObservations", 0))
        completed_trades = int(report.get("CompletedTrades", 0))


        st.markdown("#### Research status")

        metric_cols = st.columns(3, gap="medium")

        with metric_cols[0]:
            st.metric(
                label="Trading dates",
                value=f"{trading_dates:,}",
                help="Number of distinct trading dates in the backtest.",
            )

        with metric_cols[1]:
            st.metric(
                label="Pair observations",
                value=f"{pair_observations:,}",
                help="Available observations for the evaluated contract pairs.",
            )

        with metric_cols[2]:
            st.metric(
                label="Completed trades",
                value=f"{completed_trades:,}",
                help="Trades completed under the configured research rules.",
            )

        if trading_dates < 30:
            st.warning(
                f"Status: {status}. Only {trading_dates} trading date(s) "
                "are available. Historical performance cannot be validated."
            )
        else:
            st.info(f"Research status: {status}")

        st.markdown("#### Strategy configuration")

        config_cols = st.columns(3)
        config_cols[0].metric(
            "Entry threshold",
            f"{report.get('EntryZThreshold', 2.0):.1f} Z"
            if pd.notna(report.get("EntryZThreshold", 2.0))
            else "N/A",
        )
        config_cols[1].metric(
            "Exit threshold",
            f"{report.get('ExitZThreshold', 0.5):.1f} Z"
            if pd.notna(report.get("ExitZThreshold", 0.5))
            else "N/A",
        )
        config_cols[2].metric(
            "Illustrative cost",
            f"{report.get('IllustrativeCostBpsPerLeg', 10):.1f} bps/leg"
            if pd.notna(report.get("IllustrativeCostBpsPerLeg", 10))
            else "N/A",
        )

        # Display performance metrics only when trades exist.
        if completed_trades > 0 and "MeanNetProxyPercent" in report.index:
            st.markdown("#### Exploratory trade statistics")
            result_cols = st.columns(3)

            result_cols[0].metric(
                "Mean net spread-move proxy",
                f"{report['MeanNetProxyPercent']:.3f}%"
            )
            result_cols[1].metric(
                "Median net spread-move proxy",
                f"{report['MedianNetProxyPercent']:.3f}%"
            )
            result_cols[2].metric(
                "Positive proxy trades",
                f"{int(report.get('PositiveProxyTrades', 0))}"
            )
        if BACKTEST_TRADES.exists():
            if BACKTEST_TRADES.stat().st_size == 0:
                st.info(
                    "No completed trades are available yet. "
                    "Run the backtest again after adding historical data."
                )
            else:
                try:
                    trades_df = pd.read_csv(BACKTEST_TRADES)

                    st.markdown("#### Trade log")

                    if trades_df.empty:
                        st.info(
                            "No completed trades are available yet. "
                            "This is expected with limited historical data."
                        )
                    else:
                        st.dataframe(
                            trades_df,
                            width="stretch",
                            hide_index=True,
                            height=350,
                        )

                        st.download_button(
                            "Download trade log",
                            data=trades_df.to_csv(index=False).encode("utf-8"),
                            file_name="goldlens_backtest_trades.csv",
                            mime="text/csv",
                        )
                        st.subheader("Open Positions")

                        if OPEN_POSITIONS_FILE.exists():
                            open_positions = pd.read_csv(OPEN_POSITIONS_FILE)

                            st.metric("Open Positions", len(open_positions))

                            if not open_positions.empty:
                                st.dataframe(
                                    open_positions,
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            else:
                                st.success(
                                     "No open positions at the end of available history."
                                )
                        else:
                            st.info("Open positions file is not available yet.")

                except pd.errors.EmptyDataError:
                    st.info(
                        "The trade log is empty because no trades have "
                        "been completed. No historical performance is "
                        "available yet."
                    )
            st.markdown("#### Research methodology")

            method_col1, method_col2 = st.columns(2)

            with method_col1:
                st.markdown("**What GoldLens evaluates**")
                st.write(
                    "- Purity-adjusted reference prices across gold contracts.\n"
                    "- Relative-value differences for matched expiries.\n"
                    "- Term structure across consecutive expiries.\n"
                    "- Historical spread deviations when sufficient data is available."
                )

            with method_col2:
                st.markdown("**Research safeguards**")
                st.write(
                    "- Signals require sufficient prior observations.\n"
                    "- Transaction costs are explicitly configurable.\n"
                    "- Incomplete history is reported rather than inferred.\n"
                    "- Statistical alerts are not buy/sell recommendations."
                )
            st.warning(
                f"DATA LIMITATION — The current dataset contains {history_dates} "
                "trading dates. Historical anomalies and strategy performance "
                "are not validated. Additional MCX trading history and realistic "
                "execution assumptions are required before drawing performance conclusions."
            )


            st.download_button(
                "Download backtest report",
                data=report_df.to_csv(index=False).encode("utf-8"),
                file_name="goldlens_backtest_report.csv",
                mime="text/csv",
            )

# ---------- Footer ----------
st.divider()
st.markdown("""
<div style="text-align:center; padding:10px 0 18px 0;">
    <div style="color:#E7BD68; font-weight:700; letter-spacing:2px;">
        ◈ GOLDLENS
    </div>
    <div style="color:#64748B; font-size:0.78rem; margin-top:5px;">
        Commodity Derivatives Intelligence · Hackathon Research Prototype
    </div>
</div>
""", unsafe_allow_html=True)
