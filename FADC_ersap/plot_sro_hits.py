import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_npy(file_path):
    path = Path(file_path)
    if not path.exists() or path.suffix != '.npy':
        print(f"Error: '{file_path}' does not exist or is not a .npy file.")
        sys.exit(1)

    try:
        data = np.load(file_path)
    except Exception as e:
        print(f"Error loading .npy file: {e}")
        sys.exit(1)

    print(f"File: {file_path}")
    print(f"Type: {type(data)}")
    print(f"Shape: {data.shape}")
    print(f"Fields: {data.dtype.names}")

    df = pd.DataFrame(data)
   
    crate_val = 2
    slot_val = 13
    channel_val = 1
    
    # Filter the DataFrame
    df_sel = df[
        (df['crate'] == crate_val) &
        (df['slot'] == slot_val) &
        (df['channel'] == channel_val)
    ]
    
    # Plot
    plt.figure(figsize=(8,5))
    plt.scatter(df_sel['time'], df_sel['charge'], s=10)  # s=10 for smaller points
    plt.xlabel('Time')
    plt.ylabel('Charge')
    plt.title(f'Charge vs Time (crate={crate_val}, slot={slot_val}, channel={channel_val})')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python csv_to_npy.py <filename.csv>")
        sys.exit(1)

    plot_npy(sys.argv[1])

