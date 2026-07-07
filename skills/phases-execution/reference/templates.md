# phases-execution — formats & templates

Loaded on demand from SKILL.md at the step that uses each section. Paste formats verbatim — do not paraphrase them.

## 1. Refined Acceptance Criteria document (pre-flight C)

```
## Phase N — Acceptance Criteria

### Must-pass (hard gates — phase does not ship if any fail)
- [Specific, measurable, falsifiable — number + unit + verification method]
- [Another]
- Advisory requirements from [Expert name]: [list non-negotiables]
- Security floor: secrets scan clean; new dependencies verified + pinned; injection misuse test where input handling changes
- Operational readiness (behavior-changing phases): the observability signal and the turn-off path exist and are named

### Should-pass (soft gates — flag to user if they fail, don't auto-block)
- [Performance target that can slip one iteration]
- [Coverage target that may need a waiver]

### Verification method per gate
- Gate 1: verified by [unit test / integration test / E2E / metric query / code inspection]
- Gate 2: ...

### What "done" looks like in plain language
[One sentence. Not "tests pass." Something like: "A user can trigger a topic scout, see ranked suggestions with freshness scores, and the cron picks up the org without manual intervention."]
```

## 2. Dependency graph format (pre-flight D)

```
## Dependency graph

Nodes: Phase 1, Phase 2, ..., Phase N
Edges: Phase B → Phase A means "B depends on A landing first"

For each edge, name the reason:
- "B reads a column A creates"
- "B's exit gate measures a metric A populates"
- "B and A both edit file X — must serialize"
- "B's test fixture depends on A's seed data"

Per node: gear (FULL/LITE) + expected diff size (flag > ~400 changed lines for a split)

Round 1 (parallel): [phases with no incoming edges]
Round 2 (parallel): [phases whose deps are all in round 1]
...
```

## 3. Workflow board — BOARD.md (pre-flight G)

Lives at `brain/55_Execution/boards/<workflow-slug>/BOARD.md` (fallback: `docs/boards/<workflow-slug>/BOARD.md`). **Single writer: the hawk.** Update at every gate transition, steer, kill, and decision — never in end-of-round batches.

```markdown
---
type: board
title: <Workflow name>
status: active          # active | blocked | closed
created: <ISO date>
updated: <ISO date>
---
# Board — <workflow name>

**Goal:** <one sentence, from the plan>  ·  **Plan:** <path + version>  ·  **North Star:** <metric>
**Worktree:** <path>  ·  **Branch:** hawk/<slug>  ·  **PR:** <url or —>

## Roster (live)
| Expert | Model | Phase(s) | Status | Agent id |
|--------|-------|----------|--------|----------|
| <role> | sonnet | 2 | implementing | <id> |

## File-ownership map
| Phase | Owner | Exclusive file set |
|-------|-------|--------------------|
| 2 | <role> | apps/api/src/x.py, apps/api/tests/test_x.py |
Ledger files (never owned, claim via LOCKS.md): <paths or "none">

## Tasks
### Phase N — <name>   [pending | implementing | review | looping | accepted | committed | blocked]
- Gear: FULL/LITE · Loop count: 0 · Commit: <sha or —>
- Gates: [ ] review · [ ] tests · [ ] 5a security · [ ] 5c cross-model (e.g. Codex) · [ ] PO · [ ] consistency
- Cross-model (5c) findings: <P2/P3 carried to PR round, dismissed-FP evidence lines>
- Notes: <delta-scope, steers issued, worker questions answered>

## Activity log (append-only, newest first)
- <ISO datetime> — <event: dispatched / steered / killed+respawned / gate passed / committed>

## Decisions
- <ISO date> — <decision + why>  (or link DECISIONS.md)

## Postmortems
- <link(s) into brain/55_Execution/postmortems/, or "none">
```

## 4. Phase contract + AC (Step 1)

