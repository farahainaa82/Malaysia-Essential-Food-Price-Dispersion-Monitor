# Replicate the state-to-national price-gap calculation in base R.
# Run after Python creates data/processed/state_item_month_panel.csv.

path <- "data/processed/state_item_month_panel.csv"
df <- read.csv(path, stringsAsFactors = FALSE)

df$recalc_gap <- df$price_median / df$national_price_median - 1
df$gap_difference <- df$recalc_gap - df$state_to_national_gap

cat("Maximum absolute replication difference:\n")
print(max(abs(df$gap_difference), na.rm = TRUE))

stopifnot(max(abs(df$gap_difference), na.rm = TRUE) < 1e-10)
