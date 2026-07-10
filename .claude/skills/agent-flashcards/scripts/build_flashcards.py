#!/usr/bin/env python3
"""Render a flashcards JSON deck into a self-contained, printable HTML sheet.

Usage:
    python build_flashcards.py <input.json> <output.html>

Input JSON shape:
    {"title": "...", "cards": [{"q": "...", "a": "...", "hint": "..."?}, ...]}
"""

import html
import json
import sys


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #f5f5f7;
    --card-bg: #ffffff;
    --card-border: #ddd;
    --text: #1a1a1a;
    --muted: #666;
    --accent: #4f46e5;
    --answer-bg: #eef2ff;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #16161a;
      --card-bg: #212127;
      --card-border: #34343c;
      --text: #f0f0f2;
      --muted: #a0a0ab;
      --accent: #8583f0;
      --answer-bg: #2a2a45;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 2rem 1.5rem 4rem;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
  header {{
    max-width: 1100px;
    margin: 0 auto 1.5rem;
  }}
  h1 {{
    font-size: 1.6rem;
    margin: 0 0 0.25rem;
  }}
  .meta {{
    color: var(--muted);
    font-size: 0.9rem;
  }}
  .grid {{
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    cursor: pointer;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: box-shadow 0.15s ease;
  }}
  .card:hover {{
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  }}
  .card .num {{
    font-size: 0.75rem;
    color: var(--accent);
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
  }}
  .card .q {{
    font-size: 1rem;
    line-height: 1.4;
  }}
  .card .hint {{
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.5rem;
    font-style: italic;
  }}
  .card .a {{
    display: none;
    margin-top: 0.7rem;
    padding-top: 0.7rem;
    border-top: 1px dashed var(--card-border);
    background: var(--answer-bg);
    border-radius: 6px;
    padding: 0.6rem 0.6rem;
    font-size: 0.95rem;
    line-height: 1.4;
  }}
  .card.revealed .a {{
    display: block;
  }}
  .card .toggle-label {{
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.5rem;
  }}
  @media print {{
    body {{ background: white; color: black; padding: 0.5rem; }}
    .card {{
      break-inside: avoid;
      box-shadow: none;
      border: 1px solid #ccc;
    }}
    .card .a {{ display: block !important; }}
    .card .toggle-label {{ display: none; }}
  }}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <div class="meta">{count} cards &middot; click a card to reveal its answer &middot; use your browser's print dialog for a printable sheet</div>
</header>
<div class="grid">
{cards_html}
</div>
<script>
  document.querySelectorAll('.card').forEach(function (card) {{
    card.addEventListener('click', function () {{
      card.classList.toggle('revealed');
    }});
  }});
</script>
</body>
</html>
"""

CARD_TEMPLATE = """  <div class="card">
    <div>
      <div class="num">Card {index}</div>
      <div class="q">{question}</div>
      {hint_html}
    </div>
    <div>
      <div class="a">{answer}</div>
      <div class="toggle-label">click to reveal / hide</div>
    </div>
  </div>"""


def build_html(deck: dict) -> str:
    title = html.escape(deck.get("title", "Flashcards"))
    cards = deck.get("cards", [])

    cards_html_parts = []
    for i, card in enumerate(cards, start=1):
        question = html.escape(card["q"])
        answer = html.escape(card["a"])
        hint = card.get("hint")
        hint_html = f'<div class="hint">Hint: {html.escape(hint)}</div>' if hint else ""
        cards_html_parts.append(
            CARD_TEMPLATE.format(
                index=i, question=question, answer=answer, hint_html=hint_html
            )
        )

    return PAGE_TEMPLATE.format(
        title=title,
        count=len(cards),
        cards_html="\n".join(cards_html_parts),
    )


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: build_flashcards.py <input.json> <output.html>", file=sys.stderr)
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, "r") as f:
        deck = json.load(f)

    output = build_html(deck)

    with open(output_path, "w") as f:
        f.write(output)

    print(f"Wrote {len(deck.get('cards', []))} cards to {output_path}")


if __name__ == "__main__":
    main()
