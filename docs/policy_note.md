# Policy Note: Use High-Frequency Prices to Ask Better Questions

## Decision question

Where should analysts investigate unusually high or dispersed prices for essential goods without mistaking surveillance data for an inflation index?

## The analytical problem

National averages are useful but can hide local variation.

A consumer in one district does not face the national median price. At the same time, a high observed price may reflect:
- premise type;
- product specification;
- transport costs;
- temporary shortages;
- promotion cycles;
- uneven sample coverage.

A useful monitoring system must therefore distinguish **signal** from **conclusion**.

## Proposed approach

Use PriceCatcher for high-frequency screening of specific items and locations.

For each item and month:
1. estimate the state median;
2. measure within-state dispersion using IQR / median;
3. compare the state median with the national median;
4. compare the state with its own recent history using a robust anomaly score;
5. require minimum coverage before raising a flag.

## What a flag means

A flag means:

> **Investigate this observation.**

It does not mean:

> **A market failure has been proven.**

The next step should examine premise mix, item specification, district distribution, supply conditions and data quality.

## Potential policy uses

The monitor could support:
- prioritisation of manual price review;
- identification of persistent geographic price gaps;
- monitoring of selected essential goods;
- evaluation of whether anomalies are isolated or recurrent;
- evidence selection for deeper competition, logistics or affordability studies.

## Governance requirement

Thresholds should be documented, version-controlled and reviewed periodically.

If the monitor is used operationally, every alert should retain:
- source month;
- item code and unit;
- observation count;
- premise coverage;
- reason for flag;
- analyst disposition.

This creates a traceable decision record rather than a black-box alerting system.
