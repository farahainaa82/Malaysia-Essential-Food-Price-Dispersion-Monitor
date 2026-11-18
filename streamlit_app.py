from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed" / "state_item_month_diagnostics.csv"

st.set_page_config(
    page_title="Malaysia Essential Food Price Dispersion Monitor",
    page_icon="📊",
    layout="wide",
)

st.title("Malaysia Essential Food Price Dispersion Monitor")
st.caption(
    "High-frequency policy surveillance using Malaysia's PriceCatcher data. "
    "Statistical flags are screening signals, not evidence of misconduct."
)

if not DATA.exists():
    st.error(
        "The processed diagnostics file is not in this repository yet. "
        "Run the local pipeline, then commit "
        "`data/processed/state_item_month_diagnostics.csv` to GitHub."
    )
    st.markdown("### Local preparation")
    st.code(
        "python src/download.py --months 2026-05 2026-06 2026-07 2026-08 2026-09 2026-10\n"
        "python src/build_panel.py\n"
        "python src/diagnostics.py\n"
        "python src/visualize.py\n"
        "pytest -q",
        language="bash",
    )
    st.stop()

df = pd.read_csv(DATA, parse_dates=["month"])

st.sidebar.header("Filters")
item_table = (
    df[["item_code", "item", "unit"]]
    .drop_duplicates()
    .sort_values(["item", "unit"])
)
item_labels = {
    f"{row.item} ({row.unit})": row.item_code
    for row in item_table.itertuples(index=False)
}
selected_label = st.sidebar.selectbox("Item", list(item_labels))
selected_code = item_labels[selected_label]

month_values = sorted(df["month"].dropna().unique())
selected_month = st.sidebar.selectbox(
    "Month",
    month_values,
    index=len(month_values) - 1,
    format_func=lambda x: pd.Timestamp(x).strftime("%B %Y"),
)

view = df[
    (df["item_code"] == selected_code)
    & (df["month"] == selected_month)
].copy()

if view.empty:
    st.warning("No observations are available for this item and month.")
    st.stop()

st.subheader(
    f"{selected_label} — {pd.Timestamp(selected_month).strftime('%B %Y')}"
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("States represented", int(view["state"].nunique()))
c2.metric("Price observations", f"{int(view['n_observations'].sum()):,}")
c3.metric("Premises represented", f"{int(view['n_premises'].sum()):,}")
c4.metric(
    "Review-priority states",
    int((view["review_flag"] == "review_priority").sum()),
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["State comparison", "Policy triage", "State detail", "Methodology"]
)

with tab1:
    chart = view.sort_values("state_to_national_gap")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(chart["state"], chart["state_to_national_gap"] * 100)
    ax.axvline(0, linewidth=1)
    ax.set_xlabel("State median gap from national median (%)")
    ax.set_title("Observed state-to-national median price gap")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")

    table = view[
        [
            "state",
            "price_median",
            "national_price_median",
            "state_to_national_gap",
            "dispersion_iqr_over_median",
            "n_observations",
            "n_premises",
            "review_flag",
        ]
    ].copy()
    table["state_to_national_gap"] *= 100
    table["dispersion_iqr_over_median"] *= 100
    table = table.rename(
        columns={
            "state": "State",
            "price_median": "State median price",
            "national_price_median": "National median price",
            "state_to_national_gap": "Gap vs national (%)",
            "dispersion_iqr_over_median": "Dispersion (%)",
            "n_observations": "Observations",
            "n_premises": "Premises",
            "review_flag": "Review flag",
        }
    )
    st.dataframe(table, width="stretch", hide_index=True)

with tab2:
    covered = view[view["coverage_ok"]].copy()

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(
        covered["state_to_national_gap"] * 100,
        covered["dispersion_iqr_over_median"] * 100,
    )
    for _, row in covered.iterrows():
        ax.annotate(
            row["state"],
            (
                row["state_to_national_gap"] * 100,
                row["dispersion_iqr_over_median"] * 100,
            ),
            fontsize=7,
            xytext=(3, 3),
            textcoords="offset points",
        )
    ax.axvline(10, linestyle="--", linewidth=1)
    ax.axhline(15, linestyle="--", linewidth=1)
    ax.set_xlabel("State-to-national median gap (%)")
    ax.set_ylabel("Within-state IQR / median (%)")
    ax.set_title("Policy surveillance triage")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")

    st.markdown("### Why observations were flagged")
    flagged = view[view["review_flag"].isin(["review_priority", "watch"])]
    if flagged.empty:
        st.success("No watch or review-priority observations for this selection.")
    else:
        for _, row in flagged.sort_values("state").iterrows():
            reasons = []
            if not bool(row["coverage_ok"]):
                reasons.append("coverage is below the screening minimum")
            else:
                if row["state_to_national_gap"] >= 0.10:
                    reasons.append(
                        f"state median is {row['state_to_national_gap'] * 100:.1f}% "
                        "above the national median"
                    )
                if row["dispersion_iqr_over_median"] >= 0.15:
                    reasons.append(
                        f"within-state dispersion is "
                        f"{row['dispersion_iqr_over_median'] * 100:.1f}%"
                    )
                if abs(row["robust_z"]) >= 3.5:
                    reasons.append(
                        f"robust anomaly score is {row['robust_z']:.2f}"
                    )

            st.write(
                f"**{row['state']} — {row['review_flag']}**: "
                + "; ".join(reasons)
                + "."
            )

with tab3:
    state = st.selectbox("Choose state", sorted(view["state"].dropna().unique()))
    row = view[view["state"] == state].iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("State median price", f"{row['price_median']:.2f}")
    m2.metric("Gap vs national", f"{row['state_to_national_gap'] * 100:.1f}%")
    m3.metric("Dispersion", f"{row['dispersion_iqr_over_median'] * 100:.1f}%")

    history = df[
        (df["state"] == state) & (df["item_code"] == selected_code)
    ].sort_values("month")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(history["month"], history["price_median"], marker="o")
    ax.set_title(f"Monthly median observed price — {state}")
    ax.set_xlabel("Month")
    ax.set_ylabel("Median observed price")
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()
    fig.tight_layout()
    st.pyplot(fig, width="stretch")

    st.info(
        "A statistical flag does not establish profiteering, anti-competitive "
        "conduct, or a causal supply shock. A flagged observation should be "
        "followed by review of product specification, premise mix, district "
        "coverage, local supply conditions, and data quality."
    )

with tab4:
    st.markdown(
        """
### What this monitor measures

For each selected item, state and month, the monitor reports:

- state median observed price;
- state-to-national median gap;
- within-state price dispersion using IQR / median;
- robust time-series anomaly score;
- observation and premise coverage;
- transparent review flags.

### Screening rules

The default analytical thresholds are:

- at least **30 observations** and **5 premises**;
- state median **10% or more above** the national median;
- dispersion **15% or more**;
- absolute robust anomaly score **3.5 or more**.

Two or more signals produce a `review_priority` flag.

These are analytical screening parameters, not official policy thresholds.

### Evidence boundary

PriceCatcher is used for high-frequency surveillance of specific observed
prices. It is **not** used to construct an alternative CPI or infer inflation.
"""
    )

st.divider()
st.caption(
    "Portfolio project by Farah Ainaa Baharudin | "
    "Policy Data Science • Decision Intelligence • Data Governance"
)
