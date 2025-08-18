import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class SRODataAnalyzer:
    def __init__(self, file_path):
        path = Path(file_path)
        if not path.exists() or path.suffix != '.npy':
            raise FileNotFoundError(f"Error: '{file_path}' does not exist or is not a .npy file.")

        try:
            self.data = np.load(file_path)
        except Exception as e:
            raise RuntimeError(f"Error loading .npy file: {e}")

        print(f"File: {file_path}")
        print(f"Type: {type(self.data)}")
        print(f"Shape: {self.data.shape}")
        print(f"Fields: {self.data.dtype.names}")

        self.df = pd.DataFrame(self.data)
        #print(self.df.columns)
        #print(self.df.head(5))
        #print(self.df.tail(5))

    def plot_npy(self, crate_val=2, slot_val=13, channel_val=1):
        df_sel = self.df[
            (self.df['crate'] == crate_val) &
            (self.df['slot'] == slot_val) &
            (self.df['channel'] == channel_val)
        ]

        plt.figure(figsize=(8, 5))
        plt.scatter(df_sel['time'], df_sel['charge'], s=10)
        plt.xlabel('Time')
        plt.ylabel('Charge')
        plt.title(f'Charge vs Time (crate={crate_val}, slot={slot_val}, channel={channel_val})')
        plt.grid(True)
        plt.show()


    def calculate_rate(self, crate_val=2, slot_val=13, channel_val=1):
        df_sel = self.df[
            (self.df['crate'] == crate_val) &
            (self.df['slot'] == slot_val) &
            (self.df['channel'] == channel_val)
        ]
        if df_sel.empty:
            print("No matching data found.")
            return None

        time_min = df_sel['timestamp'].min()
        time_max = df_sel['timestamp'].max()
        total_time = (time_max - time_min)/250.e6

        if total_time <= 0:
            print("Invalid time range.")
            return None

        rate = len(df_sel) / total_time
        print(time_min,time_max,rate)
        print(f"Hit rate (crate={crate_val}, slot={slot_val}, channel={channel_val}): {rate:.2f} hits/unit time")
        return rate

    def calculate_rate_all_channels(self, crate_val=2, slots=(13, 15), channels=range(16)):
        plt.figure(figsize=(8, 5))

        for slot in slots:
            rates = []
            for ch in channels:
                df_sel = self.df[
                    (self.df['crate'] == crate_val) &
                    (self.df['slot'] == slot) &
                    (self.df['channel'] == ch)
                ]

                if df_sel.empty:
                    rates.append(0)
                    continue

                time_min = df_sel['time'].min()
                time_max = df_sel['time'].max()
                total_time = (time_max - time_min)/250.0e6

                if total_time <= 0:
                    rates.append(0)
                    continue

                rate = len(df_sel) / total_time
                rates.append(rate)

            plt.plot(channels, rates, marker='o', label=f"Slot {slot}")

        plt.xlabel("Channel")
        plt.ylabel("Rate (hits per time unit)")
        plt.title(f"Rate vs Channel (crate={crate_val})")
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_charge_histogram(self, crate_val=2, slot_val=13, channel_val=1, bins=50):
        df_sel = self.df[
            (self.df['crate'] == crate_val) &
            (self.df['slot'] == slot_val) &
            (self.df['channel'] == channel_val)
        ]
        if df_sel.empty:
            print("No matching data found.")
            return

        plt.figure(figsize=(8, 5))
        plt.hist(df_sel['charge'], bins=bins, edgecolor='black', alpha=0.7)
        plt.xlabel("Charge")
        plt.ylabel("Count")
        plt.title(f"Charge Histogram (crate={crate_val}, slot={slot_val}, channel={channel_val})")
        plt.yscale('log')
        plt.grid(True)
        plt.show()

    def plot_charge_histograms_all_channels(self, crate_val=2, slot_val=13, bins=50):
        channels = range(16)
        fig, axes = plt.subplots(4, 4, figsize=(16, 12))
        axes = axes.flatten()

        for i, ch in enumerate(channels):
            ax = axes[i]
            df_sel = self.df[
                (self.df['crate'] == crate_val) &
                (self.df['slot'] == slot_val) &
                (self.df['channel'] == ch)
            ]

            if df_sel.empty:
                ax.text(0.5, 0.5, "No data", ha="center", va="center")
                ax.set_title(f"Ch {ch}")
                ax.axis("off")
                continue

            ax.hist(df_sel['charge'], bins=bins, edgecolor='black', alpha=0.7)
            ax.set_title(f"Ch {ch}")
            ax.set_yscale("log")  # log scale for y
            ax.grid(True, which="both", axis="y")

        fig.suptitle(f"Charge Histograms (crate={crate_val}, slot={slot_val})", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python plot_sro_hits.py <filename.npy>")
        sys.exit(1)

    analyzer = SRODataAnalyzer(sys.argv[1])
#    analyzer.plot_npy()
#    analyzer.calculate_rate()
#    analyzer.calculate_rate_all_channels()
#    analyzer.plot_charge_histogram(2,15,15)
    analyzer.plot_charge_histograms_all_channels(2,13)
