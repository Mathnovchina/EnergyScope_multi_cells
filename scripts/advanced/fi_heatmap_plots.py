from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_time_series(csv_path: Path) -> pd.DataFrame:
    """Read the Finland time series file with a clean timestamp index."""
    df = pd.read_csv(csv_path, sep=";", index_col=0, parse_dates=True)
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    df.index.name = "timestamp"
    return df


def create_heatmap_data(series: pd.Series) -> pd.DataFrame:
    """
    Reshape hourly time series into a 2D array: hours × days.
    Returns a DataFrame with 24 rows (hour of day) and 365 columns (day of year).
    """
    df = series.to_frame(name="value")
    df["day_of_year"] = df.index.dayofyear
    df["hour_of_day"] = df.index.hour
    
    # Pivot to create hour × day matrix
    heatmap = df.pivot_table(
        values="value",
        index="hour_of_day",
        columns="day_of_year",
        aggfunc="mean",
    )
    return heatmap


def plot_heatmap(
    data: pd.DataFrame,
    title: str,
    output_path: Path,
    cmap: str = "YlOrRd",
    vmin: float | None = None,
    vmax: float | None = None,
) -> None:
    """
    Create a single heatmap figure: hour of day (rows) vs day of year (columns).
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Auto-scale if not provided
    if vmin is None:
        vmin = data.min().min()
    if vmax is None:
        vmax = data.max().max()
    
    im = ax.imshow(
        data.values,
        aspect="auto",
        cmap=cmap,
        interpolation="nearest",
        vmin=vmin,
        vmax=vmax,
        origin="lower",
    )
    
    # Set ticks for readability
    # Month boundaries (approximate day of year for each month start)
    month_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax.set_xticks(month_days)
    ax.set_xticklabels(month_labels)
    
    hour_ticks = np.arange(0, 24, 2)
    ax.set_yticks(hour_ticks)
    ax.set_yticklabels(hour_ticks)
    
    ax.set(
        xlabel="Month",
        ylabel="Hour of Day",
        title=title,
    )
    
    cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02)
    cbar.set_label("Normalized Value")
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_combined_heatmaps(
    df: pd.DataFrame,
    columns: list[str],
    output_dir: Path,
) -> Path:
    """
    Create a single figure with three subplots (heatmaps) for ELECTRICITY,
    HEAT_LOW_T_SH, and SPACE_COOLING.
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 14), sharex=True)
    
    # Configure each heatmap
    configs = [
        {
            "col": "ELECTRICITY",
            "title": "Electricity Demand (normalized)",
            "cmap": "Blues",
        },
        {
            "col": "HEAT_LOW_T_SH",
            "title": "Heat Low Temperature (space heating, normalized)",
            "cmap": "Reds",
        },
        {
            "col": "SPACE_COOLING",
            "title": "Space Cooling (normalized)",
            "cmap": "Greens",
        },
    ]
    
    for ax, config in zip(axes, configs):
        col = config["col"]
        if col not in df.columns:
            ax.text(
                0.5, 0.5, f"Column '{col}' not found",
                ha="center", va="center", transform=ax.transAxes,
            )
            continue
        
        heatmap_data = create_heatmap_data(df[col])
        
        # Auto-scale per variable for better contrast
        vmin = heatmap_data.min().min()
        vmax = heatmap_data.max().max()
        
        im = ax.imshow(
            heatmap_data.values,
            aspect="auto",
            cmap=config["cmap"],
            interpolation="nearest",
            vmin=vmin,
            vmax=vmax,
            origin="lower",
        )
        
        # Ticks
        hour_ticks = np.arange(0, 24, 2)
        ax.set_yticks(hour_ticks)
        ax.set_yticklabels(hour_ticks)
        
        ax.set_ylabel("Hour of Day")
        ax.set_title(config["title"], fontsize=12, fontweight="bold")
        
        # Colorbar
        cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.01, fraction=0.046)
        cbar.ax.tick_params(labelsize=9)
    
    # Bottom axis only - month labels
    month_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    axes[-1].set_xticks(month_days)
    axes[-1].set_xticklabels(month_labels)
    axes[-1].set_xlabel("Month", fontsize=11)
    
    fig.suptitle(
        "Finland 2017 Time Series Heatmaps",
        fontsize=14,
        fontweight="bold",
        y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.99])
    
    output_path = output_dir / "fi_heatmaps_combined.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create heatmap plots for electricity, heat, and cooling time series.",
    )
    parser.add_argument(
        "--year",
        default="2035",
        help="Dataset year to use (2035 or 2050).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("Data"),
        help="Root data directory (repository Data folder by default).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("plots/fi_heatmaps"),
        help="Directory where plots will be stored.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = args.data_dir / args.year / "FI" / "Time_series.csv"
    
    if not csv_path.exists():
        msg = f"Could not find the requested file at {csv_path}"
        raise FileNotFoundError(msg)
    
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = load_time_series(csv_path)
    
    # Target columns
    target_columns = ["ELECTRICITY", "HEAT_LOW_T_SH", "SPACE_COOLING"]
    
    # Combined heatmap figure
    combined_path = plot_combined_heatmaps(df, target_columns, output_dir)
    print(f"Created combined heatmap: {combined_path}")


if __name__ == "__main__":
    main()
