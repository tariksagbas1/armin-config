import argparse
import csv
import io
import json
import re
import urllib.parse
from math import isclose
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


GOOGLE_PROPERTIES = {
    "web": "",
    "images": "images",
    "news": "news",
    "youtube": "youtube",
    "shopping": "froogle",
}
DEFAULT_PROFILE_DIR = Path(__file__).resolve().parents[1] / ".browser-profile"


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def non_negative_integer(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def non_negative_number(value):
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def growth_percent(first_average, last_average):
    if isclose(first_average, 0):
        return 0.0 if isclose(last_average, 0) else None
    return round(
        ((last_average - first_average) / first_average) * 100,
        2,
    )


def trend_direction(growth, threshold):
    if growth is None:
        return "UNDEFINED"
    if growth > threshold:
        return "UPWARD"
    if growth < -threshold:
        return "DOWNWARD"
    return "STABLE"


def parse_score(value):
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned.startswith("<"):
        return 0

    match = re.search(r"-?\d+(?:\.\d+)?", cleaned.replace(",", "."))
    if not match:
        return None
    return round(float(match.group()), 2)


def find_data_header(rows):
    for index, row in enumerate(rows):
        populated = [cell.strip() for cell in row if cell.strip()]
        if len(populated) >= 2:
            return index
    raise ValueError("Downloaded CSV does not contain a data table")


def parse_interest_csv(csv_text, keywords):
    rows = list(csv.reader(io.StringIO(csv_text.lstrip("\ufeff"))))
    header_index = find_data_header(rows)
    header = rows[header_index]

    if len(header) - 1 < len(keywords):
        raise ValueError(
            "Downloaded CSV contains fewer keyword columns than requested"
        )

    points_by_keyword = {keyword: [] for keyword in keywords}
    for row in rows[header_index + 1:]:
        if not row or not row[0].strip():
            continue

        date_label = row[0].strip()
        for column, keyword in enumerate(keywords, start=1):
            if column >= len(row):
                continue
            score = parse_score(row[column])
            if score is None:
                continue
            points_by_keyword[keyword].append({
                "date": date_label,
                "score": score,
            })

    if not any(points_by_keyword.values()):
        raise ValueError("Downloaded CSV contains no trend scores")
    return points_by_keyword


def analyze_keyword(points, keyword, recent_points, comparison_points, threshold):
    if not points:
        return {"keyword": keyword, "status": "no_data_found"}

    values = [point["score"] for point in points]
    comparison_size = min(comparison_points, len(values))
    first_average = round(
        sum(values[:comparison_size]) / comparison_size,
        2,
    )
    last_average = round(
        sum(values[-comparison_size:]) / comparison_size,
        2,
    )
    growth = growth_percent(first_average, last_average)

    return {
        "keyword": keyword,
        "status": "ok",
        "pointsAnalyzed": len(values),
        "currentInterestScore": values[-1],
        "averageInterestScore": round(sum(values) / len(values), 2),
        "firstWindowAverage": first_average,
        "lastWindowAverage": last_average,
        "growthPercent": growth,
        "trendDirection": trend_direction(growth, threshold),
        "recentScores": points[-recent_points:],
    }


def build_explore_url(args):
    geo = "" if args.geo.lower() == "worldwide" else args.geo.upper()
    params = {
        "q": ",".join(args.keywords),
        "date": args.timeframe,
        "hl": args.language,
        "tz": args.timezone,
    }
    if geo:
        params["geo"] = geo
    if args.category:
        params["cat"] = args.category
    if GOOGLE_PROPERTIES[args.property]:
        params["gprop"] = GOOGLE_PROPERTIES[args.property]

    query = urllib.parse.urlencode(params)
    return f"https://trends.google.com/trends/explore?{query}", geo


def find_export_button(page, timeout_ms):
    selectors = [
        "button.export:visible",
        'button[aria-label*="Download"]:visible',
        'button[aria-label*="download"]:visible',
        'button[aria-label*="İndir"]:visible',
    ]

    deadline_per_selector = max(timeout_ms // len(selectors), 1_000)
    for selector in selectors:
        try:
            locator = page.locator(selector)
            locator.first.wait_for(
                state="visible",
                timeout=deadline_per_selector,
            )
            return locator.first
        except PlaywrightTimeoutError:
            continue

    raise RuntimeError(
        "Interest-over-time download button was not found. "
        "Complete any consent or verification screen in the browser and retry."
    )


def download_interest_csv(args, explore_url):
    profile_dir = Path(args.profile_dir).expanduser().resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)
    timeout_ms = args.browser_timeout * 1_000

    with sync_playwright() as playwright:
        launch_options = {
            "user_data_dir": str(profile_dir),
            "headless": args.headless,
            "accept_downloads": True,
            "slow_mo": args.slow_mo,
            "viewport": {"width": 1440, "height": 1000},
        }
        if args.browser_channel != "chromium":
            launch_options["channel"] = args.browser_channel

        context = playwright.chromium.launch_persistent_context(
            **launch_options
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            response = None
            for attempt in range(args.browser_retries + 1):
                response = page.goto(
                    explore_url,
                    wait_until="domcontentloaded",
                    timeout=timeout_ms,
                )
                if not response or response.status != 429:
                    break
                if attempt < args.browser_retries:
                    page.wait_for_timeout(args.retry_delay * 1_000)

            if response and response.status == 429:
                raise RuntimeError(
                    "Google returned HTTP 429 after browser retries"
                )

            button = find_export_button(page, timeout_ms)
            button.scroll_into_view_if_needed()

            with page.expect_download(timeout=timeout_ms) as download_info:
                button.click()

            download = download_info.value
            failure = download.failure()
            if failure:
                raise RuntimeError(f"Google Trends CSV download failed: {failure}")

            download_path = download.path()
            if not download_path:
                raise RuntimeError("Browser download did not produce a file")
            return Path(download_path).read_text(
                encoding="utf-8-sig",
            )
        finally:
            context.close()


def create_parser():
    parser = argparse.ArgumentParser(
        description="Fetch Google Trends data through a visible browser"
    )
    parser.add_argument(
        "keywords",
        nargs="+",
        help="One to five search terms; quote terms containing spaces",
    )
    parser.add_argument(
        "--geo",
        default="US",
        help="Region such as US, TR, or DE; use worldwide for global",
    )
    parser.add_argument(
        "--timeframe",
        default="today 12-m",
        help="Google Trends timeframe (default: today 12-m)",
    )
    parser.add_argument(
        "--category",
        type=non_negative_integer,
        default=0,
        help="Google Trends category ID; 0 means all categories",
    )
    parser.add_argument(
        "--language",
        default="en-US",
        help="Interface locale such as en-US or tr-TR (default: en-US)",
    )
    parser.add_argument(
        "--timezone",
        type=int,
        default=360,
        help="UTC offset in minutes expected by Google Trends (default: 360)",
    )
    parser.add_argument(
        "--property",
        choices=GOOGLE_PROPERTIES,
        default="web",
        help="Search property (default: web)",
    )
    parser.add_argument(
        "--recent-points",
        type=positive_integer,
        default=12,
        help="Recent data points included in output (default: 12)",
    )
    parser.add_argument(
        "--comparison-points",
        type=positive_integer,
        default=12,
        help="Points used in first/last growth windows (default: 12)",
    )
    parser.add_argument(
        "--direction-threshold",
        type=non_negative_number,
        default=15,
        help="Growth percentage used to label direction (default: 15)",
    )
    parser.add_argument(
        "--profile-dir",
        default=str(DEFAULT_PROFILE_DIR),
        help="Persistent browser profile directory",
    )
    parser.add_argument(
        "--browser-channel",
        choices=["chromium", "chrome", "msedge"],
        default="chrome",
        help="Installed browser channel (default: chrome)",
    )
    parser.add_argument(
        "--browser-timeout",
        type=positive_integer,
        default=120,
        help="Seconds allowed for page load and interaction (default: 120)",
    )
    parser.add_argument(
        "--slow-mo",
        type=non_negative_integer,
        default=100,
        help="Delay between browser actions in milliseconds (default: 100)",
    )
    parser.add_argument(
        "--browser-retries",
        type=non_negative_integer,
        default=2,
        help="Navigation retries when Google returns 429 (default: 2)",
    )
    parser.add_argument(
        "--retry-delay",
        type=non_negative_integer,
        default=3,
        help="Seconds between browser navigation retries (default: 3)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without a visible browser; visible mode is the default",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if len(args.keywords) > 5:
        parser.error("Google Trends supports at most five keywords per query")

    explore_url, geo = build_explore_url(args)

    try:
        csv_text = download_interest_csv(args, explore_url)
        points_by_keyword = parse_interest_csv(csv_text, args.keywords)

        output = {
            "query": {
                "keywords": args.keywords,
                "geo": geo or "worldwide",
                "timeframe": args.timeframe,
                "category": args.category,
                "language": args.language,
                "timezone": args.timezone,
                "property": args.property,
                "recentPoints": args.recent_points,
                "comparisonPoints": args.comparison_points,
                "directionThresholdPercent": args.direction_threshold,
            },
            "source": {
                "type": "google_trends_browser_csv",
                "url": explore_url,
                "headless": args.headless,
            },
            "scoreScale": {
                "minimum": 0,
                "maximum": 100,
                "type": "relative_search_interest",
            },
            "results": [
                analyze_keyword(
                    points_by_keyword[keyword],
                    keyword,
                    args.recent_points,
                    args.comparison_points,
                    args.direction_threshold,
                )
                for keyword in args.keywords
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))

    except Exception as error:
        message = str(error)
        if "Executable doesn't exist" in message:
            message += (
                ". Install Chromium with: "
                "python3 -m playwright install chromium"
            )
        print(json.dumps({"error": message}))
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
