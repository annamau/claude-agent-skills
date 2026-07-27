#!/usr/bin/env python3
"""Assert every skill survives compaction and fits its frontmatter budget.

Both failures found in the 2026-07-27 audit are caught here: a SKILL.md whose
back 66% is silently dropped after auto-compaction, and a description 35 chars
from silent truncation.

Limits come from the Claude Code docs:
  - After auto-compaction, only the first 5,000 tokens of a skill are
    re-attached. Content past that is dropped without warning.
  - description + when_to_use are truncated at 1,536 chars in the listing.

Run: python3 scripts/check_skills.py [--verbose]
Exit 0 if every skill passes, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TOKEN_LIMIT = 5000
FRONTMATTER_LIMIT = 1536
WARN_AT = 0.85

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


def count_tokens(text: str) -> tuple[int, str]:
    """Token count, exact if tiktoken is available and estimated otherwise."""
    try:
        import tiktoken
        return len(tiktoken.get_encoding("o200k_base").encode(text)), "exact"
    except Exception:
        # ~3.6 chars/token for English prose with markdown punctuation. Only a
        # fallback: CI installs tiktoken so the gate is measured, not guessed.
        return int(len(text) / 3.6), "estimated"


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fields, key, buf = {}, None, []
    for line in m.group(1).split("\n"):
        km = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if km:
            if key:
                fields[key] = "\n".join(buf).strip()
            key, rest = km.group(1), km.group(2).strip()
            buf = []
            if rest and rest not in (">-", ">", "|", "|-"):
                fields[key] = rest.strip("'\"")
                key = None
        elif key:
            buf.append(line.strip())
    if key:
        fields[key] = "\n".join(buf).strip()
    return fields


def cut_line(text: str, limit: int) -> int | None:
    """First line number past the token limit, or None if it fits."""
    lines = text.split("\n")
    total, _ = count_tokens(text)
    if total <= limit:
        return None
    running = ""
    for i, line in enumerate(lines, 1):
        running += line + "\n"
        n, _ = count_tokens(running)
        if n > limit:
            return i
    return None


def main() -> int:
    verbose = "--verbose" in sys.argv
    skills = sorted(p for p in SKILLS.glob("*/SKILL.md"))
    if not skills:
        print("no skills found", file=sys.stderr)
        return 1

    failures, warnings, mode = [], [], "exact"
    rows = []

    for path in skills:
        name = path.parent.name
        text = path.read_text()
        tokens, mode = count_tokens(text)
        fm = parse_frontmatter(text)
        fchars = len(fm.get("description", "")) + len(fm.get("when_to_use", ""))
        lines = text.count("\n") + 1

        status = "ok"
        if tokens > TOKEN_LIMIT:
            cut = cut_line(text, TOKEN_LIMIT)
            pct = round(100 * (1 - TOKEN_LIMIT / tokens))
            failures.append(
                f"{name}: {tokens} tokens exceeds {TOKEN_LIMIT}. "
                f"Content past line {cut} of {lines} (~{pct}% of the skill) is "
                f"dropped after auto-compaction."
            )
            status = "FAIL"
        elif tokens > TOKEN_LIMIT * WARN_AT:
            warnings.append(f"{name}: {tokens} tokens, near the {TOKEN_LIMIT} limit")
            status = "warn"

        if fchars > FRONTMATTER_LIMIT:
            failures.append(
                f"{name}: description+when_to_use is {fchars} chars, over the "
                f"{FRONTMATTER_LIMIT} limit — the tail is silently truncated."
            )
            status = "FAIL"
        elif fchars > FRONTMATTER_LIMIT * WARN_AT:
            warnings.append(
                f"{name}: frontmatter {fchars} chars, {FRONTMATTER_LIMIT - fchars} "
                f"from truncation"
            )
            status = "warn" if status == "ok" else status

        rows.append((name, lines, tokens, fchars, status))

    width = max(len(r[0]) for r in rows)
    print(f"{'skill':<{width}}  {'lines':>6} {'tokens':>7} {'fm':>6}  status")
    for name, lines, tokens, fchars, status in rows:
        print(f"{name:<{width}}  {lines:>6} {tokens:>7} {fchars:>6}  {status}")
    if mode != "exact":
        print("\nnote: tiktoken unavailable — token counts are estimated")

    if warnings and (verbose or not failures):
        print()
        for w in warnings:
            print(f"warn: {w}")

    if failures:
        print()
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print(f"\nall {len(rows)} skills within limits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
