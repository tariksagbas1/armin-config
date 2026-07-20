---
name: google-play-store-search
description: Searches Google Play for a requested number of competing apps and returns their install ranges, ratings, and app IDs. Supports country-specific search results.
---

# Execution
Extract the market niche or search term, requested result count, and optional
country/language from the user's request, then run:

```bash
python3 "{baseDir}/search_play_store.py" "<keyword>" <count> [--country <cc>] [--lang <lang>]
```

- `<keyword>` — search term (required)
- `<count>` — number of results; use **10** when the user does not specify a count
- `--country <cc>` — two-letter country code (e.g. `us`, `be`, `tr`, `gb`, `sa`). Omit for global/US default.
- `--lang <lang>` — language code (e.g. `en`, `fr`, `tr`, `ar`). Omit for English default.

# Market Analysis Guidelines
When evaluating the returned JSON data:
1. **Demand Signal:** Look for niches where top apps have **100k+ or 1M+ installs**.
2. **Opportunity Gap:** Look for top-ranked apps with an average score **below 3.8 stars**. A high-install app with poor ratings means users need the product, but current implementations are failing them.
3. **App ID Tracking:** Keep track of the `appId` values (e.g., `com.example.app`). You will use these IDs to scrape negative reviews in follow-up analyses.
4. **Regional Variance:** Always mention the country context when presenting results (e.g. "Top Islamic apps in Turkey"). Results can vary significantly by region.