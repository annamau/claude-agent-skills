#!/usr/bin/env python3
"""Gate edits to test files, and hard-deny edits to the held-out suite.

PreToolUse hook for Edit/Write/NotebookEdit. Two rules:

1. `tests/holdout/**` is never editable by the agent, in any phase. It is the
   only oracle the agent cannot tune to, which is what makes it evidence.
2. Ordinary test files are editable only when the session has declared a
   test-authoring phase. Otherwise the edit is denied with instructions.

Rule 2 is the countermeasure with the best measured effect in the literature:
penalising test modification during implementation cut hacked solutions from
28.57% to 0.56% while *raising* legitimate solve rate. The base rate motivating
it: agent commits modify test files ~23% of the time versus ~13% for humans.

The phase is a file, not a model belief, so it survives compaction:

    .claude/ship-phase        containing `red` (writing tests) or `green`

Fails OPEN on unparseable input.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HOLDOUT = re.compile(r"(^|/)tests?/holdout/")

TEST_PATH = re.compile(
    r"(^|/)(tests?|spec|__tests__|e2e)/|"
    r"(^|/)test_[^/]*\.(py|rb)$|"
    r"[^/]*_test\.(py|go|ts|js|rb|rs)$|"
    r"[^/]*\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$|"
    r"(^|/)conftest\.py$"
)

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def phase(cwd: str) -> str:
    """Read the declared phase. Absent file means implementation ('green')."""
    override = os.environ.get("SHIP_PHASE")
    if override:
        return override.strip().lower()
    try:
        return (Path(cwd) / ".claude" / "ship-phase").read_text().strip().lower()
    except Exception:
        return "green"


def deny(reason: str) -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # fail open

    if payload.get("tool_name") not in EDIT_TOOLS:
        return 0

    raw = payload.get("tool_input", {}).get("file_path", "")
    if not raw:
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    try:
        rel = str(Path(raw).resolve().relative_to(Path(cwd).resolve()))
    except Exception:
        rel = str(raw)
    probe = rel.replace(os.sep, "/")

    if HOLDOUT.search(probe):
        return deny(
            "The held-out suite is not editable. It exists precisely because "
            "the agent cannot see or tune it — that is what makes a pass there "
            "evidence rather than a restatement of what you already wrote. "
            "If a held-out test is genuinely wrong, say so and let a human "
            "decide; do not edit it."
        )

    if not TEST_PATH.search(probe):
        return 0

    if phase(cwd) in ("red", "test", "tests"):
        return 0

    return deny(
        f"Editing `{probe}` is blocked during implementation.\n\n"
        "Changing a test to match the code you just wrote turns the test from "
        "evidence into an echo. If the test is genuinely wrong, or you are "
        "deliberately writing tests now, declare it:\n\n"
        "    echo red > .claude/ship-phase\n\n"
        "Then write the test, watch it FAIL, and set the file back to `green` "
        "before implementing. A test never observed failing proves nothing."
    )


if __name__ == "__main__":
    sys.exit(main())
