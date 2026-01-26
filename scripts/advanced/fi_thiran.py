#!/usr/bin/env python3
"""
plot_td_inputs_fi_2017_paper.py

Paper-ready plots for EnergyScope Multi-Cells TD inputs (Finland, reference year 2017, UTC):
1) Main heatmaps (day of year x hour) for ELECTRICITY, HEAT_LOW_T_SH, PV, WIND_ONSHORE, HYDRO_RIVER, SOLAR
2) Optional separate heatmap for SPACE_COOLING (scale differs a lot)
3) Duration curves (demands; renewables)
4) Daily-mean correlation scatter plots (weather vs demand), color coded by day of year
5) Passenger mobility mean daily profile (hour-of-day)

Folder output:
- <out_dir>/figures/*.pdf and *.png

Usage example:
python plot_td_inputs_fi_2017_paper.py \
  --input "EnergyScope_multi_cells/Data/2035/FI/Time_series.csv" \
  --out_dir "plots/td_inputs_fi_2017"

Notes:
- Input CSV is semicolon-separated in Multi-Cells.
- First column is a timestamp, parsed as UTC.
"""

from __future__ import annotations
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def read_multicells_timeseries(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=";")
    # First column is timestamp (unnamed in the Multi-Cells export)
    ts_col = df.columns[0]
    df["datetime"] = pd.to_datetime(df[ts_col], utc=True)
    df = df.drop(columns=[ts_col]).set_index("datetime").sort_index()
    # Ensure hourly
    df = df.asfreq("h")
    return df


def day_hour_matrix(series: pd.Series) -> np.ndarray:
    """Return matrix of shape (24, n_days) with hours on rows and days on columns."""
    s = series.asfreq("h")
    n_days = int(s.index.dayofyear.max())
    mat = np.zeros((24, n_days))
    doy = s.index.dayofyear.values - 1  # 0-indexed days
    hr = s.index.hour.values
    mat[hr, doy] = s.values
    return mat


def month_tick_positions(year: int) -> tuple[list[int], list[str]]:
    """Tick positions for day-of-year axis, at month starts."""
    start = pd.Timestamp(f"{year}-01-01", tz="UTC")
    month_starts = pd.date_range(start, periods=12, freq="MS", tz="UTC")
    pos = [int(d.dayofyear) - 1 for d in month_starts]  # 0-index day rows
    lab = [d.strftime("%b") for d in month_starts]
    return pos, lab


def quarter_tick_positions(year: int) -> tuple[list[int], list[str]]:
    """Quarterly ticks (Jan, Apr, Jul, Oct) for compact month labeling."""
    months = [1, 4, 7, 10]
    pos = []
    lab = []
    for m in months:
        d = pd.Timestamp(f"{year}-{m:02d}-01", tz="UTC")
        pos.append(int(d.dayofyear) - 1)
        lab.append(d.strftime("%b"))
    return pos, lab


