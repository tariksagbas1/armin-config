---
name: calculate-market-saturation
description: Calculates ten rating-count proxy HHIs and two store averages by searching five keywords across Apple App Store and Google Play.
---

# Execution

Extract exactly five unique market keywords and optional storefront settings,
then run:

```bash
python3 "{baseDir}/scripts/calculate_market_saturation.py" \
  "<keyword-1>" "<keyword-2>" "<keyword-3>" "<keyword-4>" "<keyword-5>" \
  [--limit <1-20>] \
  [--app-store-country <country>] \
  [--play-store-country <country>] \
  [--play-store-language <language>] \
  [--dominance-threshold <percent>] \
  [--request-timeout <seconds>] \
  [--detail-delay <seconds>]
```

# Defaults

- Maximum apps per keyword and store: `20`
- Apple App Store country: `us`
- Google Play country: `us`
- Google Play language: `en`
- Dominance threshold: strictly above `30%`
- Google Play detail-request delay: `0` seconds

# Calculation

For each keyword and each store:

1. Search for up to the configured number of apps.
2. Use Apple `userRatingCount` and Google Play `ratings` as the consistent
   rating-count proxy.
3. Calculate each app's proxy share as its rating count divided by the total
   rating count of all returned apps.
4. Calculate proxy HHI as the sum of squared percentage shares.
5. Return app name, ID, rating count, and share only for apps whose share is
   strictly above the dominance threshold.

The script returns five Apple keyword HHIs, five Google Play keyword HHIs, the
arithmetic average of the five Apple scores, and the arithmetic average of the
five Google Play scores.

# Output Rules

- Return the JSON numbers without recommendations or market interpretation.
- Keep Apple and Google Play results separate.
- State how many apps were analyzed for each keyword.
- Do not describe rating-count proxy HHI as actual revenue or market-share HHI.
- If a keyword has no rating data, its HHI is `null` and it is excluded from
  that store's average; report the number of keyword scores included.

# Example

```bash
python3 "{baseDir}/scripts/calculate_market_saturation.py" \
  "habit tracker" "budget planner" "meal planner" "focus timer" "sleep sounds" \
  --limit 20 \
  --app-store-country us \
  --play-store-country us \
  --play-store-language en \
  --dominance-threshold 30
```
