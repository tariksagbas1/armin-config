import argparse
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta


PAGE_SIZE = 50
MAX_PAGES = 10
MAX_REVIEWS = PAGE_SIZE * MAX_PAGES
USER_AGENT = "iTunes/12.0"


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def review_count(value):
    number = positive_integer(value)
    if number > MAX_REVIEWS:
        raise argparse.ArgumentTypeError(
            f"must be between 1 and {MAX_REVIEWS}"
        )
    return number


def non_negative_number(value):
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def iso_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "must use YYYY-MM-DD format"
        ) from error


def country_code(value):
    normalized = value.lower()
    if len(normalized) != 2 or not normalized.isalpha():
        raise argparse.ArgumentTypeError(
            "must be a two-letter country code"
        )
    return normalized


def nested_label(entry, key):
    value = entry.get(key, {})
    return value.get("label") if isinstance(value, dict) else None


def parse_review(entry):
    updated = nested_label(entry, "updated")
    rating = nested_label(entry, "im:rating")
    if not updated or not rating:
        return None

    reviewed_at = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    return {
        "rating": int(rating),
        "date": reviewed_at.date(),
        "title": nested_label(entry, "title"),
        "review": nested_label(entry, "content"),
        "author": nested_label(entry.get("author", {}), "name"),
        "version": nested_label(entry, "im:version"),
        "reviewId": nested_label(entry, "id"),
    }


def fetch_reviews(app_id, country, count, start_date, sleep_seconds):
    collected = []
    page_count = min(math.ceil(count / PAGE_SIZE), MAX_PAGES)

    for page in range(1, page_count + 1):
        path = (
            f"https://itunes.apple.com/{urllib.parse.quote(country)}/rss/"
            f"customerreviews/page={page}/id={app_id}/"
            "sortby=mostrecent/json"
        )
        request = urllib.request.Request(
            path,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))

        entries = payload.get("feed", {}).get("entry", [])
        page_reviews = [
            parsed
            for entry in entries
            if (parsed := parse_review(entry)) is not None
        ]
        if not page_reviews:
            break

        collected.extend(page_reviews)
        if len(collected) >= count:
            break
        if min(item["date"] for item in page_reviews) < start_date:
            break
        if sleep_seconds and page < page_count:
            time.sleep(sleep_seconds)

    return collected[:count]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and filter Apple App Store reviews"
    )
    parser.add_argument("app_id", type=positive_integer, help="Numeric app ID")
    parser.add_argument(
        "app_name",
        nargs="?",
        help="Optional app name used only in the JSON output",
    )
    parser.add_argument(
        "--rating-threshold",
        type=int,
        choices=range(1, 6),
        help="Include reviews at or below this rating (default: all ratings)",
    )
    parser.add_argument(
        "--country",
        type=country_code,
        default="us",
        help="Two-letter App Store country code (default: us)",
    )
    parser.add_argument(
        "--start-date",
        type=iso_date,
        default=date.today() - timedelta(days=30),
        help="Include reviews on or after this date (default: 30 days ago)",
    )
    parser.add_argument(
        "--end-date",
        type=iso_date,
        default=date.today(),
        help="Include reviews on or before this date (default: today)",
    )
    parser.add_argument(
        "--count",
        type=review_count,
        default=50,
        help="Reviews to fetch before filtering, from 1 to 500 (default: 50)",
    )
    parser.add_argument(
        "--sleep",
        type=non_negative_number,
        default=0,
        help="Seconds to wait between requests (default: 0)",
    )
    args = parser.parse_args()

    if args.start_date > args.end_date:
        parser.error("--start-date must be on or before --end-date")

    try:
        fetched_reviews = fetch_reviews(
            app_id=args.app_id,
            country=args.country,
            count=args.count,
            start_date=args.start_date,
            sleep_seconds=args.sleep,
        )

        clean_reviews = []
        for review in fetched_reviews:
            rating = review.get("rating")
            reviewed_on = review.get("date")

            if rating is None:
                continue
            if (
                args.rating_threshold is not None
                and rating > args.rating_threshold
            ):
                continue
            if reviewed_on < args.start_date or reviewed_on > args.end_date:
                continue

            clean_reviews.append({
                "rating": rating,
                "date": reviewed_on.isoformat(),
                "title": review.get("title"),
                "review": review.get("review"),
                "author": review.get("author"),
                "version": review.get("version"),
                "reviewId": review.get("reviewId"),
            })

        print(json.dumps({
            "appId": str(args.app_id),
            "appName": args.app_name,
            "source": "Apple customer reviews RSS",
            "filters": {
                "ratingThreshold": args.rating_threshold,
                "country": args.country,
                "startDate": args.start_date.isoformat(),
                "endDate": args.end_date.isoformat(),
                "requestedCount": args.count,
            },
            "totalFetched": len(fetched_reviews),
            "totalMatching": len(clean_reviews),
            "reviews": clean_reviews,
        }, indent=2, ensure_ascii=False))

    except Exception as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()