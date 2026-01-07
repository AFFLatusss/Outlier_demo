import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# def plot_scatter(s):
#     # Extract metadata
#     unit = s.iloc[0]                    # 'ohm' (string, ignore for plotting but use in label)
#     lower_bound = float(s.iloc[1])      # 0.0
#     upper_bound = float(s.iloc[2])      # 20.0

#     # Extract only the actual measurement data (from index 3 onward) and ensure numeric
#     data = pd.to_numeric(s.iloc[3:], errors='coerce').dropna()

#     # Optional: Reset x-axis to start from 0,1,2,... for cleaner sequential view
#     x = range(len(data))                 # Or use data.index if you want original indices

#     # Plot
#     plt.figure(figsize=(14, 7))
#     plt.scatter(x, data.values, alpha=0.7, color='blue', s=20)  # s=50 for bigger dots

#     # Add spec limit lines
#     plt.axhline(y=lower_bound, color='green', linestyle='--', linewidth=2, label=f'Lower Bound: {lower_bound}')
#     plt.axhline(y=upper_bound, color='red', linestyle='--', linewidth=2, label=f'Upper Bound: {upper_bound}')

#     # Labels and styling
#     plt.xlabel('Measurement Point / Index (sequential)')
#     plt.ylabel(f'DC_Kelvin_P2 ({unit})')
#     plt.title('Scatter Plot of DC_Kelvin_P2 Measurements with Spec Limits')
#     plt.legend()
#     plt.grid(True, alpha=0.3)

#     # Optional: zoom Y-axis to focus on data cluster (since values are ~2.52 and limits 0-20)
#     plt.ylim(lower_bound - 2, upper_bound + 2)  # Or tighter: plt.ylim(2.4, 2.6)

#     # plt.tight_layout()
#     plt.show()

def plot_scatter(s):
    # Extract metadata
    unit = s.iloc[0]                    # 'ohm'
    lower_bound = float(s.iloc[1])      # 0.0
    upper_bound = float(s.iloc[2])      # 20.0

    # Extract only the actual measurement data (from index 3 onward) and ensure numeric
    data = pd.to_numeric(s.iloc[3:], errors='coerce').dropna()

    # Create figure explicitly (better control in Streamlit)
    fig, ax = plt.subplots(figsize=(14, 7))

    # Sequential x-axis
    x = range(len(data))

    # Scatter plot
    ax.scatter(x, data.values, alpha=0.7, color='blue', s=20)

    # Spec limit lines
    ax.axhline(y=lower_bound, color='green', linestyle='--', linewidth=2,
               label=f'Lower Bound: {lower_bound}')
    ax.axhline(y=upper_bound, color='red', linestyle='--', linewidth=2,
               label=f'Upper Bound: {upper_bound}')

    # Labels and styling
    ax.set_xlabel('Measurement Point / Index (sequential)')
    ax.set_ylabel(f'DC_Kelvin_P2 ({unit})')
    ax.set_title('Scatter Plot of DC_Kelvin_P2 Measurements with Spec Limits')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Optional Y-zoom (adjust as needed)
    ax.set_ylim(lower_bound - 2, upper_bound + 2)

    plt.tight_layout()

    return fig  # Return the figure object