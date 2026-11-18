"""Download selected monthly PriceCatcher files and lookup tables."""

from __future__ import annotations
from argparse import ArgumentParser
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

LOOKUPS = {
    "lookup_item.parquet":
        "https://storage.data.gov.my/pricecatcher/lookup_item.parquet",
    "lookup_premise.parquet":
        "https://storage.data.gov.my/pricecatcher/lookup_premise.parquet",
}

def download(url: str, destination: Path) -> None:
    print(f"Downloading {url}")
    response = requests.get(url, timeout=180)
    response.raise_for_status()
    destination.write_bytes(response.content)
    print(f"Saved {destination}")

def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--months",
        nargs="+",
        required=True,
        help="Months in YYYY-MM format, for example 2026-05 2026-06",
    )
    args = parser.parse_args()

    for filename, url in LOOKUPS.items():
        download(url, RAW / filename)

    for month in args.months:
        filename = f"pricecatcher_{month}.parquet"
        url = f"https://storage.data.gov.my/pricecatcher/{filename}"
        download(url, RAW / filename)

    (RAW / "months.txt").write_text("\n".join(args.months), encoding="utf-8")

if __name__ == "__main__":
    main()
