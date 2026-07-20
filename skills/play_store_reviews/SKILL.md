---
name: google-play-store-reviews
description: Fetches Google Play reviews filtered by rating, locale, date range, result count, and minimum thumbs-up votes.
---

# Execution

Extract the Google Play app ID from the user's request. If the user provides
an app URL, use the value of its `id` query parameter. Also extract any rating,
country, language, date range, review count, and thumbs-up filters.

Run:

```bash
python3 "{baseDir}/scripts/scrape_google_play_store_reviews.py" "<app-id>" \
  [--rating-threshold <rating>] \
  [--country <country>] \
  [--lang <language>] \
  [--count <count>] \
  [--start-date <YYYY-MM-DD>] \
  [--end-date <YYYY-MM-DD>] \
  [--min-thumbs-up <count>]
```

- `<app-id>` is the package identifier, such as `com.example.app`.
- `--rating-threshold` includes ratings less than or equal to the value. Omit
  it to include all ratings.
- `--country` controls the Play Store market and defaults to `us`.
- `--lang` controls the review language and defaults to `en`.
- `--count` controls how many reviews are fetched before filters are applied.
  It defaults to `50`.
- Date boundaries are inclusive. When omitted, the range defaults dynamically
  to the last 30 days through today.
- `--min-thumbs-up` includes reviews with at least that many votes. Omit it
  when the user does not want a thumbs-up filter.

Google Play requires a locale for each request, so an unfiltered global
country or language request is not available. When the user does not specify a
locale, clearly report that the effective default is US/English. Country and
language are independent: for example, use `--country tr --lang en` for
English reviews in Turkey or `--country us --lang de` for German reviews in
the US.

If no app ID can be determined, ask the user for one.

# Review Analysis Guidelines

When evaluating the returned JSON:

1. Group reviews into recurring complaint themes.
2. Distinguish widespread problems from isolated reports.
3. Prioritize complaints with high `thumbsUp` values.
4. Cite representative review excerpts without inventing details.
5. Report the number of matching reviews analyzed and note when the sample is
   too small to support a strong conclusion.
