import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_scatter(data, test_name="", type="scatter", outlier_mode=False, merge=False):
    """
    Plots scatter or line for:
    - A single Series (original behavior)
    - Or a DataFrame (new: multiple columns overlaid with different colors)
    
    Assumes:
    - All columns in DataFrame have the SAME lower/upper bounds (taken from first column)
    - Row 0: unit (per column)
    - Row 1: lower bound (if not outlier_mode)
    - Row 2: upper bound (if not outlier_mode)
    - Row 3+: measurement data
    """
    fig, ax = plt.subplots(figsize=(16, 8))

    # Handle single Series (backward compatible)
    if isinstance(data, pd.Series):
        cols = [data.name or "Measurement"]
        data_df = data.to_frame()
    else:
        data_df = data
        cols = data_df.columns.tolist()

    # Use bounds from first column (user confirmed they are identical across columns)
    first_col = data_df.columns[0]
    lower_bound = float(data_df[first_col].iloc[2]) if outlier_mode else float(data_df[first_col].iloc[1])
    upper_bound = float(data_df[first_col].iloc[1]) if outlier_mode else float(data_df[first_col].iloc[2])

    # Color palette (cycles if many columns)
    colors = plt.cm.tab10(np.linspace(0, 1, len(cols)))

    for i, col in enumerate(cols):
        s = data_df[col]
        unit = s.iloc[0]
        meas_data = pd.to_numeric(s.iloc[3:], errors='coerce').dropna()
        x = range(len(meas_data))
        color = colors[i]

        label = f"{col}"

        if type == "scatter":
            ax.scatter(x, meas_data.values, alpha=0.8, color=color, s=30, edgecolors='black', linewidth=0.5, label=label)
        else:  # line
            ax.plot(x, meas_data.values, alpha=0.8, color=color, linewidth=2.5, label=label)

    # Common spec limits
    ax.axhline(y=lower_bound, color='green', linestyle='--', linewidth=2.5, label=f'Lower Bound: {lower_bound}')
    ax.axhline(y=upper_bound, color='red', linestyle='--', linewidth=2.5, label=f'Upper Bound: {upper_bound}')

    # Styling
    ax.set_xlabel('Measurement Index (sequential)', fontsize=12)
    ax.set_ylabel(f'{test_name} ({unit})', fontsize=12)
    if not merge:
        ax.set_title(test_name, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)  # Outside for many columns

    # Y-zoom around common bounds (with padding)
    padding = (upper_bound - lower_bound) * 0.2 or 1  # Avoid zero div
    ax.set_ylim(lower_bound - padding, upper_bound + padding)

    plt.tight_layout()
    return fig