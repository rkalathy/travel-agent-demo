---
name: agent-docs
description: Create or update this project's README.md, CLAUDE.md, and RUNBOOK.md so they stay accurate as the code changes. Use whenever the user asks to "update the README", "update CLAUDE.md", "update the runbook", "refresh the docs", "document this change", or after adding/removing a tool, skill, file, or changing the agent workflow, mock data, or test commands.
---

# Agent Docs

Keep `README.md` (user-facing), `CLAUDE.md` (agent-facing project
instructions), and `RUNBOOK.md` (manual test checklist) in sync with
the actual state of the codebase. These three files serve different
readers, so don't merge their content:

- **README.md** — for a human skimming the repo: what Atlas is, the
  agent-loop diagram, the project tree, quick-start commands, how the
  agent works, and one short section per project skill.
- **CLAUDE.md** — for Claude Code working in this repo: run/test
  commands, file-by-file architecture, conventions to follow when
  adding code, gotchas that aren't obvious from reading the source, and
  one short section per project skill describing when to use it.
- **RUNBOOK.md** — for whoever is verifying a change works: step-by-step
  manual test commands, expected output for each, edge cases, and a
  "what to run after each kind of change" table. Every command in it
  should actually work as written — this file gets stale fastest
  because it quotes live data (prices, counts, filenames).

## Workflow

1. **Read the current state before writing anything.**
   - All three existing docs: `README.md`, `CLAUDE.md`, `RUNBOOK.md`.
   - The actual source: `main.py`, `agent/agent.py`, `agent/prompts.py`,
     `agent/tools/travel_tools.py`, `data/flights.json`,
     `data/hotels.json`.
   - The skill directory: `.claude/skills/*/SKILL.md` (read each one's
     frontmatter `description` — that's the trigger phrase to summarize).
   - The project tree (`ls -R` or equivalent) to catch new/removed
     files the docs don't mention yet.

2. **Diff what you found against what the docs claim.** Look
   specifically for:
   - New or removed tools in `travel_tools.py` not reflected in
     CLAUDE.md's architecture section, `TOOL_SCHEMAS`/`TOOL_FUNCTIONS`
     mentions, or RUNBOOK.md's per-tool test steps.
   - New or removed `.claude/skills/*` directories without a matching
     README "## ..." section, CLAUDE.md section, and (if the skill
     produces something testable) RUNBOOK.md section.
   - Changed constants that docs quote literally (`MAX_TURNS`, `MODEL`,
     CLI flags) — grep the source for the current value, don't assume.
   - Changed workflow steps in `agent/prompts.py` that CLAUDE.md's
     one-line workflow summary should mirror.
   - A project tree in README.md that no longer matches `find . -type f`
     (minus `.git`, `__pycache__`, gitignored paths).
   - Data that changed in `data/flights.json`/`data/hotels.json` since
     RUNBOOK.md's price/count table was last written — re-derive it
     from the actual files, don't eyeball it.
   - New/removed edge cases worth a RUNBOOK.md entry (e.g. a new city
     that mock mode's destination matcher doesn't recognize yet).

3. **Edit in place — don't restructure.** Preserve each file's existing
   section order, heading style, and tone. Add a new section only when
   describing something that genuinely has no home yet (e.g. a new
   skill); otherwise update the existing section's text. Keep README
   examples runnable (real commands, real flags), CLAUDE.md gotchas
   specific (name the file/function, not just "be careful"), and every
   RUNBOOK.md command **actually run** before you claim its expected
   output — don't guess at counts, prices, or filenames.

4. **Keep skill sections consistent across all three files.** Every
   skill under `.claude/skills/` should have:
   - One short paragraph/list item in README.md (what it does, the
     phrase that triggers it, e.g. under "## Study flashcards").
   - One short section in CLAUDE.md (when to use it, any script it
     runs, e.g. "## Flashcards").
   - If it changes something the runbook tests (data, tools, prompts),
     a matching update in RUNBOOK.md — either a new section or a row in
     its "what to run after each kind of change" table.
   If you add a new skill's docs to one file, add its counterparts to
   the other two in the same pass.

5. **Report back.** State exactly what changed in each file — new
   sections added, sections rewritten, stale facts corrected (old value
   -> new value), including any RUNBOOK.md numbers you re-verified. If
   nothing was actually stale, say so instead of editing for the sake
   of editing.
