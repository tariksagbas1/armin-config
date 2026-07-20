---
name: app-store-search
description: Searches the Apple App Store by keyword and returns apps with their IDs, developers, ratings, review counts, and prices.
---

# Execution

Extract the search keyword, country, and requested result count from the user's
request, then run:

```bash
python3 "{baseDir}/scripts/search_app_store.py" "<keyword>" \
  --country <country> \
  --limit <limit>
```

- `<keyword>` is the App Store search term.
- `--country` is a two-letter App Store country code. Use `us` when the user
  does not specify a country.
- `--limit` is the number of results from 1 to 200. Use `10` when the user
  does not specify a limit.

Always state the selected country because rankings, ratings, review counts,
availability, and prices can differ between storefronts.

# Market Analysis Guidelines

When evaluating the returned JSON:

1. Use `reviews_count` as a demand and market-presence signal.
2. Use `score` with `reviews_count`; a high score based on very few ratings is
   weak evidence.
3. Compare prices to identify free, paid, and premium competitors.
4. Keep each `appId` for follow-up app details or review analysis.
5. Do not claim install or revenue figures because Apple's public search API
   does not provide them.
6. Report the sample size, country, leading competitors, and a short
   data-backed conclusion.
