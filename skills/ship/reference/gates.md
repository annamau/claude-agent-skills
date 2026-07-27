# Gate detail

Read the section for the gate you are at. Not front to back.

## Gate 1 — test observed failing

Run the new test before the implementation exists. You are looking for a
failure that names the missing behaviour:

```
FAILED tests/test_auth.py::test_refresh_after_expiry - AttributeError: 'NoneType'
```

A test that passes here is testing nothing new — either the behaviour already
exists, or the assertion is vacuous. Both mean stop and find out which.

Capture the actual output. "I expect this to fail" is not gate 1.

Set the phase file first, or the hook will block the edit:

```bash
echo red > .claude/ship-phase
```

## Gate 3 — test observed passing

The same command as gate 1, unmodified. Not a narrowed selection, not with
`-k` added, not a different file. If the command changed between red and green,
the pair proves nothing.

Set the phase back before implementing:

```bash
echo green > .claude/ship-phase
```

## Gates 4–5 — suite, lint, typecheck

Run the project's real commands. Common shapes:

| Stack | Suite | Lint / types |
|---|---|---|
| Python | `pytest -q` | `ruff check .` · `mypy .` |
| Node | `npm test` | `npm run lint` · `npx tsc --noEmit` |
| Go | `go test ./...` | `go vet ./...` |
| Rust | `cargo test` | `cargo clippy -- -D warnings` |

The pass condition is exit 0 on the whole suite. Not "the tests I care about".
A suite narrowed until it passes is the same defect as a weakened assertion.

If the suite is too slow to run per unit, that is a harness problem worth
fixing — not a reason to skip the gate. Say so and propose the fix.

## Gate 6 — held-out suite

If `tests/holdout/` exists, run it. It is hook-protected against editing, in
every phase, deliberately.

The reason it exists: agents saturate any suite they can see. Measured across
30 systems-level tasks, models scored near-identically on visible tests while
held-out performance diverged sharply — and the gap widened with codebase size.
The visible suite stops being informative exactly when the work gets big.

Setting one up:

1. `mkdir -p tests/holdout`
2. Write tests there that exercise the same features from a different angle —
   composition, error paths, boundaries — not copies of the visible ones.
3. Add `tests/holdout/` to whatever excludes files from agent context.
4. Run it in CI, and locally at gate 6.

Written by a human, or by an agent that never sees the implementation. A
held-out suite written by the same agent that wrote the code is not held out.

## Gate 7 — the reviewer brief

One subagent. Give it the diff and nothing else — no plan, no rationale, no
history. Provenance is what biases a reviewer toward agreement.

```
Review this diff. Assume it is wrong.

<diff>

Find the specific input, state, or sequence where this breaks. For each defect:
what breaks, the concrete conditions, and the line.

Only correctness and the stated requirements. Not style, not naming, not
hypothetical future needs. If you find nothing, say so plainly — do not
manufacture findings.
```

Then triage honestly:

- **Real and in scope** — fix it, re-run gates 3–6.
- **Real but out of scope** — write it down, ship, file it.
- **Not real** — say why in one sentence, move on.

Do not fix a finding you believe is wrong to make the reviewer quiet. That is
how over-engineering enters through the review door.

## Gate 8 — secrets

```bash
git diff --cached | grep -nEi '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)[^a-z]'
```

Or `gitleaks protect --staged` if installed. Any hit stops the commit until
resolved — a real secret gets rotated, not just unstaged, because it is already
in your shell history and possibly your reflog.

## Gate 9 — commit

```bash
git status --porcelain
git add path/one path/two
git commit -m "..."
```

`git add -A` is hook-blocked. Stage what belongs to this unit.

Check `git status --porcelain` even when you think you know what changed —
build output, scripts writing files, and tooling all produce files no Edit call
touched, and they are invisible to edit-based tracking.

## Escalating

Two failed attempts on one gate means the theory is wrong. Write down:

- what you expected
- what happened
- what that rules out

Then ask, or go back to planning. The third attempt at the same theory is
where sessions turn into loops — and it is the pattern the session-health hook
scores most heavily.

## Reading a postmortem

`.claude/postmortems/` fills when a session trips a friction threshold. The
signals, and what each usually means:

| Signal | Usual cause |
|---|---|
| grind ≥ 100 tool calls | no check existed, so nothing could stop the agent |
| same file edited ≥ 15× | the fix location is wrong |
| edit ping-pong ≥ 25 | two files disagree; the interface between them is the bug |
| error rate ≥ 12% | the environment is broken, not the code |
| error streak ≥ 4 | fixing symptoms, not the cause |
| verify re-run ≥ 5× | waiting for a different result from the same input |
| interrupts ≥ 2 | the human saw drift before the agent did |
| test files edited | check whether they were made weaker or made correct |

The useful question is never "which of these fired" — it is: **what single
check, had it existed, would have caught this at minute two instead of hour
two?** Build that check. That is the whole loop.
