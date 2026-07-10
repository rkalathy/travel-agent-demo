# CLAUDE.md

## What this is

Atlas is a demo AI travel agent built on the Anthropic Python SDK. It
shows an agentic tool-use loop: given a plain-English trip request,
Claude autonomously calls flight/hotel/weather tools and a save tool
until it has produced and saved a day-by-day itinerary.

## Run / test commands

```bash
pip install -r requirements.txt

# No API key needed — scripted planner exercises all four tools:
python main.py --mock "Plan a 3-day trip to Tokyo under $1500"

# Live run (needs ANTHROPIC_API_KEY, e.g. via .env + your own loader):
python main.py "Plan a 3-day trip to Tokyo under $1500"

# Sanity-check every file compiles:
python -m py_compile main.py agent/*.py agent/tools/*.py
```

## Architecture, file by file

- `main.py` — CLI entry point. Parses `--mock` and the request string.
  Routes to `run_agent_mock` (no API key, no `anthropic` import) or
  `run_agent` (live). Exits with a helpful message if
  `ANTHROPIC_API_KEY` is missing and `--mock` wasn't passed.
- `agent/prompts.py` — `ATLAS_SYSTEM_PROMPT`, Atlas's persona and its
  numbered workflow (understand -> flights -> hotels -> weather ->
  day-by-day plan -> save_itinerary once -> summary).
- `agent/agent.py` — the agent loop.
  - `run_agent(user_request)`: sends system prompt + `TOOL_SCHEMAS` +
    messages to `claude-sonnet-4-6`. While `stop_reason == "tool_use"`,
    executes each `tool_use` block via `TOOL_FUNCTIONS`, appends
    `tool_result` blocks, and calls the API again. Capped at
    `MAX_TURNS = 12`. Prints each tool call as it happens.
  - `run_agent_mock(user_request)`: scripted planner that calls all
    four tools directly (no API, no `anthropic` import) so the project
    is testable before spending tokens.
- `agent/tools/travel_tools.py` — the four tools, each a plain function
  returning a **JSON string**:
  - `search_flights(destination, max_price_usd=None)`
  - `search_hotels(city, max_price_per_night_usd=None, min_stars=None)`
  - `get_weather(city)` — mock 5-day forecast, seeded by city name so
    it's deterministic across runs
  - `save_itinerary(title, markdown_content)` — writes a timestamped
    `.md` file to `outputs/` and returns its path
  - Also exports `TOOL_SCHEMAS` (Anthropic tool-use JSON schemas) and
    `TOOL_FUNCTIONS` (name -> function registry).
- `data/flights.json`, `data/hotels.json` — mock inventory the tools
  read from.
- `outputs/` — where itineraries land (gitignored) and where the
  `agent-flashcards` skill writes its study deck.
- `.claude/skills/agent-flashcards/` — a project skill that generates
  or refreshes a flashcard deck about this codebase (see below).

## Conventions

- Every tool function returns a JSON **string** (`json.dumps(...)`),
  never a Python object or a raised exception.
- Adding a new tool requires three things, in `agent/tools/travel_tools.py`:
  1. the function itself (JSON-string return, errors caught and
     returned as `{"error": ...}`)
  2. a schema entry appended to `TOOL_SCHEMAS`
  3. a registry entry added to `TOOL_FUNCTIONS`
- Tool errors are returned as JSON, never raised — the model should get
  a chance to react to a failed search rather than crash the process.

## Gotchas

- `MAX_TURNS = 12` in `agent/agent.py` bounds the tool-use loop. If you
  change agent behavior and it starts looping without saving, this is
  the safety valve — raise it only if you have a good reason.
- `run_agent_mock` and everything reachable from `main.py --mock` must
  keep working **without the `anthropic` package installed or
  importable**. The `import anthropic` in `agent/agent.py` is inside
  `run_agent`, not at module scope, specifically so mock mode has no
  hard dependency on it. Keep it that way.
- `get_weather` seeds `random.Random(city)` — don't swap in unseeded
  `random` calls or the mock/live demos stop being repeatable.

## Flashcards

Use the `agent-flashcards` skill (`.claude/skills/agent-flashcards/`) to
refresh `outputs/flashcards/` whenever files under `agent/` change
meaningfully (new tools, changed workflow, prompt rewrites, etc.). It
creates the deck if none exists yet, or updates it in place otherwise.
