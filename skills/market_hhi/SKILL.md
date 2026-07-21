---
name: calculate_proxy_hhi
description: Calculates the Herfindahl-Hirschman Index (HHI) to determine market concentration and monopoly dominance based on proxy metrics like reviews or installs.
parameters:
  type: object
  properties:
    proxy_metrics:
      type: string
      description: A comma-separated list of review counts or install estimates for the top competing apps (e.g., "45000, 12000, 5000, 200, 100").
  required: ["proxy_metrics"]
---

# Execution
To run this tool, execute the following command:
`python3 {baseDir}/scripts/calculate_hhi.py "{{proxy_metrics}}"`

# Market Analysis Guidelines
1. **Gather Data:** First, use the `play_store_search` or `ios_store_search` tools to retrieve the `reviews_count` or `installs` for the top 10 apps in a niche.
2. **Calculate HHI:** Extract those numbers and pass them as a comma-separated string to this tool.
3. **Interpret Output:** 
   - **Low Concentration (HHI < 1500):** Fragmented market. Highly ideal. Proceed with the vulnerability scan.
   - **Moderate Concentration (HHI 1500-2500):** Viable. Proceed, but closely examine the top 2 players.
   - **High Concentration (HHI > 2500):** Monopoly territory. Reject this market entirely unless the dominant player has an average rating below 3.5 stars and glaringly obvious flaws.