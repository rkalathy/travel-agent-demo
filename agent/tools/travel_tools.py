"""Travel tool functions and their Anthropic tool-use JSON schemas.

Every tool function returns a JSON string (never a Python object), so the
agent loop can drop the return value straight into a tool_result block.
Errors are returned as {"error": "..."} JSON rather than raised, so the
model gets a chance to recover instead of the process crashing.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

WEATHER_CONDITIONS = [
    "Sunny",
    "Partly Cloudy",
    "Cloudy",
    "Light Rain",
    "Rain",
    "Thunderstorms",
    "Clear",
]


def _load_json(filename: str) -> list:
    path = DATA_DIR / filename
    with open(path, "r") as f:
        return json.load(f)


def search_flights(destination: str, max_price_usd: float | None = None) -> str:
    """Search mock flights to a destination, optionally capped by price."""
    try:
        flights = _load_json("flights.json")
        destination_lower = destination.strip().lower()
        results = [f for f in flights if f["to"].lower() == destination_lower]

        if max_price_usd is not None:
            results = [f for f in results if f["price_usd"] <= max_price_usd]

        results.sort(key=lambda f: f["price_usd"])

        if not results:
            return json.dumps(
                {
                    "destination": destination,
                    "count": 0,
                    "flights": [],
                    "note": "No flights matched the given criteria.",
                }
            )

        return json.dumps(
            {"destination": destination, "count": len(results), "flights": results}
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_hotels(
    city: str,
    max_price_per_night_usd: float | None = None,
    min_stars: int | None = None,
) -> str:
    """Search mock hotels in a city, optionally filtered by price and star rating."""
    try:
        hotels = _load_json("hotels.json")
        city_lower = city.strip().lower()
        results = [h for h in hotels if h["city"].lower() == city_lower]

        if max_price_per_night_usd is not None:
            results = [
                h for h in results if h["price_per_night_usd"] <= max_price_per_night_usd
            ]

        if min_stars is not None:
            results = [h for h in results if h["stars"] >= min_stars]

        results.sort(key=lambda h: h["price_per_night_usd"])

        if not results:
            return json.dumps(
                {
                    "city": city,
                    "count": 0,
                    "hotels": [],
                    "note": "No hotels matched the given criteria.",
                }
            )

        return json.dumps({"city": city, "count": len(results), "hotels": results})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_weather(city: str) -> str:
    """Return a deterministic mock 5-day forecast, seeded by city name."""
    try:
        rng = random.Random(city.strip().lower())
        today = datetime.now().date()

        forecast = []
        for day_offset in range(5):
            date = today + timedelta(days=day_offset)
            forecast.append(
                {
                    "date": date.isoformat(),
                    "condition": rng.choice(WEATHER_CONDITIONS),
                    "high_f": rng.randint(60, 95),
                    "low_f": rng.randint(45, 65),
                }
            )

        return json.dumps({"city": city, "forecast": forecast})
    except Exception as e:
        return json.dumps({"error": str(e)})


def save_itinerary(title: str, markdown_content: str) -> str:
    """Write a timestamped markdown itinerary into outputs/ and return the path."""
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "" for c in title
        ).strip()
        safe_title = safe_title.replace(" ", "_").lower() or "itinerary"

        filename = f"{safe_title}_{timestamp}.md"
        path = OUTPUT_DIR / filename
        path.write_text(markdown_content)

        return json.dumps({"path": str(path), "title": title, "saved": True})
    except Exception as e:
        return json.dumps({"error": str(e)})


TOOL_SCHEMAS = [
    {
        "name": "search_flights",
        "description": (
            "Search mock flights to a destination city. Returns flights sorted "
            "cheapest first. Use max_price_usd to cap results by budget."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Destination city, e.g. 'Tokyo'",
                },
                "max_price_usd": {
                    "type": "number",
                    "description": "Optional maximum flight price in USD",
                },
            },
            "required": ["destination"],
        },
    },
    {
        "name": "search_hotels",
        "description": (
            "Search mock hotels in a city. Returns hotels sorted cheapest first. "
            "Use max_price_per_night_usd and/or min_stars to filter."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City to search hotels in, e.g. 'Tokyo'",
                },
                "max_price_per_night_usd": {
                    "type": "number",
                    "description": "Optional maximum nightly price in USD",
                },
                "min_stars": {
                    "type": "integer",
                    "description": "Optional minimum star rating (1-5)",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "get_weather",
        "description": (
            "Get a mock 5-day weather forecast for a city. Deterministic per "
            "city so repeated calls return the same forecast."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City to get the forecast for, e.g. 'Tokyo'",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "save_itinerary",
        "description": (
            "Save the final day-by-day itinerary as a markdown file in outputs/. "
            "Call this exactly once, after flights, hotels, and weather have all "
            "been checked."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short trip title, e.g. 'Tokyo 3-Day Trip'",
                },
                "markdown_content": {
                    "type": "string",
                    "description": "Full itinerary content formatted as markdown",
                },
            },
            "required": ["title", "markdown_content"],
        },
    },
]

TOOL_FUNCTIONS = {
    "search_flights": search_flights,
    "search_hotels": search_hotels,
    "get_weather": get_weather,
    "save_itinerary": save_itinerary,
}
