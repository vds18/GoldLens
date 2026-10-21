
from pathlib import Path
import pandas as pd

# Locate the data folder relative to this Python file.
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def inspect_csv(file_path):
    """Load a CSV and inspect its structure."""
    print(f"\nReading: {file_path.name}")

    df = pd.read_csv(file_path)

    # Remove extra spaces from column names.
    df.columns = df.columns.astype(str).str.strip()

    print(f"Rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nFirst five rows:")
    print(df.head().to_string())

    return df


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    files = list(RAW_DIR.glob("*.csv"))

    if not files:
        print("No CSV files found yet.")
        print(f"Place an MCX CSV file inside: {RAW_DIR}")
        return

    for file_path in files:
        try:
            inspect_csv(file_path)
        except Exception as error:
            print(f"Could not read {file_path.name}: {error}")


if __name__ == "__main__":
    main()
