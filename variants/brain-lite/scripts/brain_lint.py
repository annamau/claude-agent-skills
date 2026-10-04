#!/usr/bin/env python3
"""Lint a project's brain/ folder. Standard library only.

Usage: python brain_lint.py [project_root] [--stale-days N]

Prints only problems, then one summary line. Exit code 1 if any ERROR,
2 if there is no brain/ folder, else 0.
"""
import argparse
import datetime
import pathlib
import re
import sys

LIMIT_INDEX, LIMIT_FILE, LIMIT_DECISION = 60, 150, 20
STATUSES = {"active", "proposed", "superseded"}
DECISION_NAME = re.compile(r"^(\d{4})-[a-z0-9][a-z0-9-]*\.md$")

SECRETS = [  # (pattern, label, severity)
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key", "ERROR"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"), "API key (sk-...)", "ERROR"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"), "GitHub token", "ERROR"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key", "ERROR"),
    (re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*['\"]?[^\s'\"<>${}]{8,}"),
     "value after a secret-like name (use env var names only)", "WARN"),
]


def parse(text):
    """Return (frontmatter dict, line offset). Minimal 'key: value' parser."""
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return {}, 0
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        v = re.sub(r"\s+#.*$", "", v).strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        fm[k.strip()] = v
    return fm, m.group(0).count("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--stale-days", type=int, default=180)
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    brain = root / "brain"
    if not brain.is_dir():
        print(f"brain_lint: no brain/ folder in {root}")
        return 2

    problems = []  # (severity, location, message)

    def add(sev, loc, msg):
        problems.append((sev, loc, msg))

    files = sorted(p for p in brain.rglob("*.md"))
    today = datetime.date.today()
    index_path = brain / "INDEX.md"
    index_text = ""
    meta = {}  # rel path -> frontmatter

    if not index_path.exists():
        add("ERROR", "brain/", "INDEX.md is missing")
    else:
        index_text = index_path.read_text(encoding="utf-8", errors="replace")

    for p in files:
        rel = p.relative_to(brain).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        lines = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        fm, _ = parse(text)
        meta[rel] = fm
        is_index = rel == "INDEX.md"
        is_decision = rel.startswith("decisions/")
        is_archive = rel.startswith("decisions/archive/")

        # Length budgets
        limit = LIMIT_INDEX if is_index else LIMIT_DECISION if is_decision else LIMIT_FILE
        if lines > limit:
            add("ERROR", rel, f"{lines} lines, budget is {limit}: split or prune")
        elif lines >= 0.9 * limit:
            add("WARN", rel, f"{lines}/{limit} lines, close to budget")

        # Secrets
        for i, line in enumerate(text.splitlines(), 1):
            for pat, label, sev in SECRETS:
                if pat.search(line):
                    add(sev, f"{rel}:{i}", f"looks like a secret: {label}")
                    break

        if is_index:
            continue

        # Index drift (decisions are covered by the 'decisions/' line)
        if not is_decision and rel not in index_text:
            add("ERROR", rel, "not listed in INDEX.md")

        # Frontmatter: verified date, staleness, covers paths
        v = fm.get("verified", "")
        if not v:
            add("WARN", rel, "missing 'verified:' date")
        else:
            try:
                d = datetime.date.fromisoformat(v)
                if not is_archive and (today - d).days > args.stale_days:
                    add("WARN", rel, f"verified {(today - d).days} days ago: re-check or update")
            except ValueError:
                add("ERROR", rel, f"'verified: {v}' is not YYYY-MM-DD")
        covers = fm.get("covers", [])
        if isinstance(covers, str):
            covers = [covers] if covers else []
        for c in covers:
            if "*" in c:
                continue
            if not (root / c.rstrip("/")).exists():
                add("WARN", rel, f"covers '{c}' not found: stale?")

        # Decision rules
        if is_decision:
            name = p.name
            if not DECISION_NAME.match(name):
                add("ERROR", rel, "name must look like 0007-topic.md")
            status = fm.get("status", "")
            if status not in STATUSES:
                add("ERROR", rel, f"status must be one of {sorted(STATUSES)}")
            elif is_archive and status != "superseded":
                add("ERROR", rel, "archived decision must be 'status: superseded'")
            elif not is_archive and status == "superseded":
                add("ERROR", rel, "superseded decision must move to decisions/archive/")
            if is_archive and not fm.get("superseded_by"):
                add("ERROR", rel, "archived decision needs 'superseded_by:'")

    # Decision ids and supersede chain
    ids = {}
    for rel in meta:
        m = DECISION_NAME.match(pathlib.PurePosixPath(rel).name)
        if rel.startswith("decisions/") and m:
            if m.group(1) in ids:
                add("ERROR", rel, f"duplicate decision id {m.group(1)} (also {ids[m.group(1)]})")
            ids[m.group(1)] = rel
    for rel, fm in meta.items():
        if not rel.startswith("decisions/"):
            continue
        sup = fm.get("supersedes", "")
        if sup:
            if sup not in ids:
                add("ERROR", rel, f"supersedes {sup}, which does not exist")
            elif meta[ids[sup]].get("status") != "superseded":
                add("ERROR", rel, f"supersedes {sup}, but {sup} is not marked superseded")
        by = fm.get("superseded_by", "")
        if by and by not in ids:
            add("ERROR", rel, f"superseded_by {by}, which does not exist")

    # INDEX entries must point at real files; 'decisions/' must be mentioned
    for tok in sorted(set(re.findall(r"[\w./-]+\.md", index_text))):
        if "NNNN" in tok or tok == "INDEX.md":
            continue
        if not (brain / tok).exists():
            add("ERROR", "INDEX.md", f"lists '{tok}', which does not exist")
    if any(r.startswith("decisions/") for r in meta) and "decisions/" not in index_text:
        add("ERROR", "INDEX.md", "has no line for decisions/")

    # Pointer in CLAUDE.md / AGENTS.md; no @import of the brain
    agent_files = [root / n for n in ("CLAUDE.md", "AGENTS.md") if (root / n).exists()]
    if not agent_files:
        add("WARN", "CLAUDE.md", "not found: agents will not know the brain exists")
    else:
        joined = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in agent_files)
        if "brain/INDEX.md" not in joined:
            add("WARN", agent_files[0].name, "no pointer to brain/INDEX.md")
        if re.search(r"@\.?/?brain/", joined):
            add("ERROR", agent_files[0].name, "@import of brain/ loads it every session: use a plain-text pointer")

    errors = sum(1 for s, _, _ in problems if s == "ERROR")
    warns = len(problems) - errors
    for sev, loc, msg in sorted(problems, key=lambda x: (x[0] != "ERROR", x[1])):
        print(f"{sev} {loc}: {msg}")
    print(f"brain_lint: {errors} errors, {warns} warnings, {len(files)} files")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