def savefig(fig: plt.Figure, out_base: Path, dpi: int = 300) -> None:
    out_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_base.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(out_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_heatmaps_main(df: pd.DataFrame, out_dir: Path, year: int) -> None:
    """
    2x3 heatmaps focused on supply-side profiles. Select up to six most variable
    sources among: PV, SOLAR (thermal), WIND_ONSHORE, WIND_OFFSHORE,
    HYDRO_DAM, HYDRO_RIVER, CSP, TIDAL. Plotted as capacity factors.
    """

    # Fixed order: offshore, solar thermal, hydro dam, wind onshore, solar PV, hydro river
    preferred_order = [
        "WIND_OFFSHORE",
        "SOLAR",
        "HYDRO_DAM",
        "WIND_ONSHORE",
        "PV",
        "HYDRO_RIVER",
    ]
    chosen = [c for c in preferred_order if c in df.columns]
    if not chosen:
        raise ValueError("No renewable/availability columns found for heatmaps")

    mats: dict[str, np.ndarray] = {c: day_hour_matrix(df[c]) for c in chosen}

    renew_vals = np.concatenate([mats[k].ravel() for k in mats])
    r_vmin, r_vmax = 0.0, float(np.nanpercentile(renew_vals, 99.0))

    xt_pos, xt_lab = quarter_tick_positions(year)

    fig, axes = plt.subplots(2, 3, figsize=(12.0, 6.2), constrained_layout=True)
    panels: list[tuple[str | None, int, int]] = []
    for idx in range(6):
        r = idx // 3
        c = idx % 3
        panels.append((chosen[idx] if idx < len(chosen) else None, r, c))

    ims = []
    for name, r, c in panels:
        ax = axes[r, c]
        if name is None:
            ax.axis("off")
            continue
        im = ax.imshow(mats[name], aspect="auto", origin="lower", vmin=r_vmin, vmax=r_vmax, cmap="viridis")
        ims.append(im)
        ax.set_title(name)
        ax.set_xlabel("Month")
        ax.set_ylabel("Hours")
        ax.set_xticks(xt_pos)
        ax.set_xticklabels(xt_lab)
        ax.set_yticks([0, 6, 12, 18, 23])
        ax.set_yticklabels([0, 6, 12, 18, 23])

    if ims:
        cbar = fig.colorbar(ims[0], ax=axes.ravel().tolist(), fraction=0.03, pad=0.015)
        cbar.set_label("Capacity factor")

    fig.suptitle(f"Finland supply profiles (heatmaps, {year}, UTC)", y=1.02)
    fig.text(0.5, -0.02, "Hours on Y, months on X; cold/warm seasonal structure visible", ha="center", va="center")
    savefig(fig, out_dir / "figures" / f"FI_{year}_heatmaps_main")


def plot_heatmap_space_cooling(df: pd.DataFrame, out_dir: Path, year: int) -> None:
    """Separate cooling heatmap since its scale often differs greatly."""
    if "SPACE_COOLING" not in df.columns:
        return

    mat = day_hour_matrix(df["SPACE_COOLING"] * 1e3)  # per mille
    xt_pos, xt_lab = quarter_tick_positions(year)
    vmin, vmax = 0.0, float(np.nanpercentile(mat.ravel(), 99.0))

    fig, ax = plt.subplots(1, 1, figsize=(10.5, 3.9), constrained_layout=True)
    im = ax.imshow(mat, aspect="auto", origin="lower", vmin=vmin, vmax=vmax, cmap="magma")
    ax.set_title("SPACE_COOLING")
    ax.set_xlabel("Month")
    ax.set_ylabel("Hours")
    ax.set_xticks(xt_pos)
    ax.set_xticklabels(xt_lab)
    ax.set_yticks([0, 6, 12, 18, 23])
    ax.set_yticklabels([0, 6, 12, 18, 23])
    cbar = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.04)
    cbar.set_label("Per mille of annual demand per hour")
    fig.suptitle(f"Finland TD input (space cooling heatmap, {year}, UTC)", y=1.02)
    savefig(fig, out_dir / "figures" / f"FI_{year}_heatmap_space_cooling")


def plot_duration_curves(df: pd.DataFrame, out_dir: Path, year: int) -> None:
    """Compact two-panel duration curves (demands, renewables)."""
    dem_cols = [c for c in ["ELECTRICITY", "HEAT_LOW_T_SH", "SPACE_COOLING"] if c in df.columns]
    res_cols = [c for c in ["PV", "WIND_ONSHORE", "WIND_OFFSHORE", "HYDRO_RIVER", "HYDRO_DAM", "SOLAR"] if c in df.columns]

    if not dem_cols and not res_cols:
        return

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2), constrained_layout=True)

    if dem_cols:
        ax = axes[0]
        for c in dem_cols:
            v = np.sort((df[c] * 1e3).values)[::-1]
            x = np.linspace(0, 100, len(v), endpoint=False)
            ax.plot(x, v, label=c)
        ax.set_xlabel("Percent of hours (sorted descending)")
        ax.set_ylabel("Per mille of annual demand per hour")
        ax.legend(ncol=2, fontsize=8, loc="upper right")
        ax.set_title("Demands")
    else:
        axes[0].axis("off")

    if res_cols:
        ax = axes[1]
        for c in res_cols:
            v = np.sort(df[c].values)[::-1]
            x = np.linspace(0, 100, len(v), endpoint=False)
            ax.plot(x, v, label=c)
        ax.set_xlabel("Percent of hours (sorted descending)")
        ax.set_ylabel("Capacity factor")
        ax.legend(ncol=3, fontsize=8, loc="upper right")
        ax.set_title("Renewables")
    else:
        axes[1].axis("off")

    fig.suptitle(f"Finland duration curves ({year}, UTC)", y=1.03)
    savefig(fig, out_dir / "figures" / f"FI_{year}_duration_curves_compact")


