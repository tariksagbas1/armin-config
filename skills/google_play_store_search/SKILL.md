---
name: google-play-store-search
description: Searches Google Play for a requested number of competing apps and returns their install ranges, ratings, and app IDs.
---

# Execution
Extract the market niche or search term and requested result count from the
user's request, then run:

`python3 "{baseDir}/search_play_store.py" "<keyword>" <count>`

Replace `<keyword>` with the user's search term and `<count>` with a positive
integer. Use 10 when the user does not specify a result count.

# Market Analysis Guidelines
When evaluating the returned JSON data:
1. **Demand Signal:** Look for niches where top apps have **100k+ or 1M+ installs**.
2. **Opportunity Gap:** Look for top-ranked apps with an average score **below 3.8 stars**. A high-install app with poor ratings means users need the product, but current implementations are failing them.
3. **App ID Tracking:** Keep track of the `appId` values (e.g., `com.example.app`). You will use these IDs to scrape negative reviews in follow-up analyses.