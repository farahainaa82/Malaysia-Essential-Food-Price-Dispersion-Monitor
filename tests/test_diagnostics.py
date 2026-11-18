import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diagnostics import robust_zscore, classify_review

def test_robust_zscore_constant_series():
    s = pd.Series([5.0, 5.0, 5.0])
    assert robust_zscore(s).tolist() == [0.0, 0.0, 0.0]

def test_robust_zscore_marks_extreme_value():
    s = pd.Series([10, 10, 11, 10, 30], dtype=float)
    z = robust_zscore(s)
    assert z.iloc[-1] > 3.5

def test_review_priority_requires_coverage():
    row = pd.Series({
        "coverage_ok": False,
        "state_to_national_gap": 0.50,
        "dispersion_iqr_over_median": 0.50,
        "robust_z": 8.0,
    })
    assert classify_review(row) == "insufficient_coverage"

def test_review_priority_two_signals():
    row = pd.Series({
        "coverage_ok": True,
        "state_to_national_gap": 0.12,
        "dispersion_iqr_over_median": 0.20,
        "robust_z": 0.0,
    })
    assert classify_review(row) == "review_priority"
