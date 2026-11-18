# Malaysia Essential Food Price Dispersion Monitor

**A reproducible public-policy data science portfolio using Malaysia's PriceCatcher open data**

## Policy question

> **Where are selected essential-food prices unusually dispersed across Malaysian states and premise types, and when do local price movements merit closer policy investigation?**

This repository is prepared as a second code portfolio for the **Khazanah Research Institute (KRI) – Policy Researcher (Data Science)** application.

It is intentionally different from the *Malaysia Household Resilience Monitor*. The first portfolio demonstrates survey/administrative-data integration. This project demonstrates **high-volume price surveillance, SQL-based transformation, robust statistics, anomaly screening and policy interpretation**.

## Why this question matters

A national average can hide substantial local variation. Consumers buy goods in specific places, from specific premise types, and at prices that may differ across districts and states.

Price dispersion can reflect many legitimate factors:
- transport and distribution costs;
- local supply conditions;
- premise type;
- product specification;
- promotions;
- temporary shocks;
- data coverage.

The objective is therefore **not to label a high price as wrongdoing**. It is to identify patterns that deserve explanation.

## Official public data

### 1. PriceCatcher transactional records
Daily product-price observations collected and verified by ground staff.

OpenDOSM states that PriceCatcher contains **over one million records per month**, with more than two million prices collected monthly.

Catalogue:
https://open.dosm.gov.my/data-catalogue/pricecatcher

Monthly Parquet pattern:
`https://storage.data.gov.my/pricecatcher/pricecatcher_YYYY-MM.parquet`

### 2. PriceCatcher item lookup
Maps `item_code` to item name, unit, group and category.

https://open.dosm.gov.my/data-catalogue/lookup_item

### 3. PriceCatcher premise lookup
Maps `premise_code` to premise name, type, state and district.

https://open.dosm.gov.my/data-catalogue/lookup_premise

### 4. State CPI inflation
Used only as contextual evidence. PriceCatcher is a **price-surveillance dataset, not an inflation index**.

https://open.dosm.gov.my/data-catalogue/cpi_state_inflation

## Important evidence boundary

OpenDOSM explicitly cautions that PriceCatcher is excellent for **high-frequency analysis of specific items in specific locations**, but inflation analysis requires the CPI methodology.

This repository therefore:
- analyses **observed price distributions**;
- uses CPI only for macro context;
- does **not** calculate an alternative inflation rate from PriceCatcher;
- does not infer market misconduct from a statistical anomaly.

## Technical design

The workflow uses:

- **DuckDB SQL** for high-volume Parquet processing;
- **Python** for orchestration, validation, robust statistics and visualisation;
- **R** for an independent replication of the state price-gap calculation;
- **pytest** for calculation tests;
- **GitHub Actions** for continuous integration.

## Core measures

### State median price
For each selected item and month, the state median is used instead of the mean because retail-price distributions can contain outliers.

### Price dispersion
Within a state-item-month group:

`dispersion = IQR(price) / median(price)`

This is a scale-adjusted measure. A larger value means the middle 50% of observed prices are more spread out.

### State-to-national price gap

`price_gap = state_median / national_median - 1`

A positive gap means the state median observed price is above the national median for the same item and month.

### Robust anomaly score

For an item's state-month median series:

`robust_z = 0.6745 × (x - median) / MAD`

where MAD is the median absolute deviation.

A large robust-z score identifies an unusual observation relative to that state's own series. It is a **screening flag**, not proof of an economic shock or pricing problem.

## Policy triage

An observation is flagged for review when it meets transparent conditions such as:

- sufficient sample coverage;
- state median materially above the national median; and/or
- high within-state dispersion; and/or
- large robust deviation from the state's own recent history.

The output keeps the reasons for each flag visible.

## Why no predictive black box?

The policy task is surveillance and diagnosis, not price forecasting for its own sake.

A black-box model might improve predictive accuracy while making it harder to explain why a state-item observation was flagged. This project therefore prioritises:
- interpretable robust statistics;
- explicit thresholds;
- coverage checks;
- traceable SQL;
- reproducible evidence.

## Repository structure

```text
.
├── config/
│   └── items.json
├── src/
│   ├── download.py
│   ├── build_panel.py
│   ├── diagnostics.py
│   └── visualize.py
├── sql/
│   └── aggregate_prices.sql
├── notebooks/
│   └── 01_price_dispersion_policy_analysis.ipynb
├── R/
│   └── replicate_price_gap.R
├── tests/
│   └── test_diagnostics.py
├── docs/
│   ├── methodology.md
│   └── policy_note.md
├── data/
│   ├── raw/
│   └── processed/
├── reports/
│   └── figures/
└── .github/workflows/ci.yml
```

## Running the project

Install:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Download six months of PriceCatcher data:

```bash
python src/download.py --months 2026-05 2026-06 2026-07 2026-08 2026-09 2026-10
```

Build the analytical panel:

```bash
python src/build_panel.py
python src/diagnostics.py
python src/visualize.py
pytest -q
```

Then open:

```bash
jupyter notebook notebooks/01_price_dispersion_policy_analysis.ipynb
```

## Data governance choices

Raw source data are not committed to GitHub because of their size. The repository stores:
- source URLs;
- requested months;
- transformation code;
- selected-item configuration;
- processed analytical outputs;
- tests.

This keeps the repository lightweight while preserving reproducibility.

## Author

**Farah Ainaa Baharudin**  
Policy Data Science | Decision Intelligence | Data Governance | Evidence-Based Research

Prepared as a public code portfolio. No confidential client or project data are used.


## Streamlit dashboard

The public dashboard is intentionally separated from the heavy raw-data pipeline.

Run the local analytical pipeline first:

```bash
python src/download.py --months 2026-05 2026-06 2026-07 2026-08 2026-09 2026-10
python src/build_panel.py
python src/diagnostics.py
python src/visualize.py
pytest -q
```

This creates:

`data/processed/state_item_month_diagnostics.csv`

Commit that compact processed file to GitHub, while leaving the large raw
PriceCatcher Parquet files excluded.

Then launch locally:

```bash
streamlit run streamlit_app.py
```

For Streamlit Community Cloud, use `streamlit_app.py` as the app entrypoint.
