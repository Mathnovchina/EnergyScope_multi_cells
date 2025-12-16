from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd

SECTOR_DEMAND_COLS = [
    "ELECTRICITY",
    "HEAT_LOW_T_SH",
    "MOBILITY_PASSENGER",
    "MOBILITY_FREIGHT",
]

WEATHER_COLS = [
    "PV",
    "SOLAR",
    "WIND_ONSHORE",
    "WIND_OFFSHORE",
    "HYDRO_DAM",
    "HYDRO_RIVER",
]

WEATHER_PAIRS = [
    ("PV", "ELECTRICITY"),
    ("SOLAR", "HEAT_LOW_T_SH"),
    ("WIND_ONSHORE", "MOBILITY_PASSENGER"),
    ("WIND_OFFSHORE", "MOBILITY_FREIGHT"),
]


def load_time_series(csv_path: Path) -> pd.DataFrame:
    """Read the Finland time series file and clean its timestamp index."""
    df = pd.read_csv(csv_path, sep=";", index_col=0, parse_dates=True)
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    df.index.name = "timestamp"
    return df


def ensure_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    present = [col for col in columns if col in df.columns]
    if not present:
        missing = ", ".join(columns)
        msg = f"None of the requested columns were found: {missing}"
        raise ValueError(msg)
    return present


def plot_sectoral_weekly_profiles(df: pd.DataFrame, output_dir: Path) -> Path:
    """Weekly mean profiles for each sector."""
    cols = ensure_columns(df, SECTOR_DEMAND_COLS)
    weekly = df[cols].resample("W").mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    weekly.plot(ax=ax, linewidth=1.5)
    ax.set(
        title="Finland 2017 weekly mean demand (normalized)",
        ylabel="Average hourly load (share of peak)",
        xlabel="Week",
    )
    ax.legend(loc="upper right")
    fig.tight_layout()

    figure_path = output_dir / "fi_weekly_sectoral_profiles.png"
    fig.savefig(figure_path, dpi=300)
    plt.close(fig)
    return figure_path


def plot_monthly_energy_breakdown(df: pd.DataFrame, output_dir: Path) -> Path:
    """Stacked monthly energy totals to show seasonal split."""
    cols = ensure_columns(df, SECTOR_DEMAND_COLS)
    monthly = df[cols].resample("M").sum()
    monthly.index = monthly.index.strftime("%b")

    fig, ax = plt.subplots(figsize=(12, 5))
    bottom = None
    for col in cols:
        if bottom is None:
            ax.bar(monthly.index, monthly[col], label=col)
            bottom = monthly[col].copy()
        else:
            ax.bar(monthly.index, monthly[col], bottom=bottom, label=col)
            bottom += monthly[col]

    ax.set(
        title="Monthly normalized energy demand split",
        ylabel="Sum of hourly normalized loads",
        xlabel="Month",
    )
    ax.legend(loc="upper right", ncol=2)
    fig.tight_layout()

    figure_path = output_dir / "fi_monthly_sectoral_energy.png"
    fig.savefig(figure_path, dpi=300)
    plt.close(fig)
    return figure_path


def plot_load_duration_curves(df: pd.DataFrame, output_dir: Path) -> Path:
    """Load duration curves for each sector."""
    cols = ensure_columns(df, SECTOR_DEMAND_COLS)
    fig, ax = plt.subplots(figsize=(12, 5))

    hours = len(df)
    share = (pd.Series(range(1, hours + 1)) / hours) * 100
    for col in cols:
        sorted_values = df[col].sort_values(ascending=False).reset_index(drop=True)
        ax.plot(share, sorted_values, label=col, linewidth=1.4)

    ax.set(
        title="Load duration curves (hour percentile vs normalized load)",
        xlabel="% of hours (descending)",
        ylabel="Normalized load",
    )
    ax.legend(loc="upper right")
    fig.tight_layout()

    figure_path = output_dir / "fi_load_duration_curves.png"
    fig.savefig(figure_path, dpi=300)
    plt.close(fig)
    return figure_path


def plot_weather_vs_energy(df: pd.DataFrame, output_dir: Path) -> Path:
    """Scatter matrix of daily mean weather proxies versus demand."""
    available_pairs = [
        pair for pair in WEATHER_PAIRS if pair[0] in df.columns and pair[1] in df.columns
    ]
    if not available_pairs:
        msg = "No overlapping weather-demand column pairs found."
        raise ValueError(msg)

    daily = df.resample("D").mean()
    day_of_year = daily.index.dayofyear

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes_flat = axes.flatten()
    for ax, (weather_col, demand_col) in zip(axes_flat, available_pairs):
        scatter = ax.scatter(
            daily[weather_col],
            daily[demand_col],
            c=day_of_year,
            cmap="viridis",
            s=25,
            alpha=0.7,
        )
        ax.set(
            title=f"Daily mean {demand_col} vs {weather_col}",
            xlabel=f"{weather_col} availability",
            ylabel=f"{demand_col} load",
        )
    # Remove unused axes if fewer than four pairs are available.
    for idx in range(len(available_pairs), len(axes_flat)):
        fig.delaxes(axes_flat[idx])

    cbar = fig.colorbar(scatter, ax=axes, orientation="vertical", fraction=0.025, pad=0.02)
    cbar.set_label("Day of year")
    fig.tight_layout()

    figure_path = output_dir / "fi_weather_vs_demand.png"
    fig.savefig(figure_path, dpi=300)
    plt.close(fig)
    return figure_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate descriptive analytics for Finland 2017 weather-energy data.",
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
        default=Path("plots/fi_weather_energy"),
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

    figure_builders = [
        plot_sectoral_weekly_profiles,
        plot_monthly_energy_breakdown,
        plot_load_duration_curves,
        plot_weather_vs_energy,
    ]

    for builder in figure_builders:
        figure_path = builder(df, output_dir)
        print(f"Created {figure_path}")


if __name__ == "__main__":
    main()
