---
name: app-store-reviews
description: Fetches Apple App Store reviews filtered by rating, country, date range, and result count for market analysis.
---

# Execution

Extract the numeric app ID, optional app name, country, rating threshold, date
range, and requested result count from the user's request. The script uses
Python's standard library and does not require third-party packages.

```bash
python3 "{baseDir}/scripts/scrape_ios_reviews.py" \
  "<app-id>" "<app-name>" \
  [--rating-threshold <rating>] \
  [--country <country>] \
  [--start-date <YYYY-MM-DD>] \
  [--end-date <YYYY-MM-DD>] \
  [--count <count>] \
  [--sleep <seconds>]
```

- `<app-id>` is required. `<app-name>` is optional and is used only to label
  the JSON output.
- Omit `--rating-threshold` to include all ratings.
- Use `--rating-threshold 2` for one- and two-star reviews, or
  `--rating-threshold 1` for one-star reviews only.
- Country defaults to `us`.
- Date range defaults to the last 30 days through today.
- `--count` controls how many recent reviews are fetched before rating and date
  filters are applied. It defaults to `50` and supports up to `500`.
- Sleep defaults to `0`.
- Apple does not support an independent review-language filter; the available
  reviews are determined by the selected country storefront.

# Examples

Fetch the 100 most recent available reviews, then return only one- and two-star
reviews from the Turkish storefront within the selected dates:

```bash
python3 "{baseDir}/scripts/scrape_ios_reviews.py" \
  "310633997" "whatsapp-messenger" \
  --rating-threshold 2 \
  --country tr \
  --start-date 2026-06-01 \
  --end-date 2026-07-20 \
  --count 100
```

Fetch 50 reviews using the default US storefront and last-30-days range,
without filtering by rating:

```bash
python3 "{baseDir}/scripts/scrape_ios_reviews.py" "310633997" --count 50
```

# Analysis Guidelines

Report the country, date range, number fetched, number matching, rating filter,
recurring complaint themes, and a short data-backed conclusion. Do not claim
that the returned sample contains every review.
