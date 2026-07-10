# Runbook: Testing Atlas

There's no automated test suite (`pytest`, etc.) in this project — it's
a demo. This runbook is the manual checklist for verifying the agent,
its tools, and its three project skills actually work before you trust
a change. Run top to bottom after any non-trivial edit; skip to the
relevant section after a small one.

Run everything from the project root (`travel-agent-demo/`).

## 0. Setup

```bash
pip install -r requirements.txt
```

No API key is needed for sections 1–4 below. Section 5 (live mode)
needs `ANTHROPIC_API_KEY`.

## 1. Static check: does everything compile?

```bash
python -m py_compile main.py agent/*.py agent/tools/*.py \
  .claude/skills/agent-flashcards/scripts/build_flashcards.py \
  .claude/skills/agent-travel-data/scripts/validate_travel_data.py
```

Expect: no output, exit code 0. Any `SyntaxError`/`IndentationError`
here means don't bother running the rest.

## 2. Mock mode: the core smoke test

Mock mode exercises all four tools (`search_flights`, `search_hotels`,
`get_weather`, `save_itinerary`) and the full save-to-`outputs/` path
with **no API key and no `anthropic` import**. This is the fastest way
to catch a broken tool or a broken save path.

### 2a. Happy path, one per supported city

```bash
python main.py --mock "Plan a 3-day trip to Tokyo under \$1500"
python main.py --mock "Plan a 3-day trip to Paris under \$2000"
python main.py --mock "Plan a 3-day trip to London under \$2000"
```

For each, check the console output shows, in order:
1. `calling search_flights(...)` followed by `found N flight(s)` with
   `N >= 1`
2. `calling search_hotels(...)` followed by `found N hotel(s)` with
   `N >= 1`
3. `calling get_weather(...)` followed by `forecast: 5 day(s)`
4. `calling save_itinerary(...)` followed by `Itinerary saved to
   .../outputs/<slug>_<timestamp>.md`
5. A final `Estimated total cost is $N` line

Then open the saved file under `outputs/` and confirm it has a `#
<City> 3-Day Trip` heading, a `## Flight` section, a `## Hotel`
section, a `## Day-by-Day Plan` with exactly 3 `### Day N` entries, and
`## Estimated Total Cost`.

Known-good reference (current mock data, current prices):

| City   | min flight | flight count | min hotel/night | hotel count |
|--------|-----------:|-------------:|-----------------:|-------------:|
| Tokyo  | $430       | 4            | $60              | 4            |
| Paris  | $560       | 2            | $75              | 2            |
| London | $640       | 1            | $195             | 1            |

If a run reports different counts/prices than this table for
*unchanged* data, something broke in `search_flights`/`search_hotels`
filtering — investigate before assuming the data changed.

### 2b. Edge case: budget below every flight price

```bash
python main.py --mock "Plan a trip to Tokyo under \$10"
```

Expect `found 0 flight(s)`, but the run should still complete: hotels
and weather are still found, `save_itinerary` still runs, and the
saved file's `## Flight` section is simply omitted (no crash, no
`None` printed). Total cost should equal `hotel_price_per_night * 3`
only (no flight added). This is a real quirk worth knowing: the
summary line still says "for flight + 3 nights" even when there's no
flight in the total — that's a cosmetic label issue, not a bug in the
cost math. Don't "fix" the math; if you touch the label, keep the cost
calculation identical.

### 2c. Edge case: unrecognized destination

```bash
python main.py --mock "Plan a trip to Rome under \$1500"
```

`run_agent_mock` only pattern-matches `tokyo`/`paris`/`london` in the
request text — anything else silently **falls back to Tokyo**. This is
expected today, not a crash to chase. If you've just added a new city
via the `agent-travel-data` skill and want mock mode to route to it,
you'd need to extend the `for city in (...)` tuple in
`run_agent_mock` (`agent/agent.py`) — that's a real code change, not a
test.

### 2d. Edge case: no dollar amount in the request

```bash
python main.py --mock "Plan a relaxing trip to Paris"
```

Expect it to fall back to the default `max_price = 700` and still
complete normally (check `search_flights(..., max_price_usd=700)` in
the printed tool call).

