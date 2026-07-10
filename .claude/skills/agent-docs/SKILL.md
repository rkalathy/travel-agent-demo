---
name: agent-docs
description: Create or update this project's README.md and CLAUDE.md so they stay accurate as the code changes. Use whenever the user asks to "update the README", "update CLAUDE.md", "refresh the docs", "document this change", or after adding/removing a tool, skill, file, or changing the agent workflow.
---

# Agent Docs

Keep `README.md` (user-facing) and `CLAUDE.md` (agent-facing project
instructions) in sync with the actual state of the codebase. These two
files serve different readers, so don't merge their content:

- **README.md** — for a human skimming the repo: what Atlas is, the
  agent-loop diagram, the project tree, quick-start commands, how the
  agent works, and one short section per project skill.
- **CLAUDE.md** — for Claude Code working in this repo: run/test
  commands, file-by-file architecture, conventions to follow when
  adding code, gotchas that aren't obvious from reading the source, and
  one short section per project skill describing when to use it.

## Workflow

1. **Read the current state before writing anything.**
   - Both existing docs: `README.md`, `CLAUDE.md`.
   - The actual source: `main.py`, `agent/agent.py`, `agent/prompts.py`,
     `agent/tools/travel_tools.py`.
   - The skill directory: `.claude/skills/*/SKILL.md` (read each one's
     frontmatter `description` — that's the trigger phrase to summarize).
   - The project tree (`ls -R` or equivalent) to catch new/removed
     files the docs don't mention yet.

2. **Diff what you found against what the docs claim.** Look
   specifically for:
   - New or removed tools in `travel_tools.py` not reflected in
     CLAUDE.md's architecture section or `TOOL_SCHEMAS`/`TOOL_FUNCTIONS`
     mentions.
   - New or removed `.claude/skills/*` directories without a matching
     README "## ..." section and CLAUDE.md section.
   - Changed constants that docs quote literally (`MAX_TURNS`, `MODEL`,
     CLI flags) — grep the source for the current value, don't assume.
   - Changed workflow steps in `agent/prompts.py` that CLAUDE.md's
     one-line workflow summary should mirror.
   - A project tree in README.md that no longer matches `find . -type f`
     (minus `.git`, `__pycache__`, gitignored paths).

3. **Edit in place — don't restructure.** Preserve each file's existing
   section order, heading style, and tone. Add a new section only when
   describing something that genuinely has no home yet (e.g. a new
   skill); otherwise update the existing section's text. Keep README
   examples runnable (real commands, real flags) and CLAUDE.md gotchas
   specific (name the file/function, not just "be careful").

4. **Keep skill sections consistent across both files.** Every skill
   under `.claude/skills/` should have:
   - One short paragraph/list item in README.md (what it does, the
     phrase that triggers it, e.g. under "## Study flashcards").
   - One short section in CLAUDE.md (when to use it, any script it
     runs, e.g. "## Flashcards").
   If you add a new skill's docs to one file, add its counterpart to
   the other in the same pass.

5. **Report back.** State exactly what changed in each file — new
   sections added, sections rewritten, stale facts corrected (old value
   -> new value). If nothing was actually stale, say so instead of
   editing for the sake of editing.
