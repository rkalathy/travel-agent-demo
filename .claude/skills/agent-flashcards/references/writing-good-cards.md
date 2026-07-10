# Writing good flashcards

Rules to follow when creating or updating cards for this deck:

1. **Atomic, one fact per card.** If a card tests two facts, split it
   into two cards. A learner should be able to fail one without the
   other being affected.
2. **Open questions, not yes/no.** Ask "What does X do?" or "Why does X
   happen?" instead of "Does X do Y?". Yes/no questions are guessable
   and don't test recall.
3. **Answers under 30 words.** If the true answer needs more, the
   question is probably testing too much at once — narrow it.
4. **At least two "why" cards.** Include cards that test the reasoning
   behind a design choice (e.g. "Why is `import anthropic` inside
   `run_agent` instead of at module scope?"), not just what the code
   does.
5. **At least one "compare X vs Y" card.** Test a distinction directly
   (e.g. "Compare `run_agent` and `run_agent_mock` — what's the same,
   what differs?").
6. **Never copy source sentences verbatim.** Paraphrase. A card that
   quotes a docstring or comment word-for-word teaches recognition, not
   understanding.
7. **Prefer "why" and "how" over "what."** Cards like "What is the name
   of the model constant?" test trivia. Cards like "Why does
   `save_itinerary` get called exactly once?" test understanding.
8. **Keep hints optional and short.** A hint (if present) should nudge,
   not answer — a phrase or a pointer to a concept, not a paraphrase of
   the answer.

## Card JSON shape

```json
{
  "title": "Atlas Travel Agent — Study Deck",
  "cards": [
    {
      "q": "Why is the anthropic import inside run_agent rather than at the top of agent.py?",
      "a": "So mock mode (run_agent_mock) works without the anthropic package installed.",
      "hint": "Think about what --mock needs to avoid depending on"
    }
  ]
}
```

`hint` is optional; omit it if the question doesn't need one.
