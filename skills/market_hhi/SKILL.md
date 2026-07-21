---
name: calculate-hhi
description: Calculates a proxy Herfindahl-Hirschman Index from consistent competitor metrics and returns concentration statistics without recommendations.
---

# Execution

Collect one consistent nonnegative metric for each competitor, then run:

```bash
python3 "{baseDir}/scripts/calculate_hhi.py" \
  "<value-1>,<value-2>,<value-3>" \
  [--labels "<competitor-1>,<competitor-2>,<competitor-3>"] \
  [--metric-name "<metric>"]
```

- Values may be a comma-separated list or a JSON numeric array.
- Do not include thousands separators inside comma-separated values.
- Labels are optional, but their count must equal the value count.
- All values must use the same metric, platform, storefront, and measurement
  basis. Do not mix review counts with install estimates.
- Use as complete a competitor set as possible. A top-N sample omits the long
  tail and can materially overstate concentration.

# Data Sources

Metrics may come from `google-play-store-search` or `app-store-search`. Keep
Google Play and Apple App Store calculations separate. Treat review counts and
install estimates as proxies rather than verified market shares.

# Output

The script returns:

- Proxy HHI on a 0–10,000 scale
- Each competitor's proxy share
- Largest competitor share
- Effective competitor count
- Competitor count and total proxy volume
- A descriptive concentration level using the 2023 DOJ/FTC boundaries:
  - Below 1,000: `UNCONCENTRATED`
  - 1,000 through 1,800: `MODERATELY_CONCENTRATED`
  - Above 1,800: `HIGHLY_CONCENTRATED`

Return these numerical results without market recommendations, opportunity
claims, `GO` / `NO-GO` decisions, or monopoly claims unless the user explicitly
requests interpretation.

# Example

```bash
python3 "{baseDir}/scripts/calculate_hhi.py" \
  "45000,12000,5000,200,100" \
  --labels "App A,App B,App C,App D,App E" \
  --metric-name "review_count"
```
