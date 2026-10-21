
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "gold_spreads.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "spread_anomalies.csv"

WINDOW = 20
MIN_HISTORY = 15
Z_THRESHOLD = 2.0

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Missing {INPUT_FILE}. Run spread_analysis.py first."
    )

df = pd.read_csv(INPUT_FILE)

required = [
    "Date",
    "Expiry Date",
    "ContractA",
    "ContractB",
    "PriceA",
    "PriceB",
    "Spread_Percent_of_Mid",
]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], errors="coerce")
df["Spread_Percent_of_Mid"] = pd.to_numeric(
    df["Spread_Percent_of_Mid"], errors="coerce"
)

df = df.dropna(
    subset=[
        "Date", "Expiry Date", "ContractA",
        "ContractB", "Spread_Percent_of_Mid",
    ]
)

df = df.drop_duplicates(
    subset=["Date", "Expiry Date", "ContractA", "ContractB"],
    keep="last",
)

df = df.sort_values(
    ["ContractA", "ContractB", "Expiry Date", "Date"]
).reset_index(drop=True)

group_cols = ["ContractA", "ContractB", "Expiry Date"]
grouped = df.groupby(group_cols, sort=False)["Spread_Percent_of_Mid"]

# Today's spread is excluded from its own historical baseline.
df["HistoricalMean"] = grouped.transform(
    lambda s: s.shift(1).rolling(
        WINDOW, min_periods=MIN_HISTORY
    ).mean()
)

df["HistoricalStd"] = grouped.transform(
    lambda s: s.shift(1).rolling(
        WINDOW, min_periods=MIN_HISTORY
    ).std()
)

df["HistoryCount"] = grouped.transform(
    lambda s: s.shift(1).rolling(
        WINDOW, min_periods=1
    ).count()
).fillna(0).astype(int)

valid_baseline = (
    (df["HistoryCount"] >= MIN_HISTORY)
    & df["HistoricalStd"].notna()
    & (df["HistoricalStd"] > 0)
)

df["ZScore"] = np.nan
df.loc[valid_baseline, "ZScore"] = (
    df.loc[valid_baseline, "Spread_Percent_of_Mid"]
    - df.loc[valid_baseline, "HistoricalMean"]
) / df.loc[valid_baseline, "HistoricalStd"]

df["Status"] = "Insufficient history"
df.loc[valid_baseline, "Status"] = "Within historical range"
df.loc[
    valid_baseline & (df["ZScore"].abs() >= Z_THRESHOLD),
    "Status",
] = "Investigate anomaly"

result = df.rename(
    columns={"Spread_Percent_of_Mid": "SpreadPercent"}
)[[
    "Date", "Expiry Date", "ContractA", "ContractB",
    "PriceA", "PriceB", "SpreadPercent", "HistoricalMean",
    "HistoricalStd", "ZScore", "HistoryCount", "Status",
]].copy()

result.to_csv(OUTPUT_FILE, index=False)

print("\nGOLDLENS — HISTORICAL SPREAD ANOMALY CHECK")
print("=" * 60)
print(f"Input trading dates: {df['Date'].nunique()}")
print(f"Same-expiry pair observations: {len(result)}")
print(f"Historical window: {WINDOW} observations")
print(f"Minimum prior observations: {MIN_HISTORY}")
print(f"Investigation threshold: |Z-score| >= {Z_THRESHOLD}")

if result.empty:
    print("No same-expiry contract pairs found.")
else:
    latest_date = result["Date"].max()
    latest = result[result["Date"] == latest_date]

    print(f"\nLatest observation date: {latest_date:%d %b %Y}")
    print(latest[[
        "ContractA", "ContractB", "Expiry Date",
        "SpreadPercent", "HistoryCount", "ZScore", "Status",
    ]].to_string(index=False))

    print("\nStatus counts:")
    print(result["Status"].value_counts().to_string())

print(f"\nSaved: {OUTPUT_FILE}")
print(
    "\nResearch limitation: an anomaly flag is a statistical alert, "
    "not proof of mispricing or a profitable trading opportunity."
)