## 3. `agent-travel-data` skill: inventory validity

Anytime `data/flights.json` or `data/hotels.json` changes — by hand or
via the skill — validate them:

```bash
python .claude/skills/agent-travel-data/scripts/validate_travel_data.py \
  data/flights.json data/hotels.json
```

Expect: `OK: 2 file(s), <N> entries, no problems found`.

To confirm the validator actually catches problems (not just a
no-op), run it against a deliberately broken copy at least once after
touching the validator itself:

```bash
python3 -c "
import json
flights = json.load(open('data/flights.json'))
broken = flights + [{**flights[0], 'id': flights[0]['id'], 'price_usd': -5}]
json.dump(broken, open('/tmp/broken_flights.json', 'w'))
"
python .claude/skills/agent-travel-data/scripts/validate_travel_data.py /tmp/broken_flights.json
```

Expect: `FAILED: N problem(s) found`, listing the duplicate id and the
non-positive `price_usd`, and a non-zero exit code (`echo $?`).

After validating, re-run section 2's mock commands for any
newly-added or changed city to confirm `search_flights`/`search_hotels`
actually surface the new entries.

## 4. `agent-flashcards` skill: deck build

If `outputs/flashcards/cards.json` changed (by hand or via the skill):

```bash
python .claude/skills/agent-flashcards/scripts/build_flashcards.py \
  outputs/flashcards/cards.json outputs/flashcards/flashcards.html
```

Expect: `Wrote <N> cards to outputs/flashcards/flashcards.html`, where
`<N>` matches the number of entries in `cards.json`.

Then check `outputs/flashcards/flashcards.html`:
- starts with `<!doctype html>`
- contains one `<div class="card">` (or equivalent) per entry in
  `cards.json` — count should match
- open it in a browser: cards should render click-to-reveal, no raw
  `<`/`>`/`"` characters leaking through unescaped (paste a card
  question containing `<script>` into a scratch copy of `cards.json`
  and rebuild if you want to re-verify escaping after touching the
  render script)

## 5. Live mode (uses real API tokens)

Only needed when touching `run_agent`, `ATLAS_SYSTEM_PROMPT`, or
`TOOL_SCHEMAS` — mock mode can't catch prompt/schema regressions since
it bypasses the model entirely.

```bash
cp .env.example .env   # then edit in your ANTHROPIC_API_KEY
export $(cat .env | xargs)
python main.py "Plan a 3-day trip to Tokyo under \$1500"
```

Check:
- Console shows `-> calling <tool>(...)` lines for all four tools, in
  a sensible order (flights/hotels/weather before save)
- `save_itinerary` is called exactly once (per the system prompt's
  rule) — if you see it called twice, the prompt or workflow logic
  regressed
- The loop terminates on its own (`stop_reason != "tool_use"`) well
  before `MAX_TURNS = 12`; hitting the cap and printing `[Atlas
  stopped after reaching MAX_TURNS=12]` means something is stuck
  re-requesting tools

## 6. `agent-docs` skill: docs stay honest

This one has no script — it's Claude editing `README.md`/`CLAUDE.md`
directly. "Testing" it means checking the *result*, not running a
command:

- Every entry under `.claude/skills/` has one section in `README.md`
  and one in `CLAUDE.md`
- `CLAUDE.md`'s quoted constants (`MAX_TURNS`, `MODEL`) match the
  actual values in `agent/agent.py`
- The `README.md` project tree matches `find . -type f` (minus `.git`,
  `.venv`, `__pycache__`, gitignored paths)

## Quick reference: what to run after each kind of change

| You changed...                          | Run |
|------------------------------------------|-----|
| Any `.py` file                            | §1 (compile), then §2 (mock) |
| `agent/tools/travel_tools.py`             | §1, §2 (all cities + edge cases) |
| `data/flights.json` / `data/hotels.json`  | §3 (validate), then §2 |
| `agent/prompts.py` or `TOOL_SCHEMAS`      | §1, §2, and §5 (live — mock can't catch this) |
| `outputs/flashcards/cards.json`           | §4 |
| `README.md` / `CLAUDE.md`                 | §6 |
| Anything under `.claude/skills/`          | Re-run the section for that skill above |
