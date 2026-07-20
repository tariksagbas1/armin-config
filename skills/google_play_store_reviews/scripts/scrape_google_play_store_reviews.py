import argparse
import json
from datetime import date, timedelta

from google_play_scraper import Sort, reviews


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def iso_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "must use YYYY-MM-DD format"
        ) from error


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and filter Google Play Store reviews"
    )
    parser.add_argument("app_id", help="Google Play package ID")
    parser.add_argument(
        "--rating-threshold",
        type=int,
        choices=range(1, 6),
        help="Include reviews at or below this rating (default: all ratings)",
    )
    parser.add_argument(
        "--country",
        default="us",
        help="Two-letter Google Play country code (default: us)",
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Google Play language code (default: en)",
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
        type=positive_integer,
        default=50,
        help="Number of reviews to fetch before filtering (default: 50)",
    )
    parser.add_argument(
        "--min-thumbs-up",
        type=positive_integer,
        help="Include reviews with at least this many thumbs-up votes",
    )
    args = parser.parse_args()

    if args.start_date and args.end_date and args.start_date > args.end_date:
        parser.error("--start-date must be on or before --end-date")

    try:
        result, _ = reviews(
            args.app_id,
            lang=args.lang.lower(),
            country=args.country.lower(),
            sort=Sort.MOST_RELEVANT,
            count=args.count,
        )

        clean_reviews = []
        for review in result:
            score = review.get("score")
            reviewed_at = review.get("at")
            reviewed_on = reviewed_at.date() if reviewed_at else None
            thumbs_up = review.get("thumbsUpCount") or 0

            if score is None:
                continue
            if (
                args.rating_threshold is not None
                and score > args.rating_threshold
            ):
                continue
            if args.start_date and (
                reviewed_on is None or reviewed_on < args.start_date
            ):
                continue
            if args.end_date and (
                reviewed_on is None or reviewed_on > args.end_date
            ):
                continue
            if args.min_thumbs_up is not None and thumbs_up < args.min_thumbs_up:
                continue

            clean_reviews.append({
                "score": score,
                "date": reviewed_on.isoformat() if reviewed_on else None,
                "review": review.get("content"),
                "thumbsUp": thumbs_up,
            })

        print(json.dumps({
            "appId": args.app_id,
            "filters": {
                "ratingThreshold": args.rating_threshold,
                "country": args.country.lower(),
                "language": args.lang.lower(),
                "startDate": (
                    args.start_date.isoformat() if args.start_date else None
                ),
                "endDate": args.end_date.isoformat() if args.end_date else None,
                "requestedCount": args.count,
                "minThumbsUp": args.min_thumbs_up,
            },
            "totalFetched": len(result),
            "totalMatching": len(clean_reviews),
            "reviews": clean_reviews,
        }, indent=2, ensure_ascii=False))

    except Exception as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()