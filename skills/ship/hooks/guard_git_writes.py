#!/usr/bin/env python3
"""Deny repository-mutating git commands to subagents, and `git add -A` to everyone.

PreToolUse hook for Bash. Two rules:

1. Subagents never write to the repo. Workers implement; the lead commits.
   A subagent is identified by `agent_id` in the hook payload.
2. Nobody runs `git add -A` / `-u` / bare `git add .`, in any context.
   Blanket staging is how unrelated work lands in an atomic commit.

Denies are returned as JSON so the model sees a reason it can act on, rather
than an opaque failure. Exit code stays 0 — the decision is in the payload.

Fails OPEN on unparseable input: a hook that crashes closed would trap the
session with no documented escape.
"""

from __future__ import annotations

import json
import re
import shlex
import sys

# Commands that mutate the repository or its history.
WRITE_SUBCOMMANDS = {
    "commit", "add", "push", "merge", "rebase", "reset", "revert",
    "cherry-pick", "stash", "am", "apply", "checkout", "switch",
    "restore", "clean", "rm", "mv", "tag", "branch", "worktree",
    "filter-branch", "gc", "prune", "update-ref", "symbolic-ref",
}

# Read-only forms of otherwise-mutating subcommands.
READONLY_FORMS = (
    re.compile(r"^branch\s+(--list|-l|--show-current|-a|--all|-r|--remotes|-v|-vv)?\s*$"),
    re.compile(r"^tag\s+(-l|--list)\b"),
    re.compile(r"^stash\s+(list|show)\b"),
    re.compile(r"^worktree\s+list\b"),
)

BLANKET_ADD = re.compile(r"\bgit\s+add\s+(-A\b|--all\b|-u\b|--update\b|\.\s*$|\.\s)")

# Shell operators that separate independent commands.
SPLIT = re.compile(r"\s*(?:&&|\|\||;|\|&|\||\n)\s*")

# Wrappers Claude Code does not strip, which would otherwise smuggle a git call.
WRAPPERS = {
    "timeout", "time", "nice", "nohup", "stdbuf", "command", "builtin",
    "noglob", "xargs", "env", "sudo", "doas", "watch", "setsid",
    "ionice", "flock", "direnv", "devbox", "mise", "rye", "uv", "poetry",
}


def strip_heredocs(command: str) -> str:
    """Drop heredoc bodies before scanning.

    A commit message or file written via `<<'EOF'` is data, not a command.
    Scanning it produces false denials on text that merely mentions a blocked
    command — which is exactly how this hook first misfired.
    """
    out, lines = [], command.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
        if m:
            terminator = m.group(2)
            i += 1
            while i < len(lines) and lines[i].strip() != terminator:
                i += 1
            if i < len(lines):
                out.append(lines[i])  # keep the terminator line
        i += 1
    return "\n".join(out)


def segments(command: str):
    for raw in SPLIT.split(strip_heredocs(command)):
        raw = raw.strip()
        if raw:
            yield raw


def strip_wrappers(tokens: list[str]) -> list[str]:
    """Peel wrapper commands and env assignments off the front."""
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if "=" in tok and not tok.startswith("-") and re.match(r"^[A-Za-z_]\w*=", tok):
            i += 1
            continue
        if tok in WRAPPERS:
            i += 1
            # Skip the wrapper's own flags/args (e.g. `timeout 30`, `devbox run`).
            while i < len(tokens) and (
                tokens[i].startswith("-") or re.match(r"^\d+[smhd]?$", tokens[i])
                or tokens[i] in {"run", "exec", "shell"}
            ):
                i += 1
            continue
        break
    return tokens[i:]


def git_write_reason(segment: str) -> str | None:
    """Return a denial reason if this segment mutates the repo, else None."""
    try:
        tokens = shlex.split(segment)
    except ValueError:
        tokens = segment.split()
    tokens = strip_wrappers(tokens)
    if not tokens:
        return None

    exe = tokens[0].rsplit("/", 1)[-1]
    if exe != "git":
        return None

    rest = tokens[1:]
    # Skip git's own global flags, including -C <path> and --git-dir=<p>.
    i = 0
    while i < len(rest):
        if rest[i] in ("-C", "--git-dir", "--work-tree", "--namespace"):
            i += 2
            continue
        if rest[i].startswith("-"):
            i += 1
            continue
        break
    if i >= len(rest):
        return None

    sub = rest[i]
    tail = " ".join(rest[i:])
    if any(p.match(tail) for p in READONLY_FORMS):
        return None
    if sub in WRITE_SUBCOMMANDS:
        return f"`git {sub}`"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # fail open

    if payload.get("tool_name") != "Bash":
        return 0

    command = str(payload.get("tool_input", {}).get("command", ""))
    if not command.strip():
        return 0

    is_subagent = bool(payload.get("agent_id"))
    deny = None
    # Heredoc bodies are data (commit messages, file contents), not commands.
    executable = strip_heredocs(command)

    if BLANKET_ADD.search(executable):
        deny = (
            "Blanket staging is blocked. `git add -A`, `-u`, and `git add .` "
            "sweep unrelated files into the commit. Stage the specific paths "
            "this change touches: `git add path/one path/two`."
        )
    elif is_subagent:
        for seg in segments(command):
            what = git_write_reason(seg)
            if what:
                deny = (
                    f"{what} is blocked for subagents. Workers implement; the "
                    "lead reviews and commits. Finish your edits and report "
                    "what you changed — the lead will stage and commit it. "
                    "Read-only git (status, log, diff, show) is allowed."
                )
                break

    if not deny:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": deny,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
