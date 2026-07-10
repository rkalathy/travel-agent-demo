#!/usr/bin/env python3
"""Validate the mock travel inventory files (data/flights.json, data/hotels.json).

Usage:
    python validate_travel_data.py data/flights.json data/hotels.json

Exits non-zero and prints every problem found if any file is invalid.
"""

import json
import sys

FLIGHT_REQUIRED_FIELDS = {
    "id": str,
    "from": str,
    "to": str,
    "airline": str,
    "depart": str,
    "arrive": str,
    "stops": int,
    "price_usd": (int, float),
}

HOTEL_REQUIRED_FIELDS = {
    "id": str,
    "city": str,
    "name": str,
    "area": str,
    "stars": int,
    "price_per_night_usd": (int, float),
    "highlights": list,
}


def _schema_for(path: str):
    if "flight" in path.lower():
        return "FL", FLIGHT_REQUIRED_FIELDS
    if "hotel" in path.lower():
        return "HT", HOTEL_REQUIRED_FIELDS
    raise ValueError(f"Can't infer schema for {path}: filename must contain 'flight' or 'hotel'")


def validate_file(path: str) -> list:
    errors = []
    prefix, schema = _schema_for(path)

    try:
        with open(path, "r") as f:
            entries = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return [f"{path}: could not read/parse JSON: {e}"]

    if not isinstance(entries, list):
        return [f"{path}: top level must be a JSON array"]

    seen_ids = set()
    for i, entry in enumerate(entries):
        label = f"{path}[{i}] (id={entry.get('id', '?')})"

        if not isinstance(entry, dict):
            errors.append(f"{label}: entry is not an object")
            continue

        for field, expected_type in schema.items():
            if field not in entry:
                errors.append(f"{label}: missing required field '{field}'")
                continue
            if not isinstance(entry[field], expected_type):
                errors.append(
                    f"{label}: field '{field}' should be {expected_type}, "
                    f"got {type(entry[field]).__name__}"
                )

        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            if not entry_id.startswith(prefix):
                errors.append(f"{label}: id should start with '{prefix}'")
            if entry_id in seen_ids:
                errors.append(f"{label}: duplicate id '{entry_id}'")
            seen_ids.add(entry_id)

        if "price_usd" in entry and isinstance(entry["price_usd"], (int, float)):
            if entry["price_usd"] <= 0:
                errors.append(f"{label}: price_usd must be positive")

        if "price_per_night_usd" in entry and isinstance(
            entry["price_per_night_usd"], (int, float)
        ):
            if entry["price_per_night_usd"] <= 0:
                errors.append(f"{label}: price_per_night_usd must be positive")

        if "stars" in entry and isinstance(entry["stars"], int):
            if not 1 <= entry["stars"] <= 5:
                errors.append(f"{label}: stars must be between 1 and 5")

        if "stops" in entry and isinstance(entry["stops"], int):
            if entry["stops"] < 0:
                errors.append(f"{label}: stops must be >= 0")

    return errors


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: validate_travel_data.py <file.json> [<file.json> ...]", file=sys.stderr)
        sys.exit(1)

    all_errors = []
    total_entries = 0
    for path in sys.argv[1:]:
        errors = validate_file(path)
        if not errors:
            with open(path) as f:
                total_entries += len(json.load(f))
        all_errors.extend(errors)

    if all_errors:
        print(f"FAILED: {len(all_errors)} problem(s) found\n")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    print(f"OK: {len(sys.argv) - 1} file(s), {total_entries} entries, no problems found")


if __name__ == "__main__":
    main()
