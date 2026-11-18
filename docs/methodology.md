# Methodology

## Research purpose

This is a **surveillance and diagnostic** project, not an inflation-estimation exercise.

The analysis asks where observed retail prices for selected items:
- differ materially from national medians;
- show unusually wide local dispersion; or
- deviate strongly from recent local history.

## Why median and IQR?

Retail-price data can contain:
- promotions;
- unusual package specifications;
- data errors;
- extreme premises.

The median and interquartile range reduce sensitivity to extremes.

## Why robust z-scores?

A conventional z-score uses the mean and standard deviation, which can themselves be distorted by an extreme observation.

The robust score uses the median and median absolute deviation (MAD).

Retail prices can repeat frequently, which can make MAD equal to zero even when one or two observations differ. To avoid silently assigning zero anomaly scores in that case, the implementation uses an explicit hierarchy:

1. MAD as the preferred robust scale;
2. IQR / 1.349 if MAD is zero;
3. sample standard deviation only if both robust scales collapse but the series still varies.

A constant series receives a zero score. The fallback used should be documented when the method is operationalised.

The score is used only when a state-item time series has enough observations to make comparison meaningful.

## Coverage gate

A statistical flag is not generated unless the state-item-month group contains at least:
- 30 price observations; and
- 5 distinct premises.

These thresholds are analytical defaults, not official standards. They are deliberately easy to find and edit.

## Thresholds

The default screening thresholds are:

- state median >= 10% above national median;
- IQR / median >= 15%;
- |robust z| >= 3.5.

A review-priority flag requires at least two signals.

Thresholds are **screening parameters**, not policy rules. Sensitivity analysis should be conducted before operational use.

## What the method cannot establish

A flag does not identify:
- profiteering;
- anti-competitive behaviour;
- supply disruption;
- household affordability;
- causal effects.

Those questions require additional evidence.

## Why CPI remains separate

PriceCatcher is a price-surveillance system. CPI is designed for inflation measurement using a representative basket and weights.

The repository therefore does not aggregate PriceCatcher observations into a pseudo-CPI.
