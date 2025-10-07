import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

def plot_timeseries(
    df: pd.DataFrame,
    y_cols,
    time_col: str = "time",
    title: str = "Time Series Plot",
    scale_100: bool = True,
    save_path: str = None,
):
    d = df.copy()

    missing = [c for c in [time_col, *y_cols] if c not in d.columns]
    if missing:
        raise ValueError(f"Missing columns in DataFrame: {missing}")

    if not pd.api.types.is_datetime64_any_dtype(d[time_col]):
        d[time_col] = pd.to_datetime(d[time_col], errors="coerce")
    d = d.dropna(subset=[time_col]).sort_values(time_col)

    for c in y_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    y_cols = [c for c in y_cols if d[c].notna().any()]
    if not y_cols:
        raise ValueError("All selected y columns are empty after coercion to numeric.")

    plotted = d[[time_col] + y_cols].copy()
    if scale_100:
        for c in y_cols:
            plotted[c] = plotted[c] * 100.0

    plt.figure(figsize=(12, 5))
    for c in y_cols:
        plt.plot(plotted[time_col], plotted[c], label=c, linewidth=1.6)

    plt.title(title)
    plt.xlabel(time_col.capitalize())
    plt.ylabel("Value (%)" if scale_100 else "Value")
    plt.grid(alpha=0.2)
    plt.legend()

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)
        print(f"Saved to {save_path}")
    else:
        plt.show()