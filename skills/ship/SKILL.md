---
name: ship
description: Execute an approved plan and ship it — implement, verify, review, commit. Use when the user asks to build, execute, implement, or ship non-trivial work ("execute the plan", "ship this", "implement phases X-Y", "build this feature", "refactor this properly"). Runs each unit of work through a gate table where every gate emits a pass/fail signal, uses a fresh-context reviewer that sees only the diff, and commits one unit at a time.
when_to_use: Any multi-step implementation where a regression would cost more than the work itself. Skip for one-line changes and throwaway scripts.
license: MIT
---

# Ship

You hold the goal and the commit rights. Subagents implement; they never decide
what "done" means and never write to the repository.

The rule this skill exists to enforce: **the thing that judges the work is never
the thing that did the work.** Every gate below is either a command that exits
non-zero, or a reader who did not write the code.

## Before anything

State the unit of work and its check, in one message, before editing:

- **Unit** — the smallest change that is independently shippable.
- **Check** — the exact command proving it works, and its pass condition.

If you cannot name the check, stop and say so. Work without a check is work
whose completion you cannot claim.

## The gate table

Per unit of work, in order. A gate that has not run has not passed.

| # | Gate | Signal |
|---|------|--------|
| 1 | Test observed failing | run it, see red — capture the output |
| 2 | Implementation | — |
| 3 | Test observed passing | same command, now green |
| 4 | Full suite | exit 0 |
| 5 | Lint + typecheck | exit 0 |
| 6 | Held-out suite (if present) | exit 0, never edited |
| 7 | Diff review by fresh context | reviewer verdict |
| 8 | Secrets scan on diff | no hits |
| 9 | Commit | one unit, specific paths |

Gate 1 is not optional and not reorderable. A test that was never observed
failing is not evidence — it may be asserting nothing, or passing on code that
predates it. Paste the red output, then the green output, from the same command.

Gates 4–6 run the real commands. Never report a gate from memory or inference.
If a gate did not run, say "not run" — never "should pass".

## Reviewing

At gate 7, dispatch one subagent with **only the diff** — not your reasoning,
not the plan, not why you chose this approach. Brief it:

> Assume this diff is wrong. Find the specific input or state where it breaks.
> Report only defects in correctness or in the stated requirements. If you find
> nothing, say so plainly.

Scope it to correctness. A reviewer told to find gaps will invent them, and
chasing invented findings produces over-engineering — which is its own defect.

Fix what is real. Argue with what is not, in writing, and move on.

## Committing

One unit per commit, staged by explicit path. `git add -A` is blocked by hook.

Before committing, check what actually changed:

```bash
git status --porcelain
```

Files can appear here that no Edit call produced — a script wrote them, a build
emitted them. Anything you did not intend is not part of this unit.

## When a gate fails twice

Two failed attempts on the same gate means the diagnosis is wrong, not the fix.
Stop fixing. Say what you expected, what happened, and what that rules out.
Ask, or escalate to a new plan. A third attempt at the same theory is where
sessions go to die.

## Phase file

Test files are hook-protected. To write tests, declare it:

```bash
echo red > .claude/ship-phase    # writing tests
echo green > .claude/ship-phase  # implementing
```

Set it back to `green` before implementing. The file exists because a phase you
merely *intend* does not survive compaction; a file does.

## What is enforced mechanically

These need no compliance from you — they are hooks, and they hold whether or
not this text is still in context:

- Subagents cannot run `git commit`, `push`, `stash`, or any repo write.
- Nobody can run `git add -A`, `-u`, or `git add .`.
- Test files cannot be edited while `.claude/ship-phase` is `green`.
- `tests/holdout/**` cannot be edited, ever.
- Session friction is scored at every stop; a postmortem is written when it trips.

If a hook denies you, it is telling you the shape of the work is wrong. Do not
route around it — `python -c "open(...)"` to edit a blocked file is the same
defect as editing it directly, plus concealment.

## Held-out tests

If the repo has `tests/holdout/`, it is the only oracle you cannot tune to.
Everything you can see, you can accidentally fit. Passing a suite you could
read is weak evidence; passing one you could not is strong evidence.

Never propose weakening, skipping, or "temporarily" disabling a held-out test.
If one is genuinely wrong, say so and let a human decide.

## Anti-patterns

- Claiming a gate passed without running it.
- Editing a test so the implementation passes.
- Mocking the thing under test, so the assertion is vacuous.
- Deleting or skipping a failing test to get green.
- `--no-verify`, `-x` to stop at first failure and calling it clean, or
  narrowing the test selection until it passes.
- A comment justifying why a workaround is acceptable. If it needs a paragraph,
  the code is wrong.

## Detail

`reference/gates.md` — per-gate specifics: what each command looks like across
stacks, what a real reviewer brief contains, how to set up a held-out suite.
Read it at the gate that needs it, not up front.
