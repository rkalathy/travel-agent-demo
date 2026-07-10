# Atlas — AI Travel Agent Demo

![CI](https://img.shields.io/badge/build-passing-brightgreen)

A small, readable demo of an agentic tool-use loop built on the
Anthropic Python SDK. Give Atlas a trip request in plain English and it
autonomously searches flights, hotels, and weather, then writes a
day-by-day itinerary to a markdown file.

## How the agent loop works

```
        ┌─────────────────────────────────────────────┐
        │  user: "Plan a 3-day trip to Tokyo under     │
        │         $1500"                               │
        └───────────────────────┬───────────────────────┘
                                 ▼
                    ┌────────────────────────┐
                    │  Claude (system prompt   │
                    │  + tool schemas)          │◄────────────┐
                    └───────────┬──────────────┘              │
                                 ▼                              │
                     stop_reason == "tool_use"?                │
                        │yes               │no                 │
                        ▼                   ▼                  │
          ┌─────────────────────────┐   done — print          │
          │ execute each tool call:  │   summary                │
          │  search_flights          │                          │
          │  search_hotels           │                          │
          │  get_weather              │                          │
          │  save_itinerary            │                          │
          └─────────────┬────────────┘                          │
                          ▼                                      │
              append tool_result blocks,                          │
              call the API again ─────────────────────────────────┘
                (capped at MAX_TURNS = 12)
```

## Project tree

```
travel-agent-demo/
├── main.py                     # CLI entry point
├── CLAUDE.md                   # project instructions for Claude Code
├── RUNBOOK.md                   # manual test checklist
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── .claude/skills/agent-flashcards/   # study-deck skill
├── .claude/skills/agent-travel-data/  # mock inventory skill
├── .claude/skills/agent-docs/         # README/CLAUDE.md upkeep skill
├── agent/
│   ├── agent.py                 # the agent loop (run_agent, run_agent_mock)
│   ├── prompts.py                # Atlas system prompt
│   └── tools/
│       └── travel_tools.py       # tool functions + JSON schemas
├── data/
│   ├── flights.json              # mock flight inventory
│   └── hotels.json               # mock hotel inventory
└── outputs/                      # itineraries + flashcards land here
```

## Quick start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Try it with no API key (mock mode)

Mock mode calls all four tools directly with a scripted planner —
useful for verifying the project works before spending any tokens.

```bash
python main.py --mock "Plan a 3-day trip to Tokyo under $1500"
```

You should see tool calls printed to the console and a new file appear
under `outputs/`. See `RUNBOOK.md` for the full manual test checklist,
including edge cases and how to verify each project skill.

### 3. Run it live

```bash
cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY
export $(cat .env | xargs)

python main.py "Plan a 3-day trip to Tokyo under $1500"
```

## How the agent works

Atlas ("agent/prompts.py") follows a fixed workflow: understand the
request, search flights, search hotels, check the weather, draft a
day-by-day plan, save the itinerary exactly once via `save_itinerary`,
then summarize the trip and total cost. The loop in `agent/agent.py`
keeps calling the API and executing tool calls until Claude stops
asking for tools (or `MAX_TURNS = 12` is hit). Every tool
(`agent/tools/travel_tools.py`) reads from the mock JSON data in
`data/` and returns a JSON string — never invented data.

## Study flashcards

This repo includes a project skill, `agent-flashcards`
(`.claude/skills/agent-flashcards/`), that builds or refreshes a study
deck about the agent's own code — the loop, the tools, the prompt
design. In a Claude Code session in this repo, just say "refresh my
flashcards" (or ask for flashcards/study cards/a quiz) and it will:

1. Read the current `agent/` source
2. Create a new deck, or update an existing one in place (keeping
   still-accurate cards, rewriting stale ones, adding cards for new
   concepts, dropping cards for removed code)
3. Save `outputs/flashcards/cards.json` and render
   `outputs/flashcards/flashcards.html` — a self-contained, printable,
   click-to-reveal flashcard sheet you can open in any browser

## Growing the mock inventory

A second project skill, `agent-travel-data`
(`.claude/skills/agent-travel-data/`), adds or updates entries in
`data/flights.json` and `data/hotels.json` — the only inventory
`search_flights`/`search_hotels` ever return. Ask for something like
"add Rome to the travel data" and it will generate consistent flight
and hotel entries, validate them with
`scripts/validate_travel_data.py`, and report what changed.

## Keeping these docs in sync

A third project skill, `agent-docs` (`.claude/skills/agent-docs/`),
updates this README, `CLAUDE.md`, and `RUNBOOK.md` whenever the code
moves out from under them — a new tool, a new skill, a changed
workflow, a renamed constant, or changed mock data that makes
RUNBOOK.md's example prices/counts stale. Ask for something like
"update the README" or "update the runbook" and it will diff the docs
against the current source and edit all three in place.

## License

Demo project — use it however you like.