```
## Phase N contract + AC

### Owned files / modules
- Exact file paths the phase is allowed to edit
- Exact directories the phase is allowed to add files inside
- Inherited from Team Roster: [technical expert name] owns this domain

### Inputs
- Data sources the phase reads (tables, APIs, env vars)
- Schema / shape of each input (columns, types, units)
- Where the input comes from (prior phase / already-shipped system)

### Outputs
- Data the phase produces (tables, columns, endpoints, files)
- Schema / shape of each output (with units)
- Who consumes it (later phase / user-facing surface)

### Assumptions (the things that, if false, break this phase)
- e.g., "phase 2 has shipped column x on table y"
- e.g., "Stripe webhook delivery is idempotent within 24h"

### Out of scope (must NOT touch)
- File paths or modules the phase must leave alone
- Behaviors the phase must NOT change
- Teammates' owned sets (from the board's ownership map) — report needs there to the hawk, never edit
- Ledger files this phase may touch: [paths] — LOCKS.md claim required per edit

### Team block (shared worktree)
- Teammates in flight: [role → task → owned paths, one line each]
- Board: [path to BOARD.md] · Ledger: [path to LOCKS.md]
- Rules: no git add/commit (the hawk commits) · scoped tests only · blocked-on-knowledge → ask the hawk

### Advisory expert requirements (non-negotiable)
- From [Advisory expert name]: [their requirement, verbatim from plan]
- These are not suggestions. If the implementation conflicts with them, it fails AC.

### Security floor (every phase — verified at Step 5a)
- No secrets in the diff (scanned before review)
- New dependencies: real on the public registry, mature, known maintainer, pinned in the lockfile
- Input-handling changes carry an injection-class misuse test (SQL / shell / HTML / prompt, as applicable)

### Acceptance criteria (definition of done — set by orchestrator, not subagent)
[Paste the refined AC from pre-flight C here]

### E2E coverage the planner will run after this phase
[Which E2E tier the orchestrator will verify after the round — so the subagent knows not to run it]
```

## 5. Escalation format (failure protocol)

```
## Phase N — escalating to user after 2 expert loops

### What we're trying to achieve
[The AC gate that is failing, in plain language]

### What we've tried
- Loop 1: [expert dispatched, what they changed, why it still failed]
- Loop 2: [expert dispatched, what they changed, why it still failed]

### Root cause hypothesis
[Why this is harder than the plan anticipated]

### Options
- Option A: [change scope, with tradeoff]
- Option B: [add a new expert / new phase, with tradeoff]
- Option C: [accept the gap and note it as a known limitation]
```

## 6. Mid-execution trajectory check (PO rhythm)

```
## Mid-execution signal — plan trajectory check

After [N phases], the North Star is [current value] vs [expected value from plan].
This is [ahead / behind / off-axis] from the plan's prediction.

Possible reasons:
- [Hypothesis 1]
- [Hypothesis 2]

Recommendation: [continue / pause and reassess / dispatch [expert] to investigate]
```

## 7. Worked example: applying this skill to a multi-phase rollout

**Team Roster (from plan-with-review):**
- AI pipeline architect (technical) — owns `apps/api/src/pipeline/`, `generate.py`
- SEO/GEO/AEO specialist (advisory) — shapes article structure requirements, doesn't implement
- Backend engineer (technical) — owns `apps/api/src/`, migrations, `server.py`

**Round 1 (sequential — foundational):**
- Phase 1+2 atomic: backend engineer implements, AI pipeline architect's constraints loaded as advisory requirements. PO reviews against North Star + SEO requirements.

**Round 2 (parallel — contracts disjoint):**
- Phase 3 (AI pipeline architect) + Phase 5.A (backend engineer) — spawned in single message.
- PO orchestrator acceptance reviews both deliverables. SEO specialist's requirements checked against both.

**Round 3 (parallel):**
- Phase 5.B + Phase 4 — parallel.

**Round 4 (sequential — billing):**
- Phase 6.A → Phase 6.B — billing correctness gate mandatory.

After each round: planner-owned E2E, North Star trajectory check, advisory expert requirements check, board refresh.

## 8. Lock ledger — LOCKS.md

Sibling of BOARD.md; **gitignored** (runtime state, not history). Workers append a claim BEFORE touching any file outside their owned set, and strike it through on release. The hawk arbitrates conflicts and clears stale claims — workers never clear each other's.

