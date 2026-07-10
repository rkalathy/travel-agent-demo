---
name: create-or-update-travel-data
description: Create or update the mock travel inventory (data/flights.json and data/hotels.json) that Atlas's tools read from. Use whenever the user asks to add a destination, add or update flights/hotels, expand the mock inventory, or says things like "add Rome to the data" — even if they don't say "travel data".
---

# Agent Travel Data

Create or update the mock flight and hotel listings in `data/flights.json`
and `data/hotels.json`. These are the only inventory `search_flights` and
`search_hotels` (in `agent/tools/travel_tools.py`) ever return — there is
no live API behind them, so realism and internal consistency matter more
than accuracy to any real-world source.

## Schema

`data/flights.json` — array of objects:

```json
{
  "id": "FL008",
  "from": "JFK",
  "to": "Rome",
  "airline": "Alitalia",
  "depart": "2026-08-10T19:00:00",
  "arrive": "2026-08-11T09:15:00",
  "stops": 0,
  "price_usd": 540
}
```

`data/hotels.json` — array of objects:

```json
{
  "id": "HT008",
  "city": "Rome",
  "name": "Trastevere Boutique Hotel",
  "area": "Trastevere",
  "stars": 4,
  "price_per_night_usd": 165,
  "highlights": ["Cobblestone streets", "Walk to Vatican", "Rooftop terrace"]
}
```

## Workflow

1. **Read the current data.** Read `data/flights.json` and
   `data/hotels.json` in full before adding or changing anything.

2. **Decide create vs. update.**
   - **Adding a new destination**: create at least 2 flight entries
     (varied airlines/prices/stops) and at least 2 hotel entries (varied
     star tiers and price points) so `search_flights`/`search_hotels`
     have something meaningful to sort and filter.
   - **Updating an existing destination**: edit the matching entries in
     place (e.g. reprice a route, change an airline, add a hotel to a
     city that already has some). Don't duplicate an existing id or
     recreate an entry that's just being tweaked.
   - **Removing stale entries**: delete them outright rather than
     leaving unused listings behind.

3. **Follow these conventions**:
   - IDs continue the existing sequence: `FL0xx` for flights, `HT0xx`
     for hotels, zero-padded to 3 digits, never reused or duplicated.
   - `depart`/`arrive` are ISO 8601 datetimes, arrival roughly a
     realistic flight duration after departure (don't worry about time
     zone math being exact — this is mock data).
   - Prices should sit in a plausible range relative to existing entries
     for similar routes/star tiers, so demo budgets (e.g. "under $1500")
     produce sensible filtered results.
   - `highlights` is 2-4 short phrases, not full sentences.

4. **Validate before finishing.** Run:

   ```bash
   python .claude/skills/create-or-update-travel-data/scripts/validate_travel_data.py \
     data/flights.json data/hotels.json
   ```

   Fix any reported problems (missing fields, duplicate ids, bad id
   prefixes, out-of-range stars, non-positive prices) and re-run until it
   reports `OK`.

5. **Update RUNBOOK.md if the price/count table is now stale.**
   `RUNBOOK.md`'s mock-mode section (§2a) quotes min flight price, min
   hotel price/night, and entry counts per city. If you added, removed,
   or repriced entries for a city already in that table, re-derive the
   numbers from the updated JSON and edit the table — don't leave it
   pointing at superseded prices. Adding a brand-new city doesn't
   require a new row unless mock mode can actually route to it (see
   `agent/agent.py`'s `run_agent_mock` destination matcher).

6. **Report back to the user.** State what changed: how many flights and
   hotels were added, updated, or removed, and for which
   destination(s)/cit(y/ies), plus whether RUNBOOK.md needed updating.
