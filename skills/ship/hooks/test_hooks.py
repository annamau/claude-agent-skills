#!/usr/bin/env python3
"""Contract tests for the ship hooks.

Run: python3 test_hooks.py

These hooks can block tool calls, so the failure mode of a bug is a trapped
session. Every rule below is a case that must hold before the hooks are wired
into settings, including the fail-open behaviour on malformed input.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
GIT = HERE / "guard_git_writes.py"
TESTS = HERE / "guard_tests.py"


def run(script: Path, payload: dict, env_extra: dict | None = None) -> dict:
    import os
    env = {**os.environ, **(env_extra or {})}
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload), capture_output=True, text=True, env=env,
    )
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    if not proc.stdout.strip():
        return {}
    return json.loads(proc.stdout)


def denied(result: dict) -> bool:
    return (
        result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
    )


def bash(cmd: str, agent: bool = False) -> dict:
    p = {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": "/repo"}
    if agent:
        p["agent_id"] = "sub-1"
    return p


def edit(path: str, cwd: str = "/repo") -> dict:
    return {"tool_name": "Edit", "tool_input": {"file_path": path}, "cwd": cwd}


CASES: list[tuple[str, bool, dict, Path, dict]] = []


def case(name, expect_deny, payload, script, env=None):
    CASES.append((name, expect_deny, payload, script, env or {}))


# --- git guard: subagent writes blocked -------------------------------------
case("subagent git commit", True, bash("git commit -m x", agent=True), GIT)
case("subagent git push", True, bash("git push origin main", agent=True), GIT)
case("subagent git stash", True, bash("git stash", agent=True), GIT)
case("subagent git checkout", True, bash("git checkout -b feat", agent=True), GIT)
case("subagent git -C write", True, bash("git -C /repo commit -m x", agent=True), GIT)
case("subagent chained write", True,
     bash("npm test && git commit -m x", agent=True), GIT)
case("subagent wrapped write", True,
     bash("timeout 30 git commit -m x", agent=True), GIT)
case("subagent devbox-wrapped write", True,
     bash("devbox run git push", agent=True), GIT)
case("subagent env-prefixed write", True,
     bash("GIT_AUTHOR_NAME=x git commit -m y", agent=True), GIT)

# --- git guard: reads always allowed ----------------------------------------
case("subagent git status", False, bash("git status", agent=True), GIT)
case("subagent git diff", False, bash("git diff --name-only", agent=True), GIT)
case("subagent git log", False, bash("git log --oneline -5", agent=True), GIT)
case("subagent git branch --list", False, bash("git branch --list", agent=True), GIT)
case("subagent git stash list", False, bash("git stash list", agent=True), GIT)
case("subagent worktree list", False, bash("git worktree list", agent=True), GIT)

# --- git guard: lead may write ----------------------------------------------
case("lead git commit", False, bash("git commit -m x"), GIT)
case("lead git push", False, bash("git push"), GIT)

# --- git guard: blanket add denied for everyone -----------------------------
case("lead git add -A", True, bash("git add -A"), GIT)
case("lead git add --all", True, bash("git add --all"), GIT)
case("lead git add -u", True, bash("git add -u"), GIT)
case("lead git add .", True, bash("git add ."), GIT)
case("lead git add specific paths", False, bash("git add src/a.py src/b.py"), GIT)

# --- git guard: non-git untouched -------------------------------------------
case("non-git command", False, bash("npm run build", agent=True), GIT)
case("word 'git' in a string", False,
     bash("echo 'run git commit later'", agent=True), GIT)

# --- git guard: heredoc bodies are data, not commands ------------------------
# Regression: the hook denied a commit whose *message* described `git add -A`.
# Text inside a heredoc is content being written, never a command being run.
case("commit message mentioning blanket add", False,
     bash("git commit -F - <<'MSG'\nfix: stop using git add -A\nMSG"), GIT)
case("commit message mentioning git commit", False,
     bash("git commit -F - <<'EOF'\ndocs: explain git commit rules\nEOF"), GIT)
case("subagent heredoc writing docs about git push", False,
     bash("cat > doc.md <<'EOF'\nRun git push when ready.\nEOF", agent=True), GIT)
case("real blanket add after a heredoc still denied", True,
     bash("cat > a.txt <<'EOF'\nhello\nEOF\ngit add -A"), GIT)
case("subagent real commit after heredoc still denied", True,
     bash("cat > a.txt <<'EOF'\nhi\nEOF\ngit commit -m x", agent=True), GIT)

# --- test guard: holdout is absolute ----------------------------------------
case("holdout edit blocked (green)", True, edit("/repo/tests/holdout/t.py"), TESTS)
case("holdout edit blocked (red)", True, edit("/repo/tests/holdout/t.py"), TESTS,
     {"SHIP_PHASE": "red"})

# --- test guard: phase-gated ------------------------------------------------
case("test edit blocked in green", True, edit("/repo/tests/test_a.py"), TESTS)
case("test edit allowed in red", False, edit("/repo/tests/test_a.py"), TESTS,
     {"SHIP_PHASE": "red"})
case("spec file blocked in green", True, edit("/repo/src/a.test.ts"), TESTS)
case("spec file allowed in red", False, edit("/repo/src/a.test.ts"), TESTS,
     {"SHIP_PHASE": "red"})
case("conftest blocked in green", True, edit("/repo/tests/conftest.py"), TESTS)

# --- test guard: source always editable -------------------------------------
case("source edit in green", False, edit("/repo/src/main.py"), TESTS)
case("source edit in red", False, edit("/repo/src/main.py"), TESTS,
     {"SHIP_PHASE": "red"})
case("file merely named latest.py", False, edit("/repo/src/latest.py"), TESTS)

# --- both: fail open on junk ------------------------------------------------
case("git guard ignores non-Bash", False, edit("/repo/src/a.py"), GIT)
case("test guard ignores Bash", False, bash("git commit -m x"), TESTS)


def main() -> int:
    failures = []
    for name, expect_deny, payload, script, env in CASES:
        try:
            result = run(script, payload, env)
            got = denied(result)
        except Exception as exc:
            failures.append((name, f"raised {exc}"))
            continue
        if got != expect_deny:
            failures.append((
                name,
                f"expected {'DENY' if expect_deny else 'ALLOW'}, "
                f"got {'DENY' if got else 'ALLOW'}",
            ))

    # Malformed stdin must fail open, not crash the session.
    for script in (GIT, TESTS):
        proc = subprocess.run(
            [sys.executable, str(script)], input="not json{{",
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            failures.append((f"{script.name} malformed stdin",
                             f"exited {proc.returncode}, must be 0"))
        if proc.stdout.strip():
            failures.append((f"{script.name} malformed stdin",
                             "emitted a decision; must fail open"))

    total = len(CASES) + 2
    if failures:
        print(f"FAILED {len(failures)}/{total}\n")
        for name, why in failures:
            print(f"  ✗ {name}: {why}")
        return 1
    print(f"PASSED {total}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
