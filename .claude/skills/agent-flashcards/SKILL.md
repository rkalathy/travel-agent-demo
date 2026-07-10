---
name: agent-flashcards
description: Create or update study flashcards for this repo's agent code. Use whenever the user asks for flashcards, study cards, revision material, a quiz, says "refresh/update my flashcards", or after meaningful changes to files under agent/ — even if they don't say the word "flashcard".
---

# Agent Flashcards

Create or refresh a study deck about this repo's agent code: the agent
loop, the system prompt, and the tools. The deck lives at
`outputs/flashcards/cards.json` and is rendered to a self-contained,
printable HTML sheet at `outputs/flashcards/flashcards.html`.

## Workflow

1. **Read the current source.** Read these files in full before writing
   or updating any cards:
   - `agent/agent.py`
   - `agent/prompts.py`
   - `agent/tools/travel_tools.py`

2. **Decide create vs. update.**
   - If `outputs/flashcards/cards.json` does not exist: **create** a new
     deck of 10-15 cards from scratch, covering the agent loop, the
     system prompt's workflow, and the four tools.
   - If it already exists: **update** it in place.
     - Keep cards that are still accurate as-is.
     - Rewrite any card whose answer no longer matches the code (e.g. a
       constant changed, a tool's signature changed, the workflow order
       changed).
     - Add new cards for new concepts (new tools, new workflow steps,
       new architectural decisions).
     - Delete cards about code that no longer exists.

3. **Follow card quality rules.** Read
   `.claude/skills/agent-flashcards/references/writing-good-cards.md`
   before writing or rewriting any card. In particular: one fact per
   card, open questions (not yes/no), answers under 30 words, at least
   two "why" cards, at least one "compare X vs Y" card, never copy
   source sentences verbatim.

4. **Save the deck.** Write the full deck as JSON to
   `outputs/flashcards/cards.json`, matching this shape:

   ```json
   {
     "title": "Atlas Travel Agent — Study Deck",
     "cards": [
       {"q": "...", "a": "...", "hint": "optional"}
     ]
   }
   ```

5. **Render the HTML.** Run:

   ```bash
   python .claude/skills/agent-flashcards/scripts/build_flashcards.py \
     outputs/flashcards/cards.json outputs/flashcards/flashcards.html
   ```

6. **Report back to the user.** State exactly what changed: how many
   cards were kept unchanged, how many were updated, how many were
   added, and how many were removed (all four counts, even if zero).