def plot_daily_mean_scatter(df: pd.DataFrame, out_dir: Path, year: int) -> None:
    """
    Scatter plots using daily means, color-coded by day-of-year.
    These are explanatory (not used directly for clustering), but help show co-variation.
    Demand axes are rescaled to per-mille (10^-3) of annual total per hour.
    Pearson r correlation is computed and displayed for each panel.
    """
    # Daily means
    daily = df.resample("D").mean()
    if daily.empty:
        return

    # Choose pairs that show weather-demand interactions
    # Format: (xcol, ycol, title, scale_x_to_permille, scale_y_to_permille)
    pairs = []
    if "HEAT_LOW_T_SH" in daily.columns and "SOLAR" in daily.columns:
        pairs.append(("HEAT_LOW_T_SH", "SOLAR", "Heating vs solar", True, False))
    if "ELECTRICITY" in daily.columns and "PV" in daily.columns:
        pairs.append(("ELECTRICITY", "PV", "Electricity vs PV", True, False))
    if "HEAT_LOW_T_SH" in daily.columns and "WIND_ONSHORE" in daily.columns:
        pairs.append(("HEAT_LOW_T_SH", "WIND_ONSHORE", "Heating vs wind (onshore)", True, False))

    if not pairs:
        return

    # Color by day of year
    doy = daily.index.dayofyear.values

    fig, axes = plt.subplots(1, len(pairs), figsize=(5.2 * len(pairs), 4.2), squeeze=False, constrained_layout=True)
    for i, (xcol, ycol, title, scale_x, scale_y) in enumerate(pairs):
        ax = axes[0, i]
        x = daily[xcol].values * (1e3 if scale_x else 1)
        y = daily[ycol].values * (1e3 if scale_y else 1)
        
        # Calculate Pearson correlation on daily means
        r = np.corrcoef(x, y)[0, 1]
        
        sc = ax.scatter(x, y, c=doy, s=14, alpha=0.85)
        ax.set_title(f"{title}\n$r = {r:.3f}$", fontsize=10)
        
        # Update axis labels based on whether scaled to per-mille
        xlabel = f"{xcol}\n(10$^{{-3}}$ × annual total per hour, daily mean)" if scale_x else f"{xcol} (daily mean)"
        ylabel = f"{ycol}\n(10$^{{-3}}$ × annual total per hour, daily mean)" if scale_y else f"{ycol} (daily mean)"
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=8)
        
    cbar = fig.colorbar(sc, ax=axes.ravel().tolist(), fraction=0.02, pad=0.02)
    cbar.set_label("Day of year", fontsize=9)
    fig.suptitle(f"Finland daily-mean co-variation ({year}, UTC)", y=1.02)
    savefig(fig, out_dir / "figures" / f"FI_{year}_daily_mean_scatter")


def plot_mobility_daily_profile(df: pd.DataFrame, out_dir: Path, year: int) -> None:
    """Mean hourly mobility profile (average over the year) for MOBILITY_PASSENGER."""
    if "MOBILITY_PASSENGER" not in df.columns:
        return

    s = df["MOBILITY_PASSENGER"] * 1e3  # per mille
    by_hour = s.groupby(s.index.hour).mean()

    fig, ax = plt.subplots(1, 1, figsize=(6.8, 3.9))
    ax.plot(by_hour.index, by_hour.values, label="MOBILITY_PASSENGER (mean day)")
    ax.set_xlabel("Hour of day (UTC)")
    ax.set_ylabel("Share of annual total per hour (per mille)")
    ax.set_xticks([0, 6, 12, 18, 23])
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(f"Finland passenger mobility daily profile ({year}, UTC)")
    savefig(fig, out_dir / "figures" / f"FI_{year}_mobility_passenger_daily_profile")


def main() -> None:
    # Default paths anchored at repo root (script sits in scripts/advanced)
    repo_root = Path(__file__).resolve().parents[2]
    default_input = repo_root / "Data/2035/FI/Time_series.csv"
    default_out = repo_root / "plots/td_inputs_fi_2017"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        default=str(default_input),
        help="Path to Time_series.csv (default: Data/2035/FI/Time_series.csv)",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=str(default_out),
        help="Output folder (default: plots/td_inputs_fi_2017)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2017,
        help="Reference year label (for titles and month ticks)",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)
    year = int(args.year)

    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path}")

    df = read_multicells_timeseries(in_path)

    # Core outputs for your TD subsection
    plot_heatmaps_main(df, out_dir, year)
    plot_heatmap_space_cooling(df, out_dir, year)
    plot_duration_curves(df, out_dir, year)
    plot_daily_mean_scatter(df, out_dir, year)
    plot_mobility_daily_profile(df, out_dir, year)

    # Simple console summary
    const_cols = [c for c in df.columns if np.isclose(df[c].max(), df[c].min())]
    print("Loaded:", in_path)
    print("Hours:", len(df))
    print("Columns:", list(df.columns))
    print("Constant series:", const_cols)
    print("Saved figures to:", out_dir / "figures")


if __name__ == "__main__":
    main()


