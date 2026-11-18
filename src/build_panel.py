"""Build a state-item-month panel using DuckDB SQL over PriceCatcher Parquet."""

from pathlib import Path
import json
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

def sql_string(value: str) -> str:
    return value.replace("'", "''")

def build_filter(patterns: list[str]) -> str:
    clauses = [
        f"upper(item) LIKE '%{sql_string(pattern.upper())}%'"
        for pattern in patterns
    ]
    return "(" + " OR ".join(clauses) + ")"

def main() -> None:
    config = json.loads((ROOT / "config" / "items.json").read_text(encoding="utf-8"))
    patterns = config["item_patterns"]

    monthly_files = sorted(RAW.glob("pricecatcher_*.parquet"))
    if not monthly_files:
        raise FileNotFoundError(
            "No PriceCatcher monthly files found. Run src/download.py first."
        )

    required = [RAW / "lookup_item.parquet", RAW / "lookup_premise.parquet"]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(f"Missing {path.name}")

    sql = (ROOT / "sql" / "aggregate_prices.sql").read_text(encoding="utf-8")
    sql = sql.format(
        item_lookup=(RAW / "lookup_item.parquet").as_posix(),
        premise_lookup=(RAW / "lookup_premise.parquet").as_posix(),
        price_glob=(RAW / "pricecatcher_*.parquet").as_posix(),
        item_filter=build_filter(patterns),
    )

    con = duckdb.connect()
    panel = con.execute(sql).df()

    # Safety checks before publishing processed output.
    if panel.empty:
        raise ValueError(
            "No item rows matched the configured patterns. "
            "Inspect lookup_item and revise config/items.json."
        )
    if (panel["n_observations"] <= 0).any():
        raise ValueError("Panel contains non-positive observation counts.")

    panel.to_csv(OUT / "state_item_month_panel.csv", index=False)
    print(f"Saved {len(panel):,} state-item-month rows.")

    selected = (
        panel[["item_code", "item", "unit"]]
        .drop_duplicates()
        .sort_values(["item", "unit"])
    )
    selected.to_csv(OUT / "selected_items.csv", index=False)
    print("Selected items:")
    print(selected.to_string(index=False))

if __name__ == "__main__":
    main()
