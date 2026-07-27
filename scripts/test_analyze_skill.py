#!/usr/bin/env python3
"""Contract tests for the skill analyzer.

The analyzer's job is to reproduce mechanically what previously required a hand
audit. The strongest case below pins it against the retired `phases-execution`
skill, whose real numbers are known independently: 14,496 tokens, 628 lines,
a 1,501-char description, and a compaction cut near line 180.

Run: python3 scripts/test_analyze_skill.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_skill import (  # noqa: E402
    FRONTMATTER_LIMIT, analyze, compaction_cut, parse_frontmatter,
    repeated_doctrine,
)

ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []
checks = 0


def check(label, got, want):
    global checks
    checks += 1
    if got != want:
        failures.append(f"{label}: expected {want!r}, got {got!r}")


def check_true(label, cond):
    global checks
    checks += 1
    if not cond:
        failures.append(label)


def skill(body: str, desc: str = "does a thing", extra: str = "") -> Path:
    d = Path(tempfile.mkdtemp()) / "sample"
    d.mkdir()
    (d / "SKILL.md").write_text(
        f"---\nname: sample\ndescription: {desc}\n{extra}---\n\n{body}\n")
    return d / "SKILL.md"


# --- frontmatter -------------------------------------------------------------
fm = parse_frontmatter("---\nname: x\ndescription: hello\n---\nbody\n")
check("parses name", fm.get("name"), "x")
check("parses description", fm.get("description"), "hello")

folded = parse_frontmatter("---\nname: x\ndescription: >-\n  one\n  two\n---\nb\n")
check_true("parses folded scalar", "one" in folded.get("description", ""))
check("no frontmatter yields empty", parse_frontmatter("# heading\n"), {})

# --- compaction --------------------------------------------------------------
check("short text has no cut", compaction_cut("hello world\n"), None)
cut = compaction_cut("\n".join(
    f"line {i} with enough words here to accumulate tokens" for i in range(4000)))
check_true("long text reports a cut line", isinstance(cut, int) and cut > 0)

# --- repeated doctrine -------------------------------------------------------
rep = repeated_doctrine(
    ("never ship a patch instead of a real solution. " * 4)
    + "an unrelated filler sentence about other matters entirely. ")
check_true("detects a phrase repeated 4x", any(n >= 3 for _, n in rep))
check_true("ignores non-repeated prose",
           not repeated_doctrine("a single unique sentence appears here."))

# --- breaches ----------------------------------------------------------------
r = analyze(skill("short body\n"))
check("clean skill has no breaches", r["breaches"], [])
check_true("clean skill reports no cut", r["compaction_cut"] is None)

r = analyze(skill("word " * 9000))
check_true("oversized skill breaches",
           any("dropped after auto-compaction" in b for b in r["breaches"]))
check_true("oversized skill reports a cut line", r["compaction_cut"] is not None)

r = analyze(skill("body\n", desc="x" * (FRONTMATTER_LIMIT + 50)))
check_true("overlong frontmatter breaches",
           any("silently truncated" in b for b in r["breaches"]))

r = analyze(skill("body\n", desc=""))
check_true("missing description breaches",
           any("no description" in b for b in r["breaches"]))

# --- allowed-tools is a grant, not a fence -----------------------------------
r = analyze(skill("body\n", extra="allowed-tools: Bash\n"))
check_true("warns that allowed-tools does not restrict",
           any("GRANT" in w for w in r["warnings"]))

# --- signal vs exhortation ---------------------------------------------------
r = analyze(skill("Run `pytest -q` and require exit 0.\n"
                  "The build must exit non-zero on failure.\n"))
check_true("counts signal-bearing lines", r["signals"] >= 2)

r = analyze(skill(
    "You must be honest with yourself here.\n"
    "Think hard and carefully consider the tradeoffs.\n"
    "It is important that you do not skip this.\n"
    "Remember to take the time to be rigorous.\n"))
check_true("counts exhortation lines", r["vibes"] >= 3)
check_true("flags exhortation exceeding signal",
           any("exhortation" in w for w in r["warnings"]))

# --- unbacked mandates -------------------------------------------------------
r = analyze(skill("\n".join(f"You MUST always perform step {i}." for i in range(12))))
check_true("flags hard rules with no adjacent check",
           any("hard rules" in w for w in r["warnings"]))

# --- out-of-repo paths -------------------------------------------------------
outside = Path(tempfile.mkdtemp()) / "elsewhere"
outside.mkdir()
(outside / "SKILL.md").write_text("---\nname: e\ndescription: d\n---\nbody\n")
try:
    r = analyze(outside / "SKILL.md")
    check("analyzes a skill outside the repo", r["name"], "elsewhere")
except Exception as exc:
    checks += 1
    failures.append(f"crashed on an out-of-repo path: {exc}")

# --- ground truth ------------------------------------------------------------
old = subprocess.run(
    ["git", "-C", str(ROOT), "show", "00e01f4:skills/phases-execution/SKILL.md"],
    capture_output=True, text=True)
if old.returncode == 0 and old.stdout:
    d = Path(tempfile.mkdtemp()) / "phases-execution"
    d.mkdir()
    (d / "SKILL.md").write_text(old.stdout)
    r = analyze(d / "SKILL.md")
    check("ground truth: tokens", r["tokens"], 14496)
    check("ground truth: lines", r["lines"], 628)
    check("ground truth: frontmatter chars", r["frontmatter_chars"], 1501)
    check_true("ground truth: cut lands near line 180",
               r["compaction_cut"] is not None and 175 <= r["compaction_cut"] <= 190)
    check_true("ground truth: breaches the token budget",
               any("dropped after auto-compaction" in b for b in r["breaches"]))
    check_true("ground truth: finds the repeated patch doctrine",
               any("patch" in p for p, _ in r["repeated"]))
    check_true("ground truth: hard rules far exceed checks",
               r["mandates"] > r["signals"] * 2)
else:
    checks += 1
    failures.append("ground truth: could not read the retired skill from git")

if failures:
    print(f"FAILED {len(failures)}/{checks}\n")
    for f in failures:
        print(f"  ✗ {f}")
    sys.exit(1)
print(f"PASSED {checks}/{checks}")
