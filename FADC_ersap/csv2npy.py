import sys
import pandas as pd
import numpy as np
from pathlib import Path

def convert_csv_to_npy(csv_path: str):
    csv_file = Path(csv_path)
    if not csv_file.exists() or not csv_file.suffix == '.csv':
        print(f"Error: File '{csv_path}' does not exist or is not a .csv file.")
        sys.exit(1)

    # Define expected column headers in order
    columns = ["rocID", "frameNumber", "timestamp", "crate", "slot", "channel", "charge", "time"]

    # Read CSV without headers
    df = pd.read_csv(csv_file, names=columns)

    # Convert to structured array
    records = df.to_records(index=False)

    # Save as .npy with same name
    npy_path = csv_file.with_suffix('.npy')
    np.save(npy_path, records)
    print(f"Saved {len(records)} records to {npy_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python csv_to_npy.py <filename.csv>")
        sys.exit(1)

    convert_csv_to_npy(sys.argv[1])
