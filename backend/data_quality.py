
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "normalized_gold.csv"
OUTPUT_FILE = DATA_DIR / "data_quality_report.csv"
SUMMARY_FILE = DATA_DIR / "data_quality_summary.csv"

TARGET_SYMBOLS = {
    "GOLDM",
    "GOLDTEN",
    "GOLDGUINEA",
    "GOLDPETAL",
}

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Missing input file: {INPUT_FILE}\n"
        "Run python normalize_gold.py first."
    )

df = pd.read_csv(INPUT_FILE)

required = [
    "Date",
    "Symbol",
    "Expiry Date",
    "Close",
    "NormalizedPrice10g",
]

missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Standardize values and types.
df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Expiry Date"] = pd.to_datetime(
    df["Expiry Date"], errors="coerce"
)
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
df["NormalizedPrice10g"] = pd.to_numeric(
    df["NormalizedPrice10g"], errors="coerce"
)

# Identify duplicates without deleting any source records.
duplicate_key = ["Date", "Symbol", "Expiry Date"]
duplicate_mask = df.duplicated(duplicate_key, keep=False)

# Build one row per symbol.
rows = []

for symbol in sorted(TARGET_SYMBOLS | set(df["Symbol"].dropna())):
    part = df[df["Symbol"] == symbol].copy()

    rows.append({
        "Symbol": symbol,
        "Rows": len(part),
        "TradingDates": part["Date"].nunique(),
        "Expiries": part["Expiry Date"].nunique(),
        "MissingDate": int(part["Date"].isna().sum()),
        "MissingExpiry": int(part["Expiry Date"].isna().sum()),
        "MissingClose": int(part["Close"].isna().sum()),
        "NonPositiveClose": int(
            (part["Close"].notna() & (part["Close"] <= 0)).sum()
        ),
        "MissingNormalizedPrice": int(
            part["NormalizedPrice10g"].isna().sum()
        ),
        "NonPositiveNormalizedPrice": int(
            (
                part["NormalizedPrice10g"].notna()
                & (part["NormalizedPrice10g"] <= 0)
            ).sum()
        ),
        "DuplicateKeyRows": int(
            duplicate_mask.loc[part.index].sum()
        ),
        "MinNormalizedPrice": part["NormalizedPrice10g"].min(),
        "MaxNormalizedPrice": part["NormalizedPrice10g"].max(),
        "AvgNormalizedPrice": part["NormalizedPrice10g"].mean(),
    })

report = pd.DataFrame(rows)

# Add volume and open-interest averages when available.
for column, output_name in [
    ("Volume(Lots)", "AvgVolumeLots"),
    ("Open Interest(Lots)", "AvgOpenInterestLots"),
]:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        averages = df.groupby("Symbol")[column].mean()
        report[output_name] = report["Symbol"].map(averages)

report = report.round(2)
report.to_csv(OUTPUT_FILE, index=False)

# Overall summary.
valid_dates = df["Date"].dropna()
all_dates = sorted(valid_dates.dt.strftime("%Y-%m-%d").unique())
symbols_found = sorted(df["Symbol"].dropna().unique())

summary = pd.DataFrame([
    {"Metric": "Input rows", "Value": len(df)},
    {"Metric": "Unique trading dates", "Value": df["Date"].nunique()},
    {
        "Metric": "First trading date",
        "Value": all_dates[0] if all_dates else "None",
    },
    {
        "Metric": "Last trading date",
        "Value": all_dates[-1] if all_dates else "None",
    },
    {"Metric": "Symbols found", "Value": len(symbols_found)},
    {
        "Metric": "Missing target symbols",
        "Value": ", ".join(sorted(TARGET_SYMBOLS - set(symbols_found)))
        or "None",
    },
    {"Metric": "Invalid dates", "Value": int(df["Date"].isna().sum())},
    {
        "Metric": "Invalid expiries",
        "Value": int(df["Expiry Date"].isna().sum()),
    },
    {
        "Metric": "Missing close prices",
        "Value": int(df["Close"].isna().sum()),
    },
    {
        "Metric": "Non-positive close prices",
        "Value": int((df["Close"].notna() & (df["Close"] <= 0)).sum()),
    },
    {
        "Metric": "Missing normalized prices",
        "Value": int(df["NormalizedPrice10g"].isna().sum()),
    },
    {
        "Metric": "Duplicate date-symbol-expiry rows",
        "Value": int(duplicate_mask.sum()),
    },
])

summary.to_csv(SUMMARY_FILE, index=False)

print("\nGOLDLENS — DATA QUALITY REPORT")
print("=" * 75)
print(report.to_string(index=False))

print("\nOVERALL SUMMARY")
print("=" * 75)
print(summary.to_string(index=False))

print(f"\nContract report saved: {OUTPUT_FILE}")
print(f"Overall summary saved: {SUMMARY_FILE}")

if df["Date"].nunique() < 30:
    print(
        "\nRESEARCH LIMITATION: Fewer than 30 trading dates are available. "
        "Treat signals and backtest results as exploratory."
    )
