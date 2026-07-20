import argparse
import json
import urllib.parse
import urllib.request


def result_limit(value):
    limit = int(value)
    if not 1 <= limit <= 200:
        raise argparse.ArgumentTypeError("must be between 1 and 200")
    return limit

def main():
    parser = argparse.ArgumentParser(description="Search the Apple App Store")
    parser.add_argument("keyword", help="App Store search term")
    parser.add_argument(
        "--country",
        default="us",
        help="Two-letter App Store country code (default: us)",
    )
    parser.add_argument(
        "--limit",
        type=result_limit,
        default=10,
        help="Number of results from 1 to 200 (default: 10)",
    )
    args = parser.parse_args()

    query = urllib.parse.urlencode({
        "term": args.keyword,
        "entity": "software",
        "country": args.country.lower(),
        "limit": args.limit,
    })
    url = f"https://itunes.apple.com/search?{query}"
    
    try:
        # We pass a User-Agent so Apple doesn't block the request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        results = data.get("results", [])
        
        clean_results = []
        for r in results:
            clean_results.append({
                "title": r.get("trackName"),
                "appId": str(r.get("trackId")),
                "developer": r.get("sellerName"),
                "score": round(r.get("averageUserRating") or 0, 2),
                "reviews_count": r.get("userRatingCount") or 0,
                "price": r.get("formattedPrice")
            })
            
        # Return pure JSON
        print(json.dumps(clean_results, indent=2))
        
    except Exception as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1) from error

if __name__ == "__main__":
    main()