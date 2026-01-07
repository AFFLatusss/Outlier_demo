import matplotlib.pyplot as plt
import numpy as np

def plot_scatter(s):
    # Extract metadata
    unit = s.iloc[0]                    # 'ohm' (string, ignore for plotting but use in label)
    lower_bound = float(s.iloc[1])      # 0.0
    upper_bound = float(s.iloc[2])      # 20.0

    # Extract only the actual measurement data (from index 3 onward) and ensure numeric
    data = pd.to_numeric(s.iloc[3:], errors='coerce').dropna()

    # Optional: Reset x-axis to start from 0,1,2,... for cleaner sequential view
    x = range(len(data))                 # Or use data.index if you want original indices

    # Plot
    plt.figure(figsize=(14, 7))
    plt.scatter(x, data.values, alpha=0.7, color='blue', s=20)  # s=50 for bigger dots

    # Add spec limit lines
    plt.axhline(y=lower_bound, color='green', linestyle='--', linewidth=2, label=f'Lower Bound: {lower_bound}')
    plt.axhline(y=upper_bound, color='red', linestyle='--', linewidth=2, label=f'Upper Bound: {upper_bound}')

    # Labels and styling
    plt.xlabel('Measurement Point / Index (sequential)')
    plt.ylabel(f'DC_Kelvin_P2 ({unit})')
    plt.title('Scatter Plot of DC_Kelvin_P2 Measurements with Spec Limits')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Optional: zoom Y-axis to focus on data cluster (since values are ~2.52 and limits 0-20)
    plt.ylim(lower_bound - 2, upper_bound + 2)  # Or tighter: plt.ylim(2.4, 2.6)

    # plt.tight_layout()
    plt.show()