import sys
import json
from google_play_scraper import search

def main():
    # Verify that a keyword and result count were passed
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Keyword and result count required"}))
        sys.exit(1)

    keyword = sys.argv[1]

    try:
        result_count = int(sys.argv[2])
        if result_count < 1:
            raise ValueError
    except ValueError:
        print(json.dumps({"error": "Result count must be a positive integer"}))
        sys.exit(1)

    try:
        # Fetch the requested number of results for the US Google Play market
        results = search(
            keyword,
            n_hits=result_count,
            lang="en",
            country="us",
        )
        
        clean_results = []
        for r in results:
            clean_results.append({
                "title": r.get("title"),
                "appId": r.get("appId"),
                "developer": r.get("developer"),
                "score": round(r.get("score") or 0, 2),
                "installs": r.get("installs"),
                "is_free": r.get("free")
            })
            
        # Print pure JSON so OpenClaw can feed it directly to DeepSeek
        print(json.dumps(clean_results, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()