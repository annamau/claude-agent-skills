#!/usr/bin/env python3
"""Mechanical audit of a Claude Code skill.

Computes what can be counted, so a human or an agent only has to judge what
cannot. Every number here was a hand-audit finding once; each one that becomes
arithmetic is one fewer thing to re-derive.

    python3 scripts/analyze_skill.py                 # all skills, summary
    python3 scripts/analyze_skill.py skills/ship     # one skill, full detail
    python3 scripts/analyze_skill.py --json          # machine-readable

Exit 1 if any skill breaches a hard limit, else 0.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

TOKEN_LIMIT = 5000       # post-compaction re-attachment budget per skill
FRONTMATTER_LIMIT = 1536  # description + when_to_use, truncated in the listing
ROOT = Path(__file__).resolve().parent.parent

# Instruction verbs that assert a hard rule. Each is a candidate for a hook:
# if the skill says it MUST happen, ask why the harness allows it not to.
MANDATE = re.compile(
    r"\b(MUST|ALWAYS|NEVER|REQUIRED|mandatory|non-negotiable|do not|don't|"
    r"cannot|may not|forbidden|blocked|no exceptions)\b", re.IGNORECASE)

# Phrases naming something a machine can decide. Presence suggests a real gate.
SIGNAL = re.compile(
    r"\b(exit code|exit 0|non-zero|returns? \d|pass(es|ed)? condition|"
    r"`[a-z-]+ (test|check|lint|build|run)|pytest|npm (run )?test|cargo test|"
    r"go test|ruff|mypy|tsc|eslint|clippy|gitleaks|--porcelain|grep -|"
    r"git diff|exits?\b|green|red|fails?\b)", re.IGNORECASE)

# Phrases that describe a judgement with no artifact behind it.
VIBES = re.compile(
    r"\b(honest(ly)?|genuinely|truly|real(ly)? solution|ask yourself|"
    r"be rigorous|think hard|carefully consider|make sure you|"
    r"take the time|do not let|resist the|remember to|it is important|"
    r"the most important|do not skip|tempted to)\b", re.IGNORECASE)

# Subagent-spawning language, for the multi-agent justification check.
SPAWN = re.compile(
    r"\b(subagent|sub-agent|dispatch|spawn|Agent tool|SendMessage|"
    r"expert team|in parallel|fan out|fresh context|worker)\b", re.IGNORECASE)


def count_tokens(text: str) -> tuple[int, bool]:
    try:
        import tiktoken
        return len(tiktoken.get_encoding("o200k_base").encode(text)), True
    except Exception:
        return int(len(text) / 3.6), False


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


def compaction_cut(text: str) -> int | None:
    """Line number where post-compaction truncation falls, if it does."""
    total, _ = count_tokens(text)
    if total <= TOKEN_LIMIT:
        return None
    running = ""
    for i, line in enumerate(text.split("\n"), 1):
        running += line + "\n"
        if count_tokens(running)[0] > TOKEN_LIMIT:
            return i
    return None


def repeated_doctrine(text: str, min_len: int = 5) -> list[tuple[str, int]]:
    """Content phrases restated across the skill.

    Doctrine repeated many times is the signature of a skill trying to survive
    by emphasis. It costs budget every time and changes nothing, because the
    model reads the skill once.
    """
    body = re.sub(r"```.*?```", "", text, flags=re.DOTALL).lower()
    body = re.sub(r"[^a-z0-9\s]", " ", body)
    words = body.split()
    stop = {
        "the", "a", "an", "and", "or", "but", "of", "to", "in", "is", "it",
        "that", "this", "for", "on", "as", "with", "by", "at", "from", "be",
        "are", "was", "not", "you", "your", "if", "then", "so", "do", "does",
        "what", "when", "which", "who", "how", "can", "will", "has", "have",
    }
    counts = Counter()
    for n in (min_len, min_len + 2):
        for i in range(len(words) - n):
            gram = words[i:i + n]
            if sum(w in stop for w in gram) > n // 2:
                continue
            counts[" ".join(gram)] += 1
    out = []
    for phrase, n in counts.most_common(40):
        if n < 3:
            continue
        if any(phrase in seen and n <= sn for seen, sn in out):
            continue
        out.append((phrase, n))
    return out[:8]


def classify_lines(text: str) -> dict:
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    mandates, signals, vibes = [], [], []
    for i, line in enumerate(body.split("\n"), 1):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|--"):
            continue
        if MANDATE.search(s):
            mandates.append((i, s[:100]))
        if SIGNAL.search(s):
            signals.append((i, s[:100]))
        elif VIBES.search(s):
            vibes.append((i, s[:100]))
    return {"mandates": mandates, "signals": signals, "vibes": vibes}


def analyze(path: Path) -> dict:
    text = path.read_text()
    tokens, exact = count_tokens(text)
    fm = parse_frontmatter(text)
    fchars = len(fm.get("description", "")) + len(fm.get("when_to_use", ""))
    lines = text.count("\n") + 1
    cut = compaction_cut(text)
    cls = classify_lines(text)

    breaches = []
    if tokens > TOKEN_LIMIT:
        pct = round(100 * (1 - TOKEN_LIMIT / tokens))
        breaches.append(
            f"{tokens} tokens over the {TOKEN_LIMIT} budget — content past line "
            f"{cut} of {lines} (~{pct}%) is dropped after auto-compaction")
    if fchars > FRONTMATTER_LIMIT:
        breaches.append(
            f"description+when_to_use is {fchars} chars, over {FRONTMATTER_LIMIT} "
            f"— the tail is silently truncated in the skill listing")
    if not fm.get("description"):
        breaches.append("no description — the model cannot tell when to invoke this")

    warnings = []
    if tokens > TOKEN_LIMIT * 0.85 and not breaches:
        warnings.append(f"{tokens} tokens: only {TOKEN_LIMIT - tokens} of headroom")
    if fchars > FRONTMATTER_LIMIT * 0.85:
        warnings.append(f"frontmatter {fchars} chars: {FRONTMATTER_LIMIT - fchars} from truncation")
    if "allowed-tools" in fm:
        warnings.append(
            "uses allowed-tools — that is a permission GRANT, not a restriction; "
            "every tool stays callable. Use disallowed-tools or a hook to confine")
    n_sig, n_vibe = len(cls["signals"]), len(cls["vibes"])
    if n_vibe > n_sig:
        warnings.append(
            f"{n_vibe} exhortation lines vs {n_sig} signal-bearing lines — "
            f"the skill leans on emphasis where it could name a check")
    unbacked = len(cls["mandates"]) - n_sig
    if unbacked > 5:
        warnings.append(
            f"~{unbacked} hard rules with no adjacent check — each is a candidate "
            f"for a hook, which enforces without the model's cooperation")

    try:
        shown = str(path.relative_to(ROOT))
    except ValueError:
        shown = str(path)  # a skill outside this repo is a valid target

    return {
        "name": path.parent.name, "path": shown,
        "lines": lines, "tokens": tokens, "exact": exact,
        "frontmatter_chars": fchars, "compaction_cut": cut,
        "has_when_to_use": "when_to_use" in fm,
        "mandates": len(cls["mandates"]), "signals": n_sig, "vibes": n_vibe,
        "spawn_mentions": len(SPAWN.findall(text)),
        "repeated": repeated_doctrine(text),
        "detail": cls, "breaches": breaches, "warnings": warnings,
    }


def print_detail(r: dict) -> None:
    print(f"\n{'=' * 66}\n{r['name']}  ({r['path']})\n{'=' * 66}")
    print(f"  {r['lines']} lines · {r['tokens']} tokens "
          f"({'exact' if r['exact'] else 'estimated'}) · "
          f"frontmatter {r['frontmatter_chars']}/{FRONTMATTER_LIMIT}")
    if r["compaction_cut"]:
        print(f"  COMPACTION CUT at line {r['compaction_cut']} — everything after "
              f"it is dropped")
    else:
        print(f"  survives compaction whole "
              f"({TOKEN_LIMIT - r['tokens']} tokens of headroom)")
    if not r["has_when_to_use"]:
        print("  no when_to_use field (triggers are crammed into description)")

    print(f"\n  lines naming a check ......... {r['signals']}")
    print(f"  lines exhorting effort ...... {r['vibes']}")
    print(f"  hard rules (MUST/NEVER) ..... {r['mandates']}")
    print(f"  subagent references ......... {r['spawn_mentions']}")

    if r["repeated"]:
        print("\n  restated doctrine:")
        for phrase, n in r["repeated"]:
            print(f"    {n}x  \"{phrase}\"")

    if r["detail"]["vibes"]:
        print("\n  exhortation without a check (first 6):")
        for ln, s in r["detail"]["vibes"][:6]:
            print(f"    L{ln}: {s}")

    for b in r["breaches"]:
        print(f"\n  FAIL: {b}")
    for w in r["warnings"]:
        print(f"  warn: {w}")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv

    if args:
        paths = []
        for a in args:
            p = Path(a)
            paths.append(p if p.name == "SKILL.md" else p / "SKILL.md")
    else:
        paths = sorted((ROOT / "skills").glob("*/SKILL.md"))

    paths = [p for p in paths if p.exists()]
    if not paths:
        print("no SKILL.md found", file=sys.stderr)
        return 1

    results = [analyze(p) for p in paths]

    if as_json:
        for r in results:
            r.pop("detail", None)
        print(json.dumps(results, indent=2))
        return 1 if any(r["breaches"] for r in results) else 0

    if len(results) == 1 or args:
        for r in results:
            print_detail(r)
    else:
        w = max(len(r["name"]) for r in results)
        print(f"{'skill':<{w}}  {'lines':>5} {'tokens':>7} {'fm':>5} "
              f"{'sig':>4} {'vibe':>5} {'rule':>5}  status")
        for r in results:
            status = "FAIL" if r["breaches"] else ("warn" if r["warnings"] else "ok")
            print(f"{r['name']:<{w}}  {r['lines']:>5} {r['tokens']:>7} "
                  f"{r['frontmatter_chars']:>5} {r['signals']:>4} "
                  f"{r['vibes']:>5} {r['mandates']:>5}  {status}")
        for r in results:
            for b in r["breaches"]:
                print(f"\nFAIL {r['name']}: {b}")
            for wn in r["warnings"]:
                print(f"warn {r['name']}: {wn}")
        print("\nRun with a skill path for per-line detail.")

    return 1 if any(r["breaches"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
