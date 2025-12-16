from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_time_series(csv_path: Path) -> pd.DataFrame:
    """Load the Finland time-series file with a clean timestamp index."""
    df = pd.read_csv(csv_path, sep=";", index_col=0, parse_dates=True)
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    df.index.name = "timestamp"
    return df


def plot_fi_time_series(csv_path: Path, output_dir: Path) -> Path:
    """Create descriptive daily-mean plots for demand and renewable profiles."""
    df = load_time_series(csv_path)

    demand_cols = [
        "ELECTRICITY",
        "HEAT_LOW_T_SH",
        "SPACE_COOLING",
        "MOBILITY_PASSENGER",
        "MOBILITY_FREIGHT",
    ]
    renewable_cols = [
        "PV",
        "WIND_ONSHORE",
        "WIND_OFFSHORE",
        "HYDRO_DAM",
        "HYDRO_RIVER",
        "SOLAR",
        "CSP",
    ]

    demand_cols = [col for col in demand_cols if col in df.columns]
    renewable_cols = [col for col in renewable_cols if col in df.columns]
    plot_cols = demand_cols + renewable_cols
    if not plot_cols:
        msg = "No matching columns found for plotting."
        raise ValueError(msg)

    daily = df[plot_cols].resample("D").mean()

    output_dir.mkdir(parents=True, exist_ok=True)
    figure_path = output_dir / "fi_time_series_daily.png"

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    daily[demand_cols].plot(ax=axes[0], linewidth=1.2)
    axes[0].set(
        title="Finland daily mean demands (share of annual peak)",
        ylabel="Fraction",
    )
    axes[0].legend(loc="upper right", ncol=2)

    daily[renewable_cols].plot(ax=axes[1], linewidth=1.2)
    axes[1].set(
        title="Finland daily mean renewable availability",
        ylabel="Capacity factor",
        xlabel="Date",
    )
    axes[1].legend(loc="upper right", ncol=2)

    fig.tight_layout()
    fig.savefig(figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return figure_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot descriptive stats for Finland time_series.csv.",
    )
    parser.add_argument(
        "--year",
        default="2035",
        help="Dataset year to use (2035 or 2050).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("plots"),
        help="Directory where the figure will be written.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("Data"),
        help="Root data directory (defaults to repository Data folder).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = args.data_dir / args.year / "FI" / "Time_series.csv"
    if not csv_path.exists():
        msg = f"Could not find the requested file at {csv_path}"
        raise FileNotFoundError(msg)

    figure_path = plot_fi_time_series(csv_path, args.output_dir)
    print(f"Figure written to {figure_path}")


if __name__ == "__main__":
    main()
