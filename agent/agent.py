"""The Atlas agent loop.

`run_agent` drives the real Claude tool-use loop and requires the
`anthropic` package plus ANTHROPIC_API_KEY. `run_agent_mock` exercises the
same four tools with a scripted planner and needs neither, so the project
can be smoke-tested without spending API tokens.
"""

import json

from agent.prompts import ATLAS_SYSTEM_PROMPT
from agent.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

MODEL = "claude-sonnet-4-6"
MAX_TURNS = 12


def _execute_tool(name: str, tool_input: dict) -> str:
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        return fn(**tool_input)
    except Exception as e:
        return json.dumps({"error": str(e)})


def run_agent(user_request: str) -> None:
    """Run the live agent loop against the Anthropic API."""
    import anthropic

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_request}]

    for turn in range(1, MAX_TURNS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=ATLAS_SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\nAtlas: {block.text.strip()}")

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"  -> calling {block.name}({json.dumps(block.input)})")
            result = _execute_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            )

        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"\n[Atlas stopped after reaching MAX_TURNS={MAX_TURNS}]")


def run_agent_mock(user_request: str) -> None:
    """Scripted planner that exercises all four tools without calling the API."""
    print(f"Atlas (mock mode): planning for -> {user_request!r}\n")

    destination = "Tokyo"
    lowered = user_request.lower()
    for city in ("tokyo", "paris", "london"):
        if city in lowered:
            destination = city.capitalize()
            break

    max_price = 700
    for token in user_request.replace("$", " ").split():
        if token.isdigit():
            max_price = int(token)
            break

    print(f"  -> calling search_flights(destination='{destination}', max_price_usd={max_price})")
    flights_json = TOOL_FUNCTIONS["search_flights"](destination, max_price_usd=max_price)
    flights = json.loads(flights_json)
    print(f"     found {flights['count']} flight(s)")

    print(f"  -> calling search_hotels(city='{destination}')")
    hotels_json = TOOL_FUNCTIONS["search_hotels"](destination)
    hotels = json.loads(hotels_json)
    print(f"     found {hotels['count']} hotel(s)")

    print(f"  -> calling get_weather(city='{destination}')")
    weather_json = TOOL_FUNCTIONS["get_weather"](destination)
    weather = json.loads(weather_json)
    print(f"     forecast: {len(weather['forecast'])} day(s)")

    best_flight = flights["flights"][0] if flights["flights"] else None
    best_hotel = hotels["hotels"][0] if hotels["hotels"] else None

    lines = [f"# {destination} 3-Day Trip", ""]

    if best_flight:
        lines += [
            "## Flight",
            f"- {best_flight['airline']} ({best_flight['from']} -> {best_flight['to']}), "
            f"${best_flight['price_usd']}, {best_flight['stops']} stop(s)",
            "",
        ]

    if best_hotel:
        lines += [
            "## Hotel",
            f"- {best_hotel['name']} ({best_hotel['area']}), {best_hotel['stars']} stars, "
            f"${best_hotel['price_per_night_usd']}/night",
            "",
        ]

    lines.append("## Day-by-Day Plan")
    for i, day in enumerate(weather["forecast"][:3], start=1):
        lines.append(
            f"### Day {i} ({day['date']}, {day['condition']}, "
            f"{day['low_f']}-{day['high_f']}F)"
        )
        lines.append(f"- Morning: Explore a local neighborhood near the hotel")
        lines.append(f"- Afternoon: Sightseeing suited to {day['condition'].lower()} weather")
        lines.append(f"- Evening: Dinner near {best_hotel['area'] if best_hotel else destination}")
        lines.append("")

    total_cost = 0
    if best_flight:
        total_cost += best_flight["price_usd"]
    if best_hotel:
        total_cost += best_hotel["price_per_night_usd"] * 3
    lines.append(f"## Estimated Total Cost: ${total_cost}")

    markdown_content = "\n".join(lines)
    title = f"{destination} 3-Day Trip"

    print(f"  -> calling save_itinerary(title='{title}', ...)")
    save_result_json = TOOL_FUNCTIONS["save_itinerary"](title, markdown_content)
    save_result = json.loads(save_result_json)

    print(f"\nAtlas: Itinerary saved to {save_result['path']}")
    print(f"Atlas: Estimated total cost is ${total_cost} for flight + 3 nights.")
