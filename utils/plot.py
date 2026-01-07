import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_scatter(s,test_name, type="scatter"):
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
    if type == "scatter":
        ax.scatter(x, data.values, alpha=0.7, color='blue', s=20)
    else:
        ax.plot(x, data.values, alpha=0.7, color='blue', linewidth=2)


    # Spec limit lines
    ax.axhline(y=lower_bound, color='green', linestyle='--', linewidth=2,
               label=f'Lower Bound: {lower_bound}')
    ax.axhline(y=upper_bound, color='red', linestyle='--', linewidth=2,
               label=f'Upper Bound: {upper_bound}')

    # Labels and styling
    ax.set_xlabel('Measurement Point / Index (sequential)')
    ax.set_ylabel(f'{test_name} ({unit})')
    ax.set_title(test_name)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Optional Y-zoom (adjust as needed)
    ax.set_ylim(lower_bound - 2, upper_bound + 2)

    plt.tight_layout()

    return fig  # Return the figure object