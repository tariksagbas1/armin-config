---
name: google-trends
description: Opens Google Trends in a browser and exports interest-over-time scores for up to five configurable keywords.
---

# Setup

This skill uses Playwright with an installed Google Chrome browser by default.
If Chrome is unavailable, install Playwright's Chromium browser:

```bash
python3 -m playwright install chromium
```

The script opens a visible browser by default and keeps cookies in
`{baseDir}/.browser-profile`. On the first run, complete any Google consent or
verification screen in the browser. The profile is reused on later runs.

# Execution

Extract the requested keywords and optional query settings, then run:

```bash
python3 "{baseDir}/scripts/get_google_trends.py" \
  "<keyword-1>" ["<keyword-2>" ...] \
  [--geo <region>] \
  [--timeframe "<timeframe>"] \
  [--category <id>] \
  [--language <locale>] \
  [--timezone <minutes>] \
  [--property <property>] \
  [--recent-points <count>] \
  [--comparison-points <count>] \
  [--direction-threshold <percent>] \
  [--browser-channel <channel>] \
  [--browser-timeout <seconds>] \
  [--slow-mo <milliseconds>] \
  [--browser-retries <count>] \
  [--retry-delay <seconds>] \
  [--data-wait <seconds>] \
  [--headless]
```

# Parameters

- Keywords: one to five terms. Quote terms containing spaces.
- `--geo`: region such as `US`, `TR`, or `DE`; use `worldwide` for global.
  Default: `US`.
- `--timeframe`: examples include `now 7-d`, `today 3-m`, `today 12-m`,
  `today 5-y`, `all`, or `"2026-01-01 2026-07-20"`. Default:
  `today 12-m`.
- `--category`: Google Trends category ID. Default: `0` (all).
- `--language`: interface locale such as `en-US` or `tr-TR`. Default:
  `en-US`.
- `--timezone`: UTC offset in minutes in Google Trends format. Default: `360`.
- `--property`: `web`, `images`, `news`, `youtube`, or `shopping`. Default:
  `web`.
- `--recent-points`: recent dated scores returned. Default: `12`.
- `--comparison-points`: points in the first and last growth windows. Default:
  `12`.
- `--direction-threshold`: percentage boundary for upward, stable, or downward
  labels. Default: `15`.
- `--browser-channel`: `chromium`, `chrome`, or `msedge`. Default: `chrome`.
- `--browser-timeout`: page/download timeout. Default: `120` seconds.
- `--slow-mo`: delay between browser actions. Default: `100` milliseconds.
- Browser navigation retries default to `2`, with `3` seconds between attempts.
- Chart-data wait defaults to `5` seconds before each CSV export attempt.
- `--headless`: disables the visible browser. Do not use it when Google blocks
  headless sessions.

# Output Rules

- The script loads the rendered Google Trends page and downloads the
  Interest-over-time CSV from its export button.
- Return the numerical JSON output without commentary unless the user asks for
  analysis.
- State that scores are relative interest values from 0 to 100, not absolute
  search volume.
- Preserve the query region, timeframe, category, property, point count, and
  partial-data handling shown in the output.
- When multiple keywords are queried together, report them as one normalized
  comparison set.

# Example

```bash
python3 "{baseDir}/scripts/get_google_trends.py" \
  "habit tracker" "budget planner" \
  --geo TR \
  --timeframe "today 12-m" \
  --property web \
  --recent-points 12 \
  --comparison-points 12
```
