# claude-agent-skills

Skills and hooks for [Claude Code](https://claude.com/claude-code) that make AI-assisted work verifiable: plan it, build it behind gates that emit real pass/fail signals, and learn from sessions that went badly.

The through-line: **the thing that judges the work is never the thing that did the work** — and wherever a rule can be a mechanism instead of a sentence, it is a mechanism. Skill prose is advisory; a hook is not.

## The skills

| Skill | Use when |
|---|---|
| **plan** (`plan-with-review`) | A non-trivial idea and no plan. A small expert team researches online and in your codebase, surfaces conflicts, drafts a plan, then verifies it against live ground truth before code exists. |
| **ship** | Executing approved work. Each unit runs a gate table where every gate is a command with an exit code or a reader who did not write the code. One unit per commit. |
| **brain** | A repo-based company brain (linked markdown). Recall before work, file findings after, garden on a schedule. |

`plan → ship` is the pipeline; **brain** is the memory either end reads from and writes to.

## The hooks (this is the part that actually holds)

`skills/ship/hooks/` — wire these into `.claude/settings.json` and they enforce
without your compliance:

| Hook | Enforces |
|---|---|
| `guard_git_writes.py` | Subagents cannot commit, push, or stash. Nobody runs `git add -A`. |
| `guard_tests.py` | Test files are not editable during implementation; `tests/holdout/**` is never editable. |
| `session_health.py` | Scores every session for friction; writes a postmortem when it trips. |

`python3 skills/ship/hooks/test_hooks.py` — 38 contract tests. Run before wiring.

## Why it is shaped this way

Each of these is a measured finding, not a preference:

- **Skills must fit in ~5,000 tokens.** After auto-compaction Claude Code re-attaches only the first 5,000 tokens of a skill. A previous version of `ship` was 14,496 tokens — 66% of it, including every gate, was silently dropped at exactly the moment it was needed. `scripts/check_skills.py` enforces the limit in CI.
- **Agents saturate any test suite they can see.** Across 30 systems-level tasks, models scored near-identically on visible tests while held-out performance diverged sharply, and the gap grew with codebase size. Hence `tests/holdout/`.
- **Blocking test edits during implementation is the highest-value single gate.** Penalising test modification cut hacked solutions from 28.57% to 0.56% while *raising* legitimate solve rate. Agent commits modify test files ~23% of the time versus ~13% for humans.
- **A test never observed failing is not evidence.** Red before green, same command both times.
- **Subagents are for context isolation, fresh-context review, and research fan-out.** Not for org charts. Role hierarchies were tried at scale and produced weak ideas and poor experiment hygiene; the coordination cost bought nothing the context budget argument doesn't already justify.
- **Sessions leave measurable evidence of going wrong.** Grind depth, error streaks, repeat-edit counts and verify-loop length separate healthy sessions from bad ones. Thresholds in `session_health.py` were calibrated on a real 150MB transcript corpus, not chosen.

## Install

```bash
for s in skills/*/; do
  ln -s "$(pwd)/$s" "$HOME/.claude/skills/$(basename "$s")"
done
```

Then `/plan-with-review`, `/ship`, `/brain` are available.

To wire the hooks, add to your project's `.claude/settings.json` (project-local
is strongly preferred over global — a `PreToolUse` deny has no documented escape
mechanism, so scope it to one repo first):

```jsonc
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command",
          "command": "python3 \"$HOME/code/claude-agent-skills/skills/ship/hooks/guard_git_writes.py\"" }] },
      { "matcher": "Edit|Write|NotebookEdit|MultiEdit",
        "hooks": [{ "type": "command",
          "command": "python3 \"$HOME/code/claude-agent-skills/skills/ship/hooks/guard_tests.py\"" }] }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "timeout": 60,
        "command": "python3 \"$HOME/code/claude-agent-skills/skills/ship/hooks/session_health.py\"" }] }
    ]
  }
}
```

Note: `claude -p --bare` skips hook discovery entirely. If you run headless in
CI, pass `--settings` explicitly or re-run the same checks as CI steps —
otherwise the enforcement silently is not there.

## Configuration (making them yours)

The skills are written generically. A few call sites reference **placeholders** you supply for your own project:

| Placeholder | Meaning | Example |
|---|---|---|
| `{{REPO}}` | GitHub `owner/repo` slug for PR/review commands | `octocat/hello-world` |
| `{{REVIEW_BOT_LOGIN}}` | Login of your cross-model reviewer bot (match with `startswith`, it has a `[bot]` suffix) | `chatgpt-codex-connector[bot]` |
| `{{CROSS_MODEL_REVIEW_CMD}}` | CLI invocation for local cross-model review | `codex exec review --commit <sha> -s read-only` |

The recommended pattern is a single local **`ADAPTER.<project>.md`** file (gitignored) that pins these values plus any project-specific keystone-note names and taxonomy. `ADAPTER.example.md` in this repo is a template — copy it, fill it in, keep it out of git.

## Provenance

Distilled from real production use and a July 2026 research sweep across supervisor/orchestrator patterns, shared-worktree concurrency, cross-model verification, poisoned-session detection, and the agentic-engineering canon (Anthropic, 12-Factor Agents, LYT/PKM, ADR practice, and the self-preference-bias literature). See each skill's header for its specific grounding.

## License

MIT — see [LICENSE](LICENSE).
