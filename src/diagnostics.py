"""Add robust anomaly diagnostics and transparent policy-review flags."""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "state_item_month_panel.csv"
OUTPUT = ROOT / "data" / "processed" / "state_item_month_diagnostics.csv"

def robust_zscore(values: pd.Series) -> pd.Series:
    """Return a robust anomaly score with explicit zero-scale fallbacks.

    Primary scale: median absolute deviation (MAD).
    If MAD is zero because many prices repeat, use IQR / 1.349.
    If both robust scales collapse but values still vary, fall back to
    sample standard deviation so unusual observations are not silently
    converted to zero-score records.
    """
    values = values.astype(float)
    median = values.median()
    mad = (values - median).abs().median()

    if pd.notna(mad) and mad > 0:
        scale = mad / 0.6745
    else:
        q25, q75 = values.quantile([0.25, 0.75])
        iqr = q75 - q25
        if pd.notna(iqr) and iqr > 0:
            scale = iqr / 1.349
        else:
            std = values.std(ddof=1)
            if pd.isna(std) or std == 0:
                return pd.Series(
                    np.zeros(len(values)),
                    index=values.index,
                    dtype=float,
                )
            scale = std

    return (values - median) / scale

def classify_review(row) -> str:
    reasons = 0
    if row["coverage_ok"]:
        reasons += int(row["state_to_national_gap"] >= 0.10)
        reasons += int(row["dispersion_iqr_over_median"] >= 0.15)
        reasons += int(abs(row["robust_z"]) >= 3.5)

    if not row["coverage_ok"]:
        return "insufficient_coverage"
    if reasons >= 2:
        return "review_priority"
    if reasons == 1:
        return "watch"
    return "no_flag"

def main() -> None:
    df = pd.read_csv(INPUT, parse_dates=["month"])

    df["coverage_ok"] = (
        (df["n_observations"] >= 30)
        & (df["n_premises"] >= 5)
    )

    df["robust_z"] = (
        df.groupby(["state", "item_code"], group_keys=False)["price_median"]
        .apply(robust_zscore)
    )

    df["review_flag"] = df.apply(classify_review, axis=1)

    df.to_csv(OUTPUT, index=False)
    print(df["review_flag"].value_counts(dropna=False).to_string())
    print(f"Saved diagnostics to {OUTPUT}")

if __name__ == "__main__":
    main()