```markdown
# LOCKS — claim before edit, release after. One holder per path.
# Stale = held past TTL with no activity → hawk arbitrates (workers never clear others' claims).

| Path | Holder (role) | Phase/task | Claimed at | TTL |
|------|---------------|------------|------------|-----|
| apps/api/src/routes/index.ts | backend-engineer | P3: register route | 2026-07-07T14:02 | 30m |
| ~~apps/api/src/config.py~~ | ~~pipeline-architect~~ | ~~P2~~ | ~~13:40~~ | released 13:55 |
```

Protocol: claim → edit → release, one file at a time; hold the claim only while actively editing. If a needed path is already claimed: tell the hawk, work on something else — never wait-spin, never edit anyway.

Stale-claim clearing: before clearing, the hawk kills or confirms-dead the holder (escalation ladder rung 2) — clearing a claim under a live worker creates a write race. A worker whose claim was revoked and who writes that file afterward is diverging: steer or kill, and note it on the board.

## 9. Agent-session postmortem (brain/55_Execution/postmortems/YYYY-MM-DD-<slug>.md)

Blameless. The unit of analysis is the harness, not the agent. **Incomplete until "Harness fix" names a change that actually landed.**

```markdown
---
type: postmortem
title: <slug>
status: current
created: <ISO date>
tags: [postmortem]
---
# Postmortem — <one-line title>

**Trigger:** what tripped — which smell tripwire / gate failure / kill decision, with the number that breached
**Timeline:** dispatch → first divergence signal → detection → containment (times or gate sequence)
**Poisoned belief:** the exact false assumption the session held ("file X was already migrated", "teammate's API returns Y")
**Propagation path:** who inherited the belief (workers, reviewers, the board?) and through which channel
**Amplifier:** what made it possible (brief gap, missing tripwire, unverified claim relayed, context rot)
**Concealer:** why it wasn't caught earlier (no scoped test, hedged reports accepted, sweep skipped)
**Root-cause class:** model | prompt/brief | tool | environment | contract | verification-gap | handoff
**Blast radius:** phases/commits/hours affected; what had to be reverted or respawned
**Harness fix (REQUIRED):** the one concrete change that prevents recurrence — skill edit / tripwire threshold / board-protocol change / new misuse test / memory entry — with a link to where it landed
```

## 10. Cross-model review runner (Step 5c)

Runner subagent: **haiku**, low-freedom brief. It runs the command and relays output verbatim — triage belongs to the hawk. The concrete command below is the reference implementation with the default cross-model reviewer (OpenAI Codex CLI); swap the command for your configured cross-model reviewer via `{{CROSS_MODEL_REVIEW_CMD}}` — the stall/timeout handling is reviewer-agnostic.

```
You are a review runner. From <worktree-path>, run exactly:

  timeout 600 codex exec review --commit <sha> -s read-only -o /tmp/codex-<sha>.md \
    "Review this commit as an independent reviewer. Goal: <phase goal>. \
     Contract: only these files should change: <owned paths>. \
     Acceptance criteria: <AC summary>. \
     Report findings with severity P0 (breaks correctness/security/data) to P3 (nit), \
     file:line for every claim. No praise, findings only."

Return the full contents of /tmp/codex-<sha>.md verbatim, plus the exit status.
If the command errors (auth, rate limit), return the error text verbatim — do not retry more than once, do not substitute your own review.
If it hits the 600s timeout or appears to wait for input (device-code login prompt), report "STALLED: <last output>" verbatim — a stall is not an error message, and you must not answer prompts on Codex's behalf.
```

Brief rules: provenance-free (no "written by", no "tests pass"); the commit SHA scopes the diff. The CLI also offers `--uncommitted` (staged + unstaged + untracked) — **never use it in a shared tree**: it would sweep teammates' WIP into the review. Committing first, then reviewing the commit, is the whole point of the ordering.

Hawk triage rubric: **P0/P1** (correctness, security, data loss, contract violation) → block, failure protocol, re-run 5c on the fix commit · **P2/P3** → board task entry, batch into the PR round · **false positive** → dismiss WITH one evidence line on the board. Rate-limit/auth failure → board note + in-family fallback reviewer for this gate + explicit flag so `copilot-review-loop` covers it at the PR.
