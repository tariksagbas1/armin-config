import sys
import json
import argparse
from google_play_scraper import search

def main():
    parser = argparse.ArgumentParser(description="Search Google Play Store")
    parser.add_argument("keyword", type=str, help="Search keyword")
    parser.add_argument("count", type=int, help="Number of results")
    parser.add_argument("--country", type=str, default="us",
                        help="Two-letter country code (us, be, tr, etc.)")
    parser.add_argument("--lang", type=str, default="en",
                        help="Language code (en, fr, tr, etc.)")

    args = parser.parse_args()

    if args.count < 1:
        print(json.dumps({"error": "Result count must be a positive integer"}))
        sys.exit(1)

    try:
        results = search(
            args.keyword,
            n_hits=args.count,
            lang=args.lang,
            country=args.country,
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

        print(json.dumps(clean_results, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()