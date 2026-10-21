
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "normalized_gold.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "term_structure.csv"

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "normalized_gold.csv not found. Run python normalize_gold.py first."
    )

df = pd.read_csv(INPUT_FILE)

required = ["Date", "Symbol", "Expiry Date", "NormalizedPrice10g"]
missing = [column for column in required if column not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], errors="coerce")
df["NormalizedPrice10g"] = pd.to_numeric(
    df["NormalizedPrice10g"], errors="coerce"
)

df = df.dropna(
    subset=["Date", "Symbol", "Expiry Date", "NormalizedPrice10g"]
)
df = df[df["NormalizedPrice10g"] > 0]

# Remove duplicate observations for the same contract and expiry.
df = df.drop_duplicates(
    subset=["Date", "Symbol", "Expiry Date"], keep="last"
)

results = []

# Analyze each contract separately to avoid mixing contract specifications.
for (date, symbol), group in df.groupby(["Date", "Symbol"]):
    group = group.sort_values("Expiry Date").reset_index(drop=True)

    for i in range(len(group) - 1):
        near = group.iloc[i]
        far = group.iloc[i + 1]

        near_price = near["NormalizedPrice10g"]
        far_price = far["NormalizedPrice10g"]
        price_difference = far_price - near_price

        results.append({
            "Date": date,
            "Symbol": symbol,
            "NearExpiry": near["Expiry Date"],
            "FarExpiry": far["Expiry Date"],
            "DaysBetweenExpiries": (
                far["Expiry Date"] - near["Expiry Date"]
            ).days,
            "NearPrice10g": near_price,
            "FarPrice10g": far_price,
            "CalendarSpreadRsPer10g": price_difference,
            "CalendarSpreadPercent": (
                price_difference / near_price * 100
            ),
            "CurveShape": (
                "Upward"
                if price_difference > 0
                else "Downward"
                if price_difference < 0
                else "Flat"
            ),
        })

columns = [
    "Date", "Symbol", "NearExpiry", "FarExpiry",
    "DaysBetweenExpiries", "NearPrice10g", "FarPrice10g",
    "CalendarSpreadRsPer10g", "CalendarSpreadPercent", "CurveShape",
]

result = pd.DataFrame(results, columns=columns)

if not result.empty:
    result = result.sort_values(
        ["Date", "Symbol", "NearExpiry"]
    )

result.to_csv(OUTPUT_FILE, index=False)

print("\nGOLDLENS — TERM-STRUCTURE ANALYSIS")
print("=" * 65)
print(f"Trading dates: {df['Date'].nunique()}")
print(f"Contracts analyzed: {df['Symbol'].nunique()}")
print(f"Adjacent-expiry comparisons: {len(result)}")

if result.empty:
    print("\nNo adjacent-expiry comparisons could be generated.")
else:
    print("\nCalendar spreads:")
    print(result.to_string(index=False))

    print("\nCurve summary:")
    summary = (
        result.groupby(["Symbol", "CurveShape"])
        .size()
        .unstack(fill_value=0)
    )
    print(summary.to_string())

print(f"\nSaved to: {OUTPUT_FILE}")
print(
    "\nNote: This is a single-date curve snapshot when only one date "
    "is available. It does not measure historical roll-down returns "
    "or establish a profitable trading strategy."
)
