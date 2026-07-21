import argparse
import json
import math


def parse_values(raw_values):
    try:
        if raw_values.lstrip().startswith("["):
            parsed = json.loads(raw_values)
            if not isinstance(parsed, list):
                raise ValueError("values JSON must be an array")
        else:
            parsed = [
                value.strip()
                for value in raw_values.split(",")
                if value.strip()
            ]
        values = [float(value) for value in parsed]
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(
            "values must be a comma-separated list or JSON array of numbers"
        ) from error

    if not values:
        raise ValueError("at least one proxy metric value is required")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("values must be finite numbers")
    if any(value < 0 for value in values):
        raise ValueError("values cannot be negative")
    if math.isclose(sum(values), 0):
        raise ValueError("the sum of values must be greater than zero")
    return values


def parse_labels(raw_labels, expected_count):
    if raw_labels is None:
        return [f"competitor_{index}" for index in range(1, expected_count + 1)]

    labels = [
        label.strip()
        for label in raw_labels.split(",")
        if label.strip()
    ]
    if len(labels) != expected_count:
        raise ValueError("label count must equal value count")
    return labels


def concentration_level(hhi):
    if hhi < 1000:
        return "UNCONCENTRATED"
    if hhi <= 1800:
        return "MODERATELY_CONCENTRATED"
    return "HIGHLY_CONCENTRATED"


def main():
    parser = argparse.ArgumentParser(
        description="Calculate a proxy Herfindahl-Hirschman Index"
    )
    parser.add_argument(
        "values",
        help="Comma-separated numeric values or a JSON numeric array",
    )
    parser.add_argument(
        "--labels",
        help="Comma-separated competitor names in the same order as values",
    )
    parser.add_argument(
        "--metric-name",
        default="proxy_metric",
        help="Name of the consistent metric represented by the values",
    )
    args = parser.parse_args()

    try:
        values = parse_values(args.values)
        labels = parse_labels(args.labels, len(values))
        total = sum(values)

        competitors = []
        hhi = 0.0
        for label, value in zip(labels, values):
            share = (value / total) * 100
            hhi += share ** 2
            competitors.append({
                "label": label,
                "value": value,
                "sharePercent": round(share, 4),
            })

        hhi = round(hhi, 2)
        competitors.sort(
            key=lambda competitor: competitor["sharePercent"],
            reverse=True,
        )

        output = {
            "metricName": args.metric_name,
            "isProxyHhi": True,
            "competitorCount": len(values),
            "totalProxyVolume": total,
            "proxyHhi": hhi,
            "hhiScale": {"minimum": 0, "maximum": 10000},
            "concentrationLevel": concentration_level(hhi),
            "classificationFramework": "US_DOJ_FTC_2023",
            "effectiveCompetitorCount": round(10000 / hhi, 2),
            "largestCompetitorSharePercent": competitors[0]["sharePercent"],
            "competitors": competitors,
            "limitations": [
                "Proxy metrics are not verified market shares.",
                "Omitted competitors can materially change the result.",
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False))

    except ValueError as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
