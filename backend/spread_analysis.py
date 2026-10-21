
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "normalized_gold.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "gold_spreads.csv"

df = pd.read_csv(INPUT_FILE)
print("\n--- RAW DATA CHECK ---")
print("Columns:", df.columns.tolist())
print("\nFirst 5 dates:")
print(df["Date"].head().to_list())
print("\nFirst 5 expiry dates:")
print(df["Expiry Date"].head().to_list())
print("\nRaw row count:", len(df))

# Parse dates consistently before matching contracts.
df["Date"] = pd.to_datetime(
    df["Date"], errors="coerce"
)

df["Expiry Date"] = pd.to_datetime(
    df["Expiry Date"], errors="coerce"
)
df["NormalizedPrice10g"] = pd.to_numeric(
    df["NormalizedPrice10g"], errors="coerce"
)

# Keep usable prices only.
df = df.dropna(
    subset=["Date", "Expiry Date", "Symbol", "NormalizedPrice10g"]
)
df = df[df["NormalizedPrice10g"] > 0]

# Keep one observation per contract, date, and expiry.
df = df.drop_duplicates(
    subset=["Date", "Symbol", "Expiry Date"], keep="last"
)
print("\n--- MATCHING DIAGNOSTICS ---")
print("Rows after cleaning:", len(df))
print("Trading dates:", df["Date"].nunique())
print("Contracts:", sorted(df["Symbol"].unique()))

expiry_counts = (
    df.groupby(["Date", "Expiry Date"])["Symbol"]
    .nunique()
)

print("Date-expiry groups with 2+ contracts:",
      (expiry_counts >= 2).sum())

print("\nContract counts per date-expiry:")
print(expiry_counts.value_counts().sort_index())

# Match contracts traded on the same date with the same expiry.
left = df.rename(
    columns={
        "Symbol": "ContractA",
        "NormalizedPrice10g": "PriceA",
    }
)
right = df.rename(
    columns={
        "Symbol": "ContractB",
        "NormalizedPrice10g": "PriceB",
    }
)

pairs = left.merge(
    right,
    on=["Date", "Expiry Date"],
    suffixes=("_A", "_B"),
)

# Remove self-comparisons and duplicate pair directions.
pairs = pairs[pairs["ContractA"] < pairs["ContractB"]].copy()

if pairs.empty:
    print("No same-expiry cross-contract pairs were found.")
    print("This is a valid result; we will not compare mismatched expiries.")
else:
    pairs["Spread_Rs_per_10g"] = pairs["PriceA"] - pairs["PriceB"]
    pairs["Spread_Percent_of_Mid"] = (
        pairs["Spread_Rs_per_10g"]
        / ((pairs["PriceA"] + pairs["PriceB"]) / 2)
        * 100
    )

    pairs = pairs[
        [
            "Date",
            "Expiry Date",
            "ContractA",
            "ContractB",
            "PriceA",
            "PriceB",
            "Spread_Rs_per_10g",
            "Spread_Percent_of_Mid",
        ]
    ].sort_values(["Date", "Expiry Date", "ContractA", "ContractB"])

    pairs.to_csv(OUTPUT_FILE, index=False)

    print("\nSame-expiry cross-contract comparisons:")
    print(pairs.to_string(index=False))
    print(f"\nSaved to: {OUTPUT_FILE}")

print(
    "\nNote: A spread is a comparison, not a trading signal. "
    "Validate contract specifications, liquidity, costs, and historical behavior."
)
