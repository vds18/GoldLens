
from pathlib import Path
import pandas as pd
import json

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "processed"

OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_SYMBOLS = {"GOLDM", "GOLDTEN", "GOLDGUINEA", "GOLDPETAL"}

REQUIRED_COLUMNS = {
    "Date", "Instrument Name", "Symbol", "Expiry Date",
    "Open", "High", "Low", "Close",
    "Volume(Lots)", "Open Interest(Lots)"
}

files = sorted(RAW_DIR.glob("*.csv"))

if not files:
    raise FileNotFoundError(f"No CSV files found in: {RAW_DIR}")

frames = []
file_report = []

for file in files:
    try:
        df = pd.read_csv(file, low_memory=False)
        df.columns = df.columns.astype(str).str.strip()

        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            print(f"SKIPPED {file.name}: missing columns {sorted(missing)}")
            file_report.append({
                "file": file.name,
                "status": "MISSING_COLUMNS",
                "missing_columns": sorted(missing),
                "rows": len(df),
            })
            continue

        df["SourceFile"] = file.name
        frames.append(df)

        file_report.append({
            "file": file.name,
            "status": "READ",
            "rows": len(df),
        })
        print(f"Read {file.name}: {len(df):,} rows")

    except Exception as exc:
        print(f"ERROR {file.name}: {exc}")
        file_report.append({
            "file": file.name,
            "status": "ERROR",
            "error": str(exc),
        })

if not frames:
    raise ValueError(
        "No files matched the expected MCX Bhavcopy columns. "
        "Check the CSV headers and delimiter."
    )

combined = pd.concat(frames, ignore_index=True, sort=False)

# Normalize text fields.
for column in ["Symbol", "Instrument Name"]:
    combined[column] = (
        combined[column].astype("string").str.strip().str.upper()
    )

# Parse dates in the format shown in your files, e.g. 13 Oct 2026.
combined["Date"] = pd.to_datetime(
    combined["Date"], format="%d %b %Y", errors="coerce"
)
combined["Expiry Date"] = pd.to_datetime(
    combined["Expiry Date"], format="%d%b%Y", errors="coerce"
)

# Convert market-value columns to numeric values.
numeric_columns = [
    "Strike Price", "Open", "High", "Low", "Close",
    "Previous Close", "Volume(Lots)", "Volume(In 000's)",
    "Value(Lacs)", "Open Interest(Lots)"
]

for column in numeric_columns:
    if column in combined.columns:
        combined[column] = pd.to_numeric(
            combined[column].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )

before = len(combined)
combined = combined.drop_duplicates().reset_index(drop=True)
duplicates_removed = before - len(combined)

# Save all contracts for auditing.
all_path = OUT_DIR / "bhavcopy_month_combined.csv"
combined.to_csv(all_path, index=False, date_format="%Y-%m-%d")

# Filter only the four target gold contracts.
gold = combined[
    combined["Symbol"].isin(TARGET_SYMBOLS)
    & combined["Instrument Name"].str.contains("FUT", na=False)
].copy()

gold_path = OUT_DIR / "historical_gold_download.csv"
gold.to_csv(gold_path, index=False, date_format="%Y-%m-%d")

valid_dates = sorted(
    combined["Date"].dropna().dt.strftime("%Y-%m-%d").unique().tolist()
)
symbols_found = sorted(combined["Symbol"].dropna().unique().tolist())

report = {
    "files_found": len(files),
    "files_read": len(frames),
    "combined_rows": len(combined),
    "exact_duplicate_rows_removed": duplicates_removed,
    "valid_trading_dates": valid_dates,
    "unique_trading_dates": len(valid_dates),
    "target_symbols_found": sorted(
        set(gold["Symbol"].dropna().tolist())
    ),
    "target_gold_rows": len(gold),
    "missing_target_symbols": sorted(
        TARGET_SYMBOLS - set(gold["Symbol"].dropna().tolist())
    ),
    "rows_missing_date": int(combined["Date"].isna().sum()),
    "rows_missing_close": int(combined["Close"].isna().sum()),
    "files": file_report,
}

report_path = OUT_DIR / "bhavcopy_validation_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\n========== VALIDATION SUMMARY ==========")
print(f"Files found: {len(files)}")
print(f"Files read: {len(frames)}")
print(f"Combined rows: {len(combined):,}")
print(f"Exact duplicates removed: {duplicates_removed:,}")
print(f"Unique trading dates: {len(valid_dates)}")
print(f"Trading dates: {valid_dates}")
print(f"Gold rows: {len(gold):,}")
print(f"Gold symbols found: {report['target_symbols_found']}")
print(f"Missing gold symbols: {report['missing_target_symbols']}")
print(f"Rows missing date: {report['rows_missing_date']}")
print(f"Rows missing close: {report['rows_missing_close']}")
print(f"\nAll contracts: {all_path}")
print(f"Gold-only data: {gold_path}")
print(f"Validation report: {report_path}")
