#!/usr/bin/env python3
"""Lint a repo's brain/ vault. Standard library only.

Usage: python3 brain_lint.py [repo_root] [--stale-days N] [--all]

Prints one block per failing check (count + a few examples), then a summary
line. Exit 1 if any ERROR, 2 if there is no brain/ folder, else 0.
Required frontmatter keys and enums are read from
brain/00_Meta/Frontmatter-Standard.md when present.
"""
import argparse
import collections
import datetime
import os
import pathlib
import re
import sys

MAX_NOTE_LINES, MAX_HOME_LINES, MAX_STATUS_LINES = 200, 120, 60
DUMP_DIR_FILES = 300            # a folder holding more files than this is data, not knowledge
BIG_MD_BYTES = 1_000_000        # a markdown file this big is generated output
ARTIFACT_ERROR_BYTES = 50_000_000
MEDIA = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".canvas"}
SKIP_DIRS = {".obsidian", ".git", ".trash"}
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")
SECRETS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"), "API key (sk-...)"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"), "JWT"),
]


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if not line or line[0] in " \t#-" or ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = re.sub(r"\s+#.*$", "", v).strip().strip("'\"")
    return fm


def read_standard(brain):
    """Return (required keys, type enum, status enum) from Frontmatter-Standard.md.

    Handles inline lists (`a` · `b`) and bullet lists (- `a` — meaning).
    Empty enums mean "not declared": those checks are skipped.
    """
    required, types, statuses = ["type", "status"], set(), set()
    std = brain / "00_Meta" / "Frontmatter-Standard.md"
    if not std.exists():
        return required, types, statuses
    text = FENCE.sub("", std.read_text(encoding="utf-8", errors="replace"))
    m = re.search(r"Required(?: on every note)?(?: keys)?:?\**:?(.*?)(?:Optional|Conditional|\n\*\*|\n\s*\n)", text, re.S)
    if m and re.findall(r"`([\w-]+)`", m.group(1)):
        required = re.findall(r"`([\w-]+)`", m.group(1))
    lines = text.splitlines()
    for key, target in (("`type` enum", types), ("`status` enum", statuses)):
        for i, line in enumerate(lines):
            if line.startswith("#") and key in line:
                for nxt in lines[i + 1:]:
                    if nxt.startswith("#") or nxt.startswith("**"):
                        break
                    tokens = re.findall(r"`([\w-]+)`", nxt)
                    if nxt.lstrip().startswith("- "):
                        tokens = tokens[:1]
                    target.update(tokens)
                break
    return required, types, statuses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--stale-days", type=int, default=180)
    ap.add_argument("--all", action="store_true", help="list every problem, not just examples")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    brain = root / "brain"
    if not brain.is_dir():
        print(f"brain_lint: no brain/ folder in {root}")
        return 2

    found = collections.defaultdict(list)  # (severity, check) -> [detail]

    def add(sev, check, detail):
        found[(sev, check)].append(detail)

    required, types, statuses = read_standard(brain)
    today = datetime.date.today()
    notes = {}  # rel path -> text
    artifact_bytes, artifacts = 0, []

    # brain/.lintignore: one path per line (relative to brain/) for data folders that cannot move yet.
    # They are reported once as data inside brain/, not linted note by note.
    ignore_file = brain / ".lintignore"
    ignored = [] if not ignore_file.exists() else [
        l.strip().strip("/") for l in ignore_file.read_text().splitlines() if l.strip() and not l.startswith("#")]
    for ig in ignored:
        files = [os.path.join(d, f) for d, _, fs in os.walk(brain / ig) for f in fs]
        size = sum(os.path.getsize(f) for f in files)
        add("WARN", "data inside brain/ excluded by .lintignore (move it out when it can)",
            f"{ig}/ — {len(files):,} files, {size / 1e6:,.0f} MB")

    for dirpath, dirnames, filenames in os.walk(brain):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = pathlib.Path(dirpath).relative_to(brain).as_posix()
        if any(rel_dir == ig or rel_dir.startswith(ig + "/") for ig in ignored):
            dirnames[:] = []
            continue
        if len(filenames) > DUMP_DIR_FILES:
            total = sum(len(fs) for _, _, fs in os.walk(dirpath))
            add("ERROR", "data dump inside brain/ (move out, keep a summary note + repo_link)",
                f"{rel_dir}/ — {total:,} files")
            dirnames[:] = []
            continue
        for name in filenames:
            p = pathlib.Path(dirpath) / name
            rel = p.relative_to(brain).as_posix()
            size = p.stat().st_size
            ext = p.suffix.lower()
            if ext != ".md":
                if ext in MEDIA and size < BIG_MD_BYTES:
                    continue
                artifact_bytes += size
                artifacts.append((size, rel))
                continue
            if size > BIG_MD_BYTES:
                add("WARN", "generated-size markdown (raw output, not a note)", f"{rel} — {size // 1_000_000} MB")
                continue
            notes[rel] = p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

    if artifacts:
        sev = "ERROR" if artifact_bytes > ARTIFACT_ERROR_BYTES else "WARN"
        check = f"raw artifacts inside brain/ ({artifact_bytes / 1e6:,.0f} MB in {len(artifacts):,} files)"
        for size, rel in sorted(artifacts, reverse=True):
            add(sev, check, f"{rel} — {size / 1e6:.1f} MB")

    # Link index: stems and extension-less relative paths
    targets = set()
    for rel in notes:
        no_ext = rel[:-3]
        targets.add(no_ext.lower())
        targets.add(pathlib.PurePosixPath(no_ext).name.lower())
    inbound = collections.Counter()

    for rel, text in notes.items():
        is_template = "/Templates/" in f"/{rel}" or rel.startswith("00_Meta/Templates")
        is_archive = rel.startswith("90_Archive/")
        name = pathlib.PurePosixPath(rel).name
        lines = text.count("\n") + 1

        for i, line in enumerate(text.splitlines(), 1):
            for pat, label in SECRETS:
                if pat.search(line):
                    add("ERROR", "possible secret", f"{rel}:{i} ({label})")
                    break

        if is_template:
            continue

        limit = {"Home.md": MAX_HOME_LINES, "Status.md": MAX_STATUS_LINES}.get(rel, MAX_NOTE_LINES)
        if lines > limit and name != "_MOC.md":
            add("WARN", f"note over line budget (Status {MAX_STATUS_LINES}, Home {MAX_HOME_LINES}, notes {MAX_NOTE_LINES})", f"{rel} — {lines} lines")

        fm = frontmatter(text)
        if "/boards/" in f"/{rel}":
            fm = fm or {}  # live boards belong to the agent running them; only links are checked
        elif fm is None:
            add("ERROR", "missing frontmatter", rel)
        else:
            missing = [] if "/boards/" in f"/{rel}" else [k for k in required if not fm.get(k)]
            if missing:
                add("ERROR", "missing required frontmatter keys", f"{rel} — {', '.join(missing)}")
            if types and fm.get("type") and fm["type"] not in types:
                add("ERROR", "type not in enum", f"{rel} — {fm['type']}")
            if statuses and fm.get("status") and fm["status"] not in statuses:
                add("ERROR", "status not in enum", f"{rel} — {fm['status']}")
            if fm.get("status") == "superseded":
                if not is_archive:
                    add("WARN", "superseded note outside 90_Archive/", rel)
                if not fm.get("superseded_by"):
                    add("WARN", "superseded note without superseded_by", rel)
            v = fm.get("verified", "")
            if v and not is_archive:
                try:
                    age = (today - datetime.date.fromisoformat(v[:10])).days
                    if age > args.stale_days:
                        add("WARN", f"verified more than {args.stale_days} days ago", f"{rel} — {age} days")
                except ValueError:
                    add("ERROR", "verified: is not YYYY-MM-DD", f"{rel} — {v}")

        for target in LINK.findall(INLINE_CODE.sub("", FENCE.sub("", text))):
            t = target.strip().removesuffix(".md").lower()
            if not t or any(c in t for c in "<>{}*"):
                continue
            t = t.removeprefix("brain/")
            if t in targets or pathlib.PurePosixPath(t).name in targets:
                inbound[pathlib.PurePosixPath(t).name] += 1
                inbound[t] += 1
            elif not is_archive:
                add("ERROR", "broken [[wikilink]]", f"{rel} → [[{target.strip()}]]")

    for rel in notes:
        name = pathlib.PurePosixPath(rel).name
        if (name in ("_MOC.md", "Home.md", "Status.md") or rel.startswith(("90_Archive/", "00_Meta/Templates"))
                or "/boards/" in rel):
            continue
        no_ext = rel[:-3].lower()
        if not inbound[no_ext] and not inbound[pathlib.PurePosixPath(no_ext).name]:
            add("WARN", "orphan (no inbound [[link]]; link it from its MOC or archive it)", rel)

    agent_files = [root / n for n in ("CLAUDE.md", "AGENTS.md", ".claude/CLAUDE.md") if (root / n).exists()]
    joined = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in agent_files)
    if re.search(r"(^|\s)@\.?/?brain/", joined):
        add("ERROR", "CLAUDE.md @imports the brain (loads it every session; use a plain-text pointer)", "CLAUDE.md")
    elif agent_files and "brain/" not in joined:
        add("WARN", "CLAUDE.md has no pointer to brain/Home.md", agent_files[0].name)

    shown = None if args.all else 5
    errors = warns = 0
    for (sev, check), items in sorted(found.items(), key=lambda kv: (kv[0][0] != "ERROR", -len(kv[1]))):
        if sev == "ERROR":
            errors += len(items)
        else:
            warns += len(items)
        print(f"{sev} {check}: {len(items)}")
        for d in items[:shown]:
            print(f"    {d}")
        if shown and len(items) > shown:
            print(f"    … {len(items) - shown} more (--all)")
    print(f"brain_lint: {errors} errors, {warns} warnings, {len(notes)} notes checked")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
