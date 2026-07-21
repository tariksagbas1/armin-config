import argparse
import json
import math
import time
import urllib.parse
import urllib.request

from google_play_scraper import app as google_play_app
from google_play_scraper import search as google_play_search


def result_limit(value):
    limit = int(value)
    if not 1 <= limit <= 20:
        raise argparse.ArgumentTypeError("must be between 1 and 20")
    return limit


def percentage(value):
    number = float(value)
    if not 0 <= number <= 100:
        raise argparse.ArgumentTypeError("must be between 0 and 100")
    return number


def non_negative_number(value):
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def search_app_store(keyword, country, limit, timeout):
    query = urllib.parse.urlencode({
        "term": keyword,
        "entity": "software",
        "country": country.lower(),
        "limit": limit,
    })
    request = urllib.request.Request(
        f"https://itunes.apple.com/search?{query}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    apps = []
    seen_ids = set()
    for result in payload.get("results", []):
        app_id = result.get("trackId")
        if app_id is None or app_id in seen_ids:
            continue
        seen_ids.add(app_id)
        apps.append({
            "appId": str(app_id),
            "name": result.get("trackName") or str(app_id),
            "ratingCount": int(result.get("userRatingCount") or 0),
        })
    return apps[:limit]


def search_google_play(keyword, country, language, limit, detail_delay):
    search_results = google_play_search(
        keyword,
        n_hits=limit,
        lang=language.lower(),
        country=country.lower(),
    )

    apps = []
    seen_ids = set()
    for result in search_results:
        app_id = result.get("appId")
        if not app_id or app_id in seen_ids:
            continue
        seen_ids.add(app_id)

        details = google_play_app(
            app_id,
            lang=language.lower(),
            country=country.lower(),
        )
        apps.append({
            "appId": app_id,
            "name": details.get("title") or result.get("title") or app_id,
            "ratingCount": int(details.get("ratings") or 0),
        })
        if detail_delay:
            time.sleep(detail_delay)
    return apps[:limit]


def calculate_keyword_hhi(keyword, apps, dominance_threshold):
    total_rating_count = sum(app["ratingCount"] for app in apps)
    if total_rating_count <= 0:
        return {
            "keyword": keyword,
            "appsAnalyzed": len(apps),
            "totalRatingCount": total_rating_count,
            "proxyHhi": None,
            "appsAboveThreshold": [],
            "status": "no_rating_data",
        }

    hhi = 0.0
    apps_above_threshold = []
    for app in apps:
        share = (app["ratingCount"] / total_rating_count) * 100
        hhi += share ** 2
        if share > dominance_threshold:
            apps_above_threshold.append({
                "name": app["name"],
                "appId": app["appId"],
                "ratingCount": app["ratingCount"],
                "marketSharePercent": round(share, 4),
            })

    apps_above_threshold.sort(
        key=lambda app: app["marketSharePercent"],
        reverse=True,
    )
    return {
        "keyword": keyword,
        "appsAnalyzed": len(apps),
        "totalRatingCount": total_rating_count,
        "proxyHhi": round(hhi, 2),
        "appsAboveThreshold": apps_above_threshold,
        "status": "ok",
    }


def average_hhi(keyword_results):
    scores = [
        result["proxyHhi"]
        for result in keyword_results
        if result["proxyHhi"] is not None
    ]
    return {
        "averageProxyHhi": (
            round(sum(scores) / len(scores), 2)
            if scores
            else None
        ),
        "keywordScoresIncluded": len(scores),
        "keywordScoresRequested": len(keyword_results),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate five-keyword saturation HHIs for both app stores"
    )
    parser.add_argument(
        "keywords",
        nargs=5,
        help="Exactly five market keywords; quote terms containing spaces",
    )
    parser.add_argument(
        "--limit",
        type=result_limit,
        default=20,
        help="Maximum apps fetched per keyword and store (default: 20)",
    )
    parser.add_argument(
        "--app-store-country",
        default="us",
        help="Apple App Store country code (default: us)",
    )
    parser.add_argument(
        "--play-store-country",
        default="us",
        help="Google Play country code (default: us)",
    )
    parser.add_argument(
        "--play-store-language",
        default="en",
        help="Google Play language code (default: en)",
    )
    parser.add_argument(
        "--dominance-threshold",
        type=percentage,
        default=30,
        help="Print apps with a proxy share above this percent (default: 30)",
    )
    parser.add_argument(
        "--request-timeout",
        type=non_negative_number,
        default=20,
        help="Apple API timeout in seconds (default: 20)",
    )
    parser.add_argument(
        "--detail-delay",
        type=non_negative_number,
        default=0,
        help="Delay between Google Play app-detail requests (default: 0)",
    )
    args = parser.parse_args()

    normalized_keywords = [keyword.strip() for keyword in args.keywords]
    if any(not keyword for keyword in normalized_keywords):
        parser.error("keywords cannot be empty")
    if len({keyword.casefold() for keyword in normalized_keywords}) != 5:
        parser.error("keywords must be unique")
    if math.isclose(args.request_timeout, 0):
        parser.error("--request-timeout must be greater than zero")

    try:
        app_store_results = []
        play_store_results = []

        for keyword in normalized_keywords:
            app_store_apps = search_app_store(
                keyword,
                args.app_store_country,
                args.limit,
                args.request_timeout,
            )
            app_store_results.append(calculate_keyword_hhi(
                keyword,
                app_store_apps,
                args.dominance_threshold,
            ))

            play_store_apps = search_google_play(
                keyword,
                args.play_store_country,
                args.play_store_language,
                args.limit,
                args.detail_delay,
            )
            play_store_results.append(calculate_keyword_hhi(
                keyword,
                play_store_apps,
                args.dominance_threshold,
            ))

        output = {
            "keywords": normalized_keywords,
            "settings": {
                "maxAppsPerKeyword": args.limit,
                "dominanceThresholdPercent": args.dominance_threshold,
                "appStoreCountry": args.app_store_country.lower(),
                "playStoreCountry": args.play_store_country.lower(),
                "playStoreLanguage": args.play_store_language.lower(),
                "shareMetric": "storefront_rating_count",
            },
            "appStore": {
                **average_hhi(app_store_results),
                "keywordResults": app_store_results,
            },
            "googlePlay": {
                **average_hhi(play_store_results),
                "keywordResults": play_store_results,
            },
            "scoreCount": {
                "individualProxyHhiRequested": 10,
                "averageProxyHhiRequested": 2,
            },
            "limitations": [
                "Rating counts are proxy metrics, not verified market shares.",
                "Each HHI is normalized only across returned search results.",
                "Search ranking and storefront selection affect the result.",
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False))

    except Exception as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
