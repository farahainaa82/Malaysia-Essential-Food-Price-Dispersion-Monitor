"""Create interpretable policy-surveillance figures."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "state_item_month_diagnostics.csv"
FIG = ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

def main() -> None:
    df = pd.read_csv(DATA, parse_dates=["month"])

    # Figure 1: latest state-to-national gaps for the most frequently observed item.
    latest = df["month"].max()
    counts = (
        df[df["month"].eq(latest)]
        .groupby(["item_code", "item"])["n_observations"].sum()
        .sort_values(ascending=False)
    )
    if counts.empty:
        raise ValueError("No data available for visualisation.")

    item_code, item_name = counts.index[0]
    one = df[(df["month"].eq(latest)) & (df["item_code"].eq(item_code))].copy()
    one = one.sort_values("state_to_national_gap")

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(one["state"], one["state_to_national_gap"] * 100)
    ax.axvline(0, linewidth=1)
    ax.set_xlabel("State median gap from national median (%)")
    ax.set_title(f"Observed Price Gap by State: {item_name}")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / "01_state_price_gap.png", dpi=180)
    plt.close(fig)

    # Figure 2: dispersion vs price gap.
    latest_df = df[df["month"].eq(latest) & df["coverage_ok"]].copy()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(
        latest_df["state_to_national_gap"] * 100,
        latest_df["dispersion_iqr_over_median"] * 100,
    )
    ax.axvline(10, linestyle="--", linewidth=1)
    ax.axhline(15, linestyle="--", linewidth=1)
    ax.set_xlabel("State-to-national median gap (%)")
    ax.set_ylabel("Within-state IQR / median (%)")
    ax.set_title("Price Surveillance Triage")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIG / "02_surveillance_triage.png", dpi=180)
    plt.close(fig)

    # Figure 3: flag counts by state.
    flags = (
        latest_df.assign(flagged=latest_df["review_flag"].isin(["watch", "review_priority"]))
        .groupby("state")["flagged"].sum()
        .sort_values()
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(flags.index, flags.values)
    ax.set_xlabel("Number of selected item series flagged")
    ax.set_title("Latest-Month Screening Flags by State")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / "03_flags_by_state.png", dpi=180)
    plt.close(fig)

    print(f"Figures saved to {FIG}")

if __name__ == "__main__":
    main()
