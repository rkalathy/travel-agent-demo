#!/usr/bin/env python3
"""CLI entry point for Atlas, the AI travel agent.

Usage:
    python main.py --mock "Plan a 3-day trip to Tokyo under $1500"
    python main.py "Plan a 3-day trip to Tokyo under $1500"
"""

import argparse
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Atlas: an AI travel agent demo")
    parser.add_argument("request", help="Trip request, e.g. 'Plan a 3-day trip to Tokyo under $1500'")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run without the Anthropic API using a scripted planner (no API key needed)",
    )
    args = parser.parse_args()

    if args.mock:
        from agent.agent import run_agent_mock

        run_agent_mock(args.request)
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY is not set.\n"
            "  - Copy .env.example to .env and add your key, then `export "
            "$(cat .env | xargs)` (or use a tool like python-dotenv), or\n"
            "  - Try the project first without an API key: "
            "python main.py --mock \"your request\"",
            file=sys.stderr,
        )
        sys.exit(1)

    from agent.agent import run_agent

    run_agent(args.request)


if __name__ == "__main__":
    main()
