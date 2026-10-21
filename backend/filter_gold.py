
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

TARGET_SYMBOLS = {
    "GOLDM",
    "GOLDTEN",
    "GOLDGUINEA",
    "GOLDPETAL",
}


def main():
    files = sorted(RAW_DIR.glob("*.csv"))

    if not files:
        print("ERROR: No CSV file found in data/raw.")
        return

    # Load the latest-named file in the raw folder.
    file_path = files[-1]
    df = pd.read_csv(file_path)
    df.columns = df.columns.astype(str).str.strip()

    required = {
        "Date", "Instrument Name", "Symbol",
        "Expiry Date", "Close",
        "Volume(Lots)", "Open Interest(Lots)"
    }

    missing = required - set(df.columns)

    if missing:
        print("Missing required columns:", sorted(missing))
        print("Available columns:", df.columns.tolist())
        return

    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
    df["Instrument Name"] = (
        df["Instrument Name"].astype(str).str.strip().str.upper()
    )

    # First inspect which gold symbols exist in the source file.
    gold_rows = df[df["Symbol"].str.contains("GOLD", na=False)]

    print("\nGold-related symbols found:")
    print(sorted(gold_rows["Symbol"].unique().tolist()))

    # Select the four target contracts.
    gold = df[df["Symbol"].isin(TARGET_SYMBOLS)].copy()

    # Keep futures records, excluding options if identified separately.
    gold = gold[gold["Instrument Name"] == "FUTCOM"].copy()

    if gold.empty:
        print("\nNo matching futures rows found.")
        print("Check the symbol list and instrument names above.")
        return

    # Parse the trading date and compact expiry date.
    gold["TradingDate"] = pd.to_datetime(
        gold["Date"].astype(str).str.strip(),
        format="%d %b %Y",
        errors="coerce"
    )

    gold["ExpiryDate"] = pd.to_datetime(
        gold["Expiry Date"].astype(str).str.strip(),
        format="%d%b%Y",
        errors="coerce"
    )

    # Convert numeric fields safely.
    numeric_columns = [
        "Open", "High", "Low", "Close",
        "Volume(Lots)", "Open Interest(Lots)"
    ]

    for col in numeric_columns:
        gold[col] = pd.to_numeric(gold[col], errors="coerce")

    print("\nMatching futures rows:", len(gold))
    print("\nRows by contract:")
    print(gold.groupby("Symbol").size().to_string())

    print("\nExpiry dates:")
    print(
        gold[["Symbol", "Expiry Date", "ExpiryDate"]]
        .drop_duplicates()
        .sort_values(["Symbol", "ExpiryDate"])
        .to_string(index=False)
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "gold_futures.csv"
    gold.to_csv(output_file, index=False)

    print(f"\nSaved filtered data to: {output_file}")
    print("\nFirst five matching records:")
    print(gold.head().to_string(index=False))


if __name__ == "__main__":
    main()
