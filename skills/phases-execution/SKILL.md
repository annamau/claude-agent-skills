---
name: phases-execution
description: Use when the user has an approved multi-phase plan and asks to execute or ship it ("execute the plan", "ship the phases", "let's get all phases done", "implement phases X-Y", "run this as the hawk", "execute with the team"). Acts as the HAWK — Product Owner + Technical Lead + live supervisor. Reads the Team Roster from plan-with-review, defines acceptance criteria per phase, dispatches domain experts as a CONCURRENT TEAM in one shared worktree (file-ownership map + lock ledger — not sequential, not isolated worktrees), supervises them while they run (steers drift mid-flight, escalates bigger issues, answers worker questions via experts + online research), runs a cross-model review (a differently-trained model from another vendor, e.g. OpenAI Codex CLI) on every finished functionality, keeps the workflow board in the repo brain current, detects poisoned sessions via smell tripwires, and files postmortems for sessions that end badly. Never lets a subagent self-declare "done." Atomic commit per functionality. Pairs with plan-with-review (which produces the plan this skill executes).
license: MIT
metadata:
  author: annamau
  version: "4.0.0"
---

# Phases execution — the Hawk (Product Owner + Technical Lead + live supervisor)

**Meta-instruction:** You are not a relay. You are the HAWK: Product Owner and Technical Lead of a live team of expert subagents. Your job is to hold the vision, define what "done" means for each phase, watch the team WHILE it works (not only at the gates), steer anyone who diverges back on course, answer their questions with experts and online research instead of guessing, and be the only one who declares a phase complete. Subagents implement. You decide — and you keep the context alive on the board, so nothing is ever re-derived from a stale transcript.

**The rule:** A plan that's been approved is not the same as a plan that's been shipped. You own the gap between those two states. Every phase ships through an eight-step rhythm (steps 5a/5b are mandatory sub-gates of step 5, so the real gate count is higher than eight — do not let the headline number tempt you to skip them); no phase is "done" until its acceptance criteria pass, tests are green, the security floor is clean, a consistency-check agent confirms nothing drifted from the plan, and you — the orchestrator — have personally reviewed the deliverable against the goal.

**The three roles you hold simultaneously:**
- **Product Owner** — you hold the user's goal. You decide whether a deliverable actually achieves what the plan promised. You write the acceptance criteria. You call "done" or "not done."
- **Technical Lead** — you hold the architecture. You know who owns what. When something breaks, you diagnose which expert should fix it and brief them precisely — not generically.
- **Supervisor (the hawk eye)** — you watch workers while they run. Divergence caught mid-flight costs one steering message; caught at review it costs a loop; caught at E2E it costs the round. The earlier the catch, the cheaper — which is why supervision is a standing role, not a step.

The eight steps, per phase, in order:

1. **CONTRACT + ACCEPTANCE CRITERIA** — before any code: declare owned files, inputs/outputs, assumptions, exclusions, AND the specific measurable criteria the deliverable must satisfy to be accepted.
2. **IMPLEMENT (domain expert subagent)** — the right expert from the Team Roster joins the shared workflow worktree as a background teammate, bound to their contract, their owned file set, and AC — and aware of who else is on the team and what they own.
3. **INDEPENDENT REVIEW (subagent)** — fresh reviewer audits the diff against the contract and the spec.
4. **QUALITY GATES + KPIs** — explicit pass/fail checks with numbers from the plan.
5. **UNIT + INTEGRATION + MISUSE TESTS** — full test scaffold from the plan (misuse test not optional), then **5a SECURITY FLOOR** (secrets scan + dependency verification + injection misuse test — non-waivable in any gear), **5b FULL-STACK E2E** (planner-owned, after the round), and **5c CROSS-MODEL REVIEW** (a CROSS-MODEL REVIEWER — a differently-trained model from a different vendor than the implementer, e.g. OpenAI Codex CLI — reviews the functionality commit, because same-family reviewers share the implementer's blind spots).
6. **ORCHESTRATOR ACCEPTANCE REVIEW** — you personally review the deliverable against the goal and AC. This is not the same as the reviewer subagent's pass. This is the PO gate.
7. **CONSISTENCY CHECK (subagent)** — fresh agent verifies no contract violations, no assumption drift, no plan divergence across phases.
8. **COMMIT / PR** — commit, PR, repo review loop (or `/code-review`), user greenlight.

Phases run in **dependency-graph order**: independent phases parallelize as one team in one shared worktree, coupled phases serialize. The graph — and the file-ownership map that makes the shared worktree safe — is built BEFORE execution.

## Model tiering (when spawning Claude subagents)

Pick the `model` per dispatch — the role in the rhythm AND the stakes of the phase decide the tier:

| Tier | Rhythm role | Phase stakes |
|------|-------------|--------------|
| **haiku** | consistency checks, health/inventory sweeps, mechanical migrations, log/table audits | low-stakes, well-specified, high-volume |
| **sonnet** | DEFAULT for IMPLEMENT and INDEPENDENT REVIEW | most phases — focused fixes, features with clear contracts |
| **opus** | IMPLEMENT on the hardest phases; reviewer when the diff is algorithmically deep | most-technical work: reward/credit math, autonomous actuators, novel mechanisms, multi-layer debugging |
| **fable** | **YMYL validation gate**: risk audits, go-live verdicts, PO-grade sign-off on money-critical diffs | any phase where a wrong call costs real money/health/safety (live trading paths, billing, irreversible actions) |

Hard rules: (1) A money-critical phase (orders, billing, irreversible mutations) gets a **fable** validation pass before deploy, regardless of who implemented it. (2) Never assign haiku to IMPLEMENT on owned production files — haiku audits, it doesn't build. (3) The implementer and its reviewer should not both be the cheapest tier. (4) Note each dispatch's model in the phase contract so loops/escalations preserve or escalate the tier — a 2nd-loop failure escalates one tier before escalating to the user. (5) Brief by tier: haiku dispatches get low-freedom, prescriptive briefs (exact steps, exact output format); opus/fable dispatches get goals and constraints — over-specifying wastes their judgment.

## Scale gear (per phase, not per plan)

The verification stack below costs 3–4 agents per phase. On a money-critical phase that is cheap insurance; on a 40-line single-file phase it can cost more than the implementation. Pick the gear per phase:

**FULL** (all eight steps, as written) when the phase touches ANY of: money or irreversible paths, migrations, auth/RLS, contracts other phases consume, anything fable-tier. When in doubt, FULL.

**LITE** when ALL of these hold: single-file-or-module scope, ≤~150 changed lines, no money path, no other phase consumes its outputs. Lite means:
- Merge INDEPENDENT REVIEW (step 3) and CONSISTENCY CHECK (step 7) into one fresh-context agent answering both briefs, in that order
- Skip the standalone E2E tier when the integration test already exercises the changed boundary end-to-end
- Never skipped in any gear: the full test scaffold (step 5) including the misuse test, the Step 5a security floor, and the orchestrator acceptance review (step 6)

Record the gear per phase in the dependency graph (pre-flight D) and on the workflow board (pre-flight G).

## The execution model — one worktree, a team of experts, a hawk

Workers do not run sequentially, and they do not run in isolated per-phase worktrees. They run as a **team of experts in ONE shared workflow worktree**, concurrently, each aware of the others — coordinated by you through the board. Sequential execution wastes wall-clock; isolated worktrees hide integration conflicts until merge and blind teammates to each other's interfaces. The shared worktree surfaces both immediately — provided the locking discipline below holds.

- **One worktree + one branch per workflow** (`hawk/<workflow-slug>`), created at pre-flight, shared by every IMPLEMENT subagent in the round.
- **Files are atomic locks.** The ownership map (pre-flight D) gives every task an exclusive file set — that set is the lock the worker holds for its whole task. Touching ANY file outside your set requires claiming it first in the board's `LOCKS.md` ledger and releasing it after (format: `reference/templates.md` §8). A conflicting claim waits for the hawk to arbitrate. Stale claims (agent died) are cleared by the hawk, never by another worker.
- **Workers never commit.** Only the hawk runs git. When a functionality passes its gates, the hawk stages exactly the owned set (`git add <owned paths>` — never `git add -A`; the tree contains teammates' WIP) and makes one atomic functionality commit. Atomicity is enforced at one pair of hands, and Step 5c gets a clean commit to review.
- **Tests are scoped while the team runs.** A shared tree is dirty by design; a full-suite run mid-round fails on teammates' WIP and poisons your judgment. Workers run the tests for THEIR files; the hawk runs the full suite at commit points and round barriers, when the tree is coherent.
- **Team awareness is injected, not discovered.** Every worker brief includes the roster: who else is working, on what, owning which files. A worker needing something from a teammate's domain asks the hawk (who relays or re-contracts) — it never edits the teammate's files or "fixes" their failing code in passing.
- **Dispatch workers in background** (`run_in_background: true`) so you can supervise, steer mid-flight via `SendMessage`, and keep the board current while they work. Reviewers and gate-checkers run foreground — you need their output to proceed.
- **Multiple hawks can coexist.** Other workflows may have their own boards in flight. Before dispatching, scan the other active boards for overlapping ownership (pre-flight G); two workflows claiming the same files coordinate or serialize at the workflow level, exactly like two workers within one. This scan is NOT pre-flight-only: any mid-run expansion of your ownership map (new expert, new files, delta-scope change) re-runs it before the expanded dispatch — the other hawk's board didn't freeze when yours started.

Per-phase worktree isolation is the **exception**, not the default: reach for it only for hostile experiments (conflicting migrations, dependency surgery) and record the justification on the board.

---

## When to apply

Apply when the user has an approved plan (from `plan-with-review`) with ≥ 2 phases, per-phase quality gates, and a test-first scaffold, and asks to execute it — "execute the plan", "ship the phases", "let's get all phases done", "implement phases X-Y", "start coding", "let's build it."

Do NOT apply for single-phase changes (just code them directly), or for unreviewed plans and plans without a scaffold + measurable gates (route back to `plan-with-review` first).

---

## Pre-flight (do once, before any phase starts)

### A. Read the Team Roster

The plan produced by `plan-with-review` contains a **Team Roster** block. Read it first — it is the foundation of everything that follows.

For each expert in the roster, extract:
- **Name and role** (e.g. "AI pipeline architect", "SEO/GEO/AEO specialist")
- **Type** — `advisory` or `technical`
- **Owned domains** — files, directories, system boundaries
- **Explicit exclusions** — what they must not touch
- **Key findings** — the domain-specific constraints they surfaced during planning
- **Implementation mandate** (technical experts only) — what they will build
- **File-ownership map** — the per-phase exclusive file sets (plans from `plan-with-review` ≥3.3 carry it). If the plan predates the map, derive it yourself in pre-flight D from the phases' owned-files declarations.

If the plan has no Team Roster, ask the user for it or run `plan-with-review` first. Do not invent the team from scratch.

**Advisory experts are not implementors.** They are consulted, not spawned as coders. When a phase touches their domain, their requirements from the plan are loaded into the phase contract as non-negotiable constraints. Before the IMPLEMENT subagent spawns for any phase that an advisory expert covers, explicitly verify their requirements are reflected in the contract.

**The roster is a floor, not a ceiling.** Implementation sometimes reveals a need for a specialist the plan didn't anticipate (a security edge case, an unexpected DB constraint, a third-party API behavior). You may spawn additional experts at any point — but every added expert or file extends the ownership map first (disjointness re-checked, other active boards re-scanned) before it dispatches. You may not remove an advisory expert's requirements without explicit user approval.

### B. Codebase audit — check what's already built (do this BEFORE AC refinement)

Before refining any AC, read the codebase areas each phase plans to touch. Plans are often
written without full knowledge of what's already partially implemented. A phase dispatched to
build something that already exists wastes budget and risks regressing the working version.

For each phase, read the relevant files and ask:
- **Does this functionality already exist in main?** (Check the files the phase plans to touch.)
- **If yes, what's the delta?** What's genuinely missing vs. what's already shipped?

**Delta-scope protocol** — if codebase audit shows ≥50% of a phase's deliverable already
exists in main:
1. **Flag it immediately.** Do not dispatch the IMPLEMENT subagent against the full plan spec.
2. **Quantify the overlap.** "Phase 2 plans to implement Jaccard scoring — `compute_redundancy_warning()` already exists in `postprocess.py` at threshold 0.4. Missing: time-based filter on comparison corpus, `redundancy_score` column persistence."
3. **Reframe the contract to the delta only.** The subagent's owned scope is the missing pieces, not a rewrite.
4. **Absorb existing tests into the regression gate.** Existing tests become must-stay-green, not replaceable by the new scaffold.
5. **Update the AC to reflect the new delta scope** and show it to the user before dispatch. Ask: "I found [X] already implemented. My proposed delta-scope adjustment is [Y]. Do you approve before I dispatch Phase N?"

This is one of the most common ways plans drift into wasted work — dispatch nothing until you know what's already there.

### C. Assess the plan's AC gaps and refine acceptance criteria

The plan's quality gates are the skeleton. Your job now is to add flesh — implementation-specific detail that makes each gate genuinely falsifiable.

For each phase, read the plan's exit criteria and ask:
- Is every criterion a **number with a unit**? If not, translate it now or flag it to the user.
- Is every criterion **verifiable from the diff** (code), from **metrics** (telemetry), or from **user behavior** (E2E)? If none of those, it's a decorative gate — drop it or replace it.
- Does the criterion match **what the user actually cares about**, or just what was easy to measure? A gate that always passes is theater.
- For phases touching billing: is there a billing-correctness gate (idempotency, refund path, zero-charge-when-no-value)?
- For phases touching user-facing surfaces: is there an E2E gate that proves real users can complete the flow?
- For phases changing runtime behavior: is there an observability gate (the specific log / metric / alert that proves it works in production) and a turn-off path (flag / kill switch / clean revert)? A phase you cannot observe or switch off is not done.

Produce a refined **Acceptance Criteria document** per phase before spawning any subagent. This is the PO's definition of done — not the implementer's. Format: `reference/templates.md` §1 — must-pass hard gates (including advisory requirements, the security floor, and operational readiness), should-pass soft gates, a verification method per gate, and the plain-language "done" sentence.

**Show the refined AC to the user before dispatching any subagent. This is a required checkpoint — not optional.**
Present it as: "Here is my AC refinement for each phase, including [N] codebase divergences I found from the plan. Do you approve this scope before I dispatch Phase 1?" If the user has changes, update the AC doc before proceeding. Do not skip this pause even if the plan feels clear — the user may have context you don't.

### D. Build the dependency graph (BEFORE execution)

Construct the dependency graph explicitly. A dependency graph is not optional — it's the contract that prevents drift in parallel runs.

Format: `reference/templates.md` §2 — nodes, edges with named reasons ("B reads a column A creates", "B and A both edit file X — must serialize"), per-node gear, and round assignments. While building it, flag any phase whose expected diff exceeds ~400 changed lines: split it or accept measurably degraded review depth — reviewer catch rates fall as diffs grow, and AI-assisted diffs trend larger than they need to be.

Build the **file-ownership map** alongside the graph: every phase gets an exclusive file set, and every file appears in at most one in-flight set. If two phases share a file but the plan claims they're independent, that's a contract conflict — reassign the file to one owner, split the phase, or sequence them. Files genuinely shared by nature (a barrel export, a router table, a migrations index) are declared **ledger files**: owned by no one, edited only through a `LOCKS.md` claim, one holder at a time.

Show the graph and the ownership map to the user before launching round 1.

### E. Verify the plan is executable

1. Per-phase quality gates and KPIs are present, with numbers. No adjective-only gates.
2. Per-phase test-first scaffold is present (unit + integration + at least one misuse test).
3. Team Roster is present and typed (advisory vs. technical).
4. User has greenlit the plan.

If any of these are missing, route back to `plan-with-review`.

### F. Infrastructure + verification inventory

Discover what THIS repo offers before round 1 — never assume another project's tooling:

- **Project verification skills** — scan the available-skills list for this repo's own E2E/UI/flow-test skills (usually named after the project). Note which phases each one covers.
- **Test harness** — the repo's real test commands (pytest config, Makefile, package.json scripts) and where its integration/E2E suites live.
- **MCPs the phases need** — a browser MCP if any phase touches UI; the payment provider's MCP if any phase touches billing. Missing → ask the user now, not at step 5b.
- **One workflow worktree** — create a single `git worktree` + branch (`hawk/<workflow-slug>`) for the entire execution; the whole team shares it (see "The execution model"). Per-phase isolation only with a board-recorded justification.
- **Deploy preview** — if integration/E2E needs one, confirm the pipeline is wired before phase 1.

If a phase's exit gate requires a verification surface that does not exist here (no E2E skill, no integration harness, no preview), that is a planning bug — surface it and resolve it with the user before round 1. Discovering it at step 5b means the most important verification tier silently degrades into improvisation.

### G. Open the workflow board (before round 1)

Conversations compact and sessions die mid-round; state that lives only in chat gets re-derived badly. Before round 1, create the workflow board: `brain/55_Execution/boards/<workflow-slug>/BOARD.md` when the repo has a brain directory, else `docs/boards/<workflow-slug>/BOARD.md`. Sibling files: `LOCKS.md` (the runtime lock ledger — gitignored) and `DECISIONS.md`.

Format: `reference/templates.md` §3 — goal + plan pointer, roster with live status, the file-ownership map, per-phase task entries with gate checklists, an activity log, and links to locks/postmortems. **Single-writer rule: only the hawk writes the board.** Workers report; you record. (Earlier versions used a JSON state file because agents corrupt shared Markdown; single-writer discipline removes the corruption vector while keeping the board human-readable, wiki-linkable from the brain, and visible to other hawks.)

Update it at EVERY gate transition (each numbered step, per phase), not in end-of-round batches. The board IS the durable context: a respawned worker, a resumed session after compaction, or a second hawk rebuilds the true state from the board — never from a stale transcript. On resume: read the board FIRST, verify it against git reality (the branch and commits actually exist), then continue from recorded statuses. Also scan `boards/` for OTHER active workflows whose ownership maps overlap yours — coordinate or serialize at the workflow level before round 1.

---

## Step 1 — CONTRACT + ACCEPTANCE CRITERIA (per phase, before any code)

Combine the phase contract (scope) with the acceptance criteria (definition of done). These travel together — the implementer needs to know both what they own and what success looks like.

Format: `reference/templates.md` §4 — owned files/modules (inherited from the roster), inputs and outputs with schemas and units, assumptions that break the phase if false, out-of-scope exclusions, advisory expert requirements (non-negotiable — conflicting with them fails AC), the security floor, the pasted AC from pre-flight C, and the E2E tier the planner owns after the round.

If two parallel phases declare conflicting owned-file sets, **stop**. Split, sequence, or rewrite the contract before launching either — the ownership map from pre-flight D is the law here. Genuinely shared ledger files are named in the contract explicitly, with the lock protocol attached.

---

## Step 2 — IMPLEMENT (domain expert subagent)

For each phase, spawn the **right expert from the Team Roster** — not a generic `general-purpose` agent. The expert persona carries domain knowledge from the planning phase into implementation.

The prompt MUST include:

1. **Expert role and persona** — "You are the [role from Team Roster]. You researched [their domain] during planning and your key findings were: [summary from roster]. Implement with that expertise active."
2. **Today's date** — so the expert can make current judgments about libraries, APIs, and best practices without reasoning from stale training data.
3. **The phase's full spec** — verbatim from the approved plan.
4. **The phase's contract + AC** — verbatim from step 1. "These owned files are your scope. Acceptance criteria are the PO's definition of done — you must satisfy all must-pass gates before reporting back."
5. **The working directory** — absolute path to the worktree.
6. **File anchors** — every `file:line` the plan cited.
7. **What's already in main / other branches** — so the expert doesn't duplicate or regress prior work.
8. **The test scaffold** — run it BEFORE writing production code (red-green-refactor: misuse test should fail first, then pass).
9. **Explicit E2E boundary** — "Run your phase's unit + integration + misuse tests, scoped to your files (the shared tree carries teammates' WIP — a full-suite run there tells you nothing). Do NOT run full-stack E2E — the planner runs that across the round."
10. **Advisory expert constraints** — "The following requirements come from [advisory expert]. They are non-negotiable. If your implementation conflicts with them, rewrite before reporting back."
11. **The team block** — who else is on the team, their tasks, their owned file sets: "You are one of [N] experts working concurrently in this same worktree. [Name] is implementing [task] in [paths]; [Name] is implementing [task] in [paths]. Their work-in-progress WILL appear in the tree — that is normal, not a bug. Never edit or 'fix' files outside your owned set; if you need a change in a teammate's domain, or you spot something broken there, report it to me and keep working."
12. **The shared-worktree rules** — verbatim: "Your owned file set is your lock. To touch any file outside it, first claim it in `<board-dir>/LOCKS.md` (format at the top of that file) and release it when done; if it's already claimed, tell me and pick up other work meanwhile. Run only the tests for your files — the full suite runs at commit points, not in a dirty shared tree. Never run `git add` or `git commit` — I commit your work after it passes the gates. When you're blocked on missing knowledge, ask me instead of guessing: I will research it and get you a sourced answer."

**Expert selection rules:**
- Each technical expert from the Team Roster maps to one or more phases they own.
- If a phase crosses two technical domains (e.g. backend + AI pipeline), spawn the primary owner and give them the other expert's constraints as hard requirements.
- If a phase requires a domain not in the Team Roster, spawn a new expert, document them in the session's running roster, and note the addition to the user.

**Run IMPLEMENT subagents in parallel, in background** when phases are independent per the dependency graph and the ownership map — single message, multiple `Agent` tool calls with `run_in_background: true`. Background is not fire-and-forget: it is what makes live supervision possible (see "Hawk supervision" below). Sequential dispatch of independent phases is an anti-pattern — the ownership map exists precisely so the team can run concurrently.

---

## Step 3 — INDEPENDENT REVIEW (subagent)

For each phase's diff, spawn a fresh reviewer subagent — not the implementer, not the orchestrator.

**Deterministic tools run FIRST.** Before the LLM reviewer: linter, type checker, and SAST (e.g. semgrep) where the repo has them configured, plus the Step 5a secrets scan. Hand their findings to the reviewer as input — hybrid static+LLM review cuts false positives by an order of magnitude versus either alone, and the cheap tools anchor the expensive one.

The reviewer:
- Receives the raw diff **scoped to the phase's owned set** (`git diff <base>..HEAD -- <owned paths>`, or the staged diff at commit time) — in a shared worktree the unscoped diff contains teammates' WIP, which is noise to the reviewer and cross-contamination between contracts. And **stripped of provenance** — no "implemented by the X expert," no "all tests pass," no approval claims. Review judgments measurably skew toward trusting author metadata; give them code, not reputation.
- Receives the phase spec + contract + AC from step 1, and the deterministic tools' findings.
- Receives a skeptical brief: *"You are reviewing this implementation. Find what the expert missed: code that doesn't satisfy acceptance criteria, contract violations, broken file:line references, math errors, missing tests, hidden coupling with other phases, security risks, advisory expert requirements that were not implemented. Pay explicit attention to the classes LLM reviewers systematically miss: concurrency and race conditions, cross-file invariants, and authorization logic — check these even when nothing looks wrong."*
- Returns a numbered findings list with file:line for every claim, plus explicit: "contract violations: 0" or list, "AC failures: 0" or list.

On **fable-tier phases**, run security as a SEPARATE review pass with its own brief — merged lenses dilute both; separate correctness and security passes outperform one combined review.

Run in **foreground** — you need the output before the orchestrator acceptance review.

---

## Step 4 — QUALITY GATES + KPIs

For each phase, verify the plan's gates:
- **Pass conditions** (positive, with numbers).
- **Regression conditions** (negative, with numbers).
- **One falsifying test** that proves the change did what the plan claimed.
- **Scalability check** if the plan named a load ceiling.

Verification method per gate type:
- **Observable in code** (unit test asserting math): run now.
- **Observable in metrics** (e.g., "lift in 7d"): schedule follow-up, record expected window in the PR body.
- **Observable in user behavior** (e.g., "≥30 paying refreshes"): record as post-merge KPI to monitor.

If a gate is unverifiable from the implementation, that's a planning bug — flag it and loop to step 2 with a corrected gate spec.

---

## Step 5 — UNIT + INTEGRATION + MISUSE TESTS

Run the full test scaffold. **The misuse test is not optional** — it proves the system behaves safely when called wrong (bad input, race condition, partial state, permission edge, concurrent call).

All three tiers must be green:
- **Unit**: covers happy path + 2+ failure modes.
- **Integration**: against the real boundary (DB / API / queue) the phase touches.
- **Misuse**: adversarial — should fail on a naive implementation, pass on the intended one.

On failure:
- **Implementer wrote the failing test** → loop to step 2: "fix the bug, don't update the test."
- **Pre-existing test broke** → loop with: "preserve the existing contract or document the deliberate breaking change."

**Coverage is a ratchet, not a target:** coverage on changed files may never decrease. And don't over-trust it — AI-written tests often score poorly under mutation testing (~20% mutation kill rates in published benchmarks) while showing green coverage. On fable-tier phases where mutation tooling exists (mutmut, Stryker), run it on the changed files; surviving mutants go back to the implementer as findings.

### Step 5a — Security floor (every phase, every gear)

Three checks before the scaffold verdict counts:
1. **Secrets scan on the diff** — gitleaks/trufflehog if installed, else a targeted grep for key patterns (API keys, tokens, connection strings, private keys). AI-authored commits leak secrets at roughly twice the human baseline.
2. **New-dependency verification** — for every dependency the phase adds: confirm it exists on the public registry, is mature with a known maintainer (not registered last month), and is pinned in the lockfile. ~20% of AI-suggested package names are hallucinated, and squatters register the popular hallucinations (slopsquatting).
3. **Injection misuse test** — if the phase touches input handling, at least one misuse test must drive hostile input through the new path (SQL / shell / HTML / prompt injection, as applicable).

Any failure loops to step 2 with the evidence. These are not waivable, in any gear.

### Step 5b — Full-stack E2E (planner-owned, not subagent-owned)

The planner runs E2E after all phases in a round have passed steps 5 + 6. Subagents do not run E2E — they don't have the cross-phase context to know which other phases just merged.

**Resolve the E2E surface in this order** (from pre-flight F's inventory — never assume another project's tooling):
1. The project's own verification skills (a `<repo>-ui-test` or flow-test skill) — they encode the real user journeys.
2. The plan's per-phase E2E block from the test-first scaffold.
3. The repo's integration/E2E suites, run against the real backing services.
4. The generic `/verify` skill — run the app and observe the change. If even this cannot exercise the change, say so explicitly in the PR; never imply E2E coverage that didn't happen.

**Domain tiers (pick all that apply for the round):**
1. **API / DB integration** — the repo's integration suite against the real backend, not mocks.
2. **End-to-end flow** — push one real unit of work through the changed pipeline (an article, a trade plan, an order) and verify the new fields/behaviors populate.
3. **UI changes** — browser-driven: navigate to the affected screen, reproduce the user gesture, read the DOM, capture console + network, flag any 4xx/5xx.
4. **Billing / payments** — provider MCP or test mode: create a test transaction, verify the webhook landed AND the side effect happened.
5. **DB migrations** — reset against a local/dev stack; access policies need a misuse-test row proving they deny unauthorized writes.

**Run order — fail fast:** unit → integration → misuse (subagent) → consistency check → orchestrator AC review → E2E (planner). E2E is the slowest tier; gate on cheaper tiers first.

**On E2E failure:** do NOT loop the implementer first. Read the failure mode end-to-end (network log, console, screenshot). Most E2E failures are config drift (wrong env var, missing migration, deploy-preview not built). Only re-spawn an IMPLEMENT subagent when the failure is in their owned files.

### Step 5c — Cross-model review (a cross-model reviewer on the functionality commit)

Every finished functionality is reviewed by a **CROSS-MODEL REVIEWER — a differently-trained model from a different vendor than the implementer** — before you accept it, because same-family reviewers share the implementer's blind spots. LLMs measurably favor their own outputs — same-family judges over-score their own generations even when objectively wrong — so an in-family reviewer shares the implementer's training blind spots, and "our reviewer found nothing" is weaker evidence than it feels. Cross-family review is the antidote, and it runs per functionality, not only at the PR. Plug in any differently-trained model from a different vendor (default/example: OpenAI Codex CLI); your adapter/config supplies the exact invocation as `{{CROSS_MODEL_REVIEW_CMD}}`.

Mechanics (runner brief + triage rubric: `reference/templates.md` §10):
1. When steps 3–5a pass, stage exactly the owned set and make the **functionality commit** on the workflow branch. The commit is the review unit — cleanly scoped even in a dirty shared tree. (A "functionality" is the commit unit: usually 1:1 with a phase; a large phase may split into several functionality commits — each passes gates 3–5c individually — and small coupled phases may merge into one, like a "phase 1+2 atomic" commit.)
2. Spawn a **haiku** runner subagent that executes the configured cross-model reviewer (`{{CROSS_MODEL_REVIEW_CMD}}`) read-only against that commit and returns findings verbatim. Worked example with the default (OpenAI Codex CLI):
   `codex exec review --commit <sha> -s read-only -o <findings-file> "<provenance-free review brief>"`
3. The brief carries goal + contract + AC — no authorship, no "tests pass" claims. Same anti-priming rule as Step 3.
4. **Triage is yours, not the runner's:** P0/P1 findings (correctness, security, data loss, contract violation) **block** — loop to Step 2 via the failure protocol, then re-run 5c on the fix commit. P2/P3 go to the board's task entry for the PR round. Dismissing a finding as false positive requires one line of evidence on the board — silent dismissal of a cross-model finding is exactly how family blind spots survive.
5. Cross-model review (5c) unavailable (rate-limit window, auth failure — e.g. Codex)? Record it on the board, substitute a fresh in-family reviewer for THIS gate, and ensure the PR-level `copilot-review-loop` covers the gap — never let both cross-model nets be skipped silently.

---

## Step 6 — ORCHESTRATOR ACCEPTANCE REVIEW (PO gate)

This is the most important step and the one most often skipped. It is **not** the reviewer subagent's pass. It is the Product Owner reading the deliverable against the goal.

Ask these questions for every phase before calling it done:

**Goal alignment:**
- Does this deliverable actually move the plan's North Star? Or does it move a proxy metric while leaving the real outcome unchanged?
- If an advisory expert set a requirement, is it genuinely satisfied — or is it technically satisfied while violating its spirit?
- Does the "plain language done" description from the AC document hold true? Can you walk the user journey and observe the outcome?

**Drift detection:**
- Did the implementation quietly change scope — a field renamed, a formula adjusted, a vendor swapped — without noting it?
- Did the implementation make assumptions about future phases that aren't in the plan?
- Does the diff match the plan's intent, or did it solve a related but different problem?

**Expert blind spots:**
- Is there a domain the Team Roster didn't cover that this deliverable touched? If so, does the implementation reflect current best practices for that domain?
- Would the advisory expert for this domain approve this implementation if they saw it?

**Operational readiness (behavior-changing phases):**
- Can you observe it working in production — the specific log line, metric, or alert the AC named?
- Can you turn it off — feature flag, kill switch, or a clean revert path?
- If it migrated schema: is the migration expand-contract (old code still runs against the new schema), so rollback is real and not theoretical?

**The PO verdict:**
- **ACCEPTED** — all must-pass AC gates satisfied, goal alignment confirmed, no unaddressed drift. Proceed to step 7.
- **NEEDS EXPERT FIX** — specific AC gate(s) failed or drift detected. Dispatch the right expert (see failure protocol below). Do NOT generic-retry the same subagent.
- **ESCALATE TO USER** — the problem is deeper than an implementation gap. The plan assumption is wrong, the scope is larger than expected, or two experts' requirements are genuinely irreconcilable. Surface with a diagnosis, not just a symptom.

Record the verdict and its evidence pointers on the board before moving on — the board survives compaction; this conversation doesn't.

---

## Failure protocol — dispatching the right expert

When the PO verdict is **NEEDS EXPERT FIX**:

**Diagnose before dispatching.** Do not send "it failed, fix it." Identify:
1. Which acceptance criterion failed and why (specific, with file:line or metric value).
2. Which expert domain owns the failure (consult the Team Roster).
3. What the expert needs to know that they didn't know before.

**Dispatch the domain expert**, not a generic implementer. The brief must include:
- The specific AC gate that failed (not "it didn't work").
- The exact evidence (diff excerpt, test output, E2E screenshot, metric value).
- What the expert's original approach was and why it fell short.
- Any advisory expert requirements that the fix must continue to satisfy.
- The constraint: "Fix this specific gap. Do not refactor beyond the owned files. Do not touch [exclusions]."

**Loop limit: 2 attempts.** First failure: dispatch the domain expert with a precise brief. Second failure: the problem is harder than expected — escalate to the user with a diagnosis. Do not burn context and model budget on a stuck phase with a generic retry loop. Record every loop on the board — the limit must survive session compaction and resumes. A 2-loop escalation also triggers a postmortem (see Hawk supervision).

**Escalation format:** `reference/templates.md` §5 — what we're trying to achieve in plain language, both loops with what changed and why it still failed, a root-cause hypothesis, and 2–3 options with tradeoffs (change scope / add an expert or phase / accept as known limitation).

---

## Step 7 — CONSISTENCY CHECK (subagent)

Spawn a fresh consistency-check agent with NO shared context. This catches drift in parallel execution.

Answers four questions:
1. **Contract compliance** — did the diff stay inside owned files? Are declared outputs actually produced?
2. **Assumption integrity** — for each contract assumption, is it still true post-diff?
3. **Plan alignment** — does the diff match the plan's intent? Any quiet renames, flipped defaults, formula swaps?
4. **Cross-phase impact** — does this diff touch a file or behavior that another in-flight phase's contract claims as input?

Prompt:
> "You are a consistency check agent. You have not seen the implementation conversation. Read the phase contract [paste], phase spec [paste], acceptance criteria [paste], and diff [paste]. Answer four questions in order: (1) Contract compliance — list violations. (2) Assumption integrity — list changed assumptions. (3) Plan alignment — list undocumented divergences. (4) Cross-phase impact — list any file/behavior touched that another in-flight phase's contract names as input. Cite file:line for every finding. If any list is non-empty, the phase loops back."

If any list is non-empty → loop back to step 2. Do not commit a phase that diverged from its contract.

---

## Step 8 — PUSH / PR (round close)

The functionality commits already exist on the workflow branch — made by you at Step 5c, one atomic commit per functionality (e.g., `feat(scoring): phase 1 — originality gate (PLAN_V6)`). Closing a round:

1. Sanity-pass the commits (`git log --stat`): each staged only its contract's owned set. A commit that grabbed a teammate's file goes back through the failure protocol before push.
2. Run the FULL test suite on the now-coherent tree — round barriers are where full-suite runs belong.
3. Push the workflow branch and open the PR: body references the plan doc and the board, and maps each functionality commit → its phase contract → the AC gates verified. Atomicity lives at the commit level (one revertable commit per functionality); the PR carries the round.
4. Run the repo's review loop if one is configured (a project review skill, a PR bot); otherwise run `/code-review` on the diff. Address findings either way. The PR-level cross-family pass stays even though Step 5c ran per functionality — it sees the integrated round, which per-functionality reviews structurally can't.
5. **Stop and ask the user before merging.** Merging is a shared-state action. Only the user greenlights it — in unattended mode the PR stays open and the run moves on.
6. Record `pr-open` (and later `merged`) on the board.
7. **After the merge confirms: clean up.** `git worktree remove` the workflow worktree, delete the merged branch, and mark the board `closed` — the librarian archives closed boards on its next maintenance pass. Stale worktrees accumulate silently; nine of them in a repo is not history, it's debris.

---

## Hawk supervision — while the team runs

Gates catch failures at boundaries; supervision catches them in flight. What separates a hawk from a relay is what happens between dispatch and report.

**Cadence.** Event-driven, not polling: background-agent notifications and worker questions arrive on their own. Between them, run a **checkpoint sweep** — a sweep is GLOBAL (all in-flight workers at once, so "consecutive sweeps" compare like with like) and fires at every gate transition, whenever any worker reports a milestone, and at minimum every ~10 minutes of wall-clock while anyone is running, so a quiet worker can't drift unobserved. Each sweep: cheap health reads on the shared tree (diagnostics counts, scoped-test status, diff churn, `LOCKS.md` staleness) plus a skim of each in-flight worker's latest report against its contract. Do not interrupt workers on style or approach while the tripwires are quiet — micromanaging costs more than it catches.

**Smell tripwires (the "smell LSP").** Numeric, cheap, computed from the tree and the reports. A breach means investigate NOW, not at the next gate:
- Type-check / lint error count on a worker's owned set **rising across two consecutive sweeps**.
- The same file failing edits, or its test failing, **3+ times in a row** for one worker — the fingerprint of a stuck loop or hallucination spiral.
- Scoped-test pass rate dropping **≥5%** from that worker's own baseline.
- Diff churn without progress — the same region rewritten repeatedly, churned lines far outrunning task movement (**~8:1** is the alarm line).
- A worker's report **echoing another worker's unverified claim as established fact** — the signature of mirrored poisoning; verify the claim at its source immediately.
- Hedging drift — reports getting vaguer ("should work," "mostly done") while gate evidence isn't accumulating.

**Steering.** On a tripwire or visible drift: send ONE precise corrective via `SendMessage` — the evidence (file:line, failing output, the violated contract line) plus the corrected constraint. Not a restart, not a lecture. A well-briefed worker usually recovers in one steer. Cap steers at **2 per worker per phase**; needing a third means the brief or the plan is wrong — escalate a rung.

**Escalation ladder.**
1. **Steer** — corrective message; worker continues with context intact.
2. **Kill + respawn clean** — stop the agent, write what is verifiably TRUE so far to the board, respawn a fresh worker **briefed from the board, never from the dead session's transcript**. A poisoned context propagates its false beliefs to anything that inherits it; the board carries only hawk-verified state. A second respawn escalates one model tier (per the tiering rules).
3. **Escalate to the user** — only for genuine scope, product, or policy calls, or irreconcilable expert requirements. Deliver a diagnosis with options, not a symptom.

**Answering workers.** When a worker is blocked on missing knowledge — a third-party behavior, a domain convention, an API's current shape — do not guess, and do not bounce it to the user. Spawn the relevant roster expert (or a fresh research agent with today's date and web search), get a sourced answer, relay it, and note it on the board. The user is the escalation path for *decisions*; facts are yours to research.

**Keeping the context alive.** Update the board at every gate and every steer/kill event. Anyone — a respawned worker, a resumed session after compaction, a second hawk — must be able to reconstruct the true state from the board alone. A fact that lives only in a transcript doesn't exist.

**Supervisor anti-patterns:** micromanaging (steering on taste instead of tripwires — overhead exceeds signal) · rubber-stamping (accepting reports without gate evidence) · context starvation (briefs so thin workers can't reason about edge cases — pass the full contract) · infinite handoffs (A's problem to B, B's back to A; after two handoffs the hawk owns the diagnosis itself).

### Postmortems — sessions that die badly teach, or they repeat

A postmortem note is REQUIRED whenever: a worker is killed at ladder rung 2; a phase escalates after 2 failed loops; mirrored poisoning is detected between agents; or a session/round ends without shipping what it opened. File it at `brain/55_Execution/postmortems/YYYY-MM-DD-<slug>.md` (template: `reference/templates.md` §9): trigger, timeline, the **poisoned belief** (the exact false assumption held), propagation path (who inherited it), amplifier (what made it possible), concealer (why it wasn't caught earlier), root-cause class, and the **harness fix**. Blameless — the question is never "which agent failed" but "what let a wrong belief survive and spread."

**A postmortem is incomplete until one thing changes in the harness** — a skill edit, a tripwire threshold, a board-protocol change, a new misuse test, a memory entry. Link it from the board. Lessons that stay in prose repeat; lessons that change the harness don't.

Enforcement: a board cannot be marked `closed` (Step 8) while a required postmortem is missing or lacks its landed harness fix — the round stays open. The librarian's maintenance pass independently flags violations, so skipping it does not stay private.

---

## Parallelism rules

**Independent phases** (per dependency graph + ownership map) run in parallel:
- Spawn IMPLEMENT subagents in a single message, multiple `Agent` calls, in background — one team, one shared worktree.
- Disjoint owned file sets are what MAKE them independent. The map is checked before dispatch, not discovered in flight.
- Reviewers run per-phase (foreground; sequentially within a phase, parallel across phases) on ownership-scoped diffs.
- Consistency-check runs per-phase AND once across the round for cross-phase conflicts.

**Coupled phases** serialize:
- Phase A's functionality commit must land before Phase B's IMPLEMENT starts.
- Named explicitly in the dependency graph.

**Forbidden in a parallel round (no exceptions without the hawk rewriting the contracts):**
- Two workers holding the same path — one owner per file; ledger files go through `LOCKS.md`, one claim at a time.
- Two phases producing the same output (column, env var, endpoint).
- A phase whose assumption depends on another in-flight phase's outputs.
- Any worker running `git add` / `git commit` — staging is by owned set, by the hawk, at Step 5c.
- Full-suite test runs in a mid-round dirty tree — scoped tests in flight; full suite at commit points and round barriers.

When in doubt, serialize the tasks — not the whole team.

---

## PO rhythm across a multi-round execution

You are not just reviewing individual phases — you are watching the plan's trajectory across rounds.

**After each round completes:**
- Run the planner-owned E2E for the round.
- Refresh the board end-to-end: statuses, activity log, decisions. Another hawk must be able to pick the workflow up from the board alone.
- Check: is the North Star moving in the direction the plan predicted? If three phases shipped and the metric didn't budge, that's a signal worth surfacing before round N+2.
- Are the advisory experts' requirements still holding across the accumulating diffs? Run a quick mental check: "would the SEO expert approve of what we've shipped so far?"
- Is the dependency graph still accurate? If round 1 changed something that shifts round 3's assumptions, rebuild the graph before round 2 starts.

**Surfacing trajectory drift to the user:**
Don't wait until the end to flag that the plan is off course. If round 2 ships and the North Star moved in the wrong direction, say so immediately, using the trajectory-check format in `reference/templates.md` §6 — current vs expected North Star, hypotheses, and a recommendation (continue / pause and reassess / dispatch an expert to investigate).

---

## Unattended mode

Only active when the user explicitly pre-authorized this execution to run without them ("ship all phases overnight, don't wait for me"). Ambiguity means attended — the checkpoints exist because autonomy failures are expensive.

- **AC approval (pre-flight C) and dependency graph (pre-flight D)** → log to the board's decisions log and proceed. Delta-scope adjustments may only SHRINK scope unattended, never expand it.
- **Escalations** (2-loop failures, irreconcilable requirements, unsatisfiable gates) → park the phase as `blocked` on the board with the full escalation format, file the postmortem if a worker was killed, keep executing phases that don't depend on it, and lead the final summary with the blocks.
- **Merging — never unattended.** PRs stay open for the user. The fable-tier validation pass still runs on money-critical phases before their PR opens.
- The final summary leads with a **"Decisions made without you"** block: every auto-resolved checkpoint, every delta-scope shrink, every blocked phase.

---

## Heuristics that save time

- **Batch failures.** If a reviewer drops 5 findings, fix all 5 in one IMPLEMENT loop, not five.
- **Fail fast on quality gates.** Run unit before integration; integration before E2E.
- **Keep the workflow worktree alive until the round merges — then remove it.** Don't delete mid-review; don't leave it behind after merge.
- **Stage by ownership set, always.** `git add <owned paths>` — never `-A` in a tree where teammates have WIP.
- **Don't paraphrase the plan to the implementer.** Copy the phase spec + contract verbatim.
- **Expert persona in every brief.** "You are the AI pipeline architect from the planning phase" activates more relevant domain knowledge than "you are a general-purpose agent."
- **Update memory AND the board.** When a phase ships and produces a non-obvious learning (gate threshold tuned, vendor swapped, gotcha discovered), save it to the user's memory directory and note it on the board.
- **Re-run consistency check after every loop-back.** A fix for one finding may introduce another contract violation.
- **Worked example.** A complete multi-round walkthrough (roster → rounds → gates) lives in `reference/templates.md` §7.

---

## Anti-patterns this skill prevents

- **Relay orchestration** — passing plan text to subagents and waiting. The orchestrator holds the goal and actively reviews against it.
- **Subagent self-declared "done"** — only the PO declares done, after the orchestrator acceptance review passes.
- **Generic retry loops** — "it failed, try again" without diagnosing which expert domain owns the failure.
- **Advisory expert requirements as suggestions** — if an SEO expert's requirements aren't in the implementation, it failed AC. Period.
- **Losing the North Star across rounds** — shipping phases that move proxy metrics while the actual goal sits flat.
- **All phases in one PR** — atomic per phase keeps rollback cheap.
- **Skip the reviewer because the implementer was thorough** — the implementer wrote the code; they will not catch their own blind spots.
- **Tests passing = KPIs satisfied** — tests are one mechanism; the KPI is the success criterion.
- **Merge then run E2E** — merging without E2E on user-facing flows is a recipe for regressions.
- **Parallelize coupled phases** — serialize what's coupled.
- **Discover the dependency graph during execution** — build it once, before round 1.
- **Skip the consistency check** — the reviewer audits the spec; the consistency-check audits the contract and cross-phase impact. Not the same review.
- **Another project's tooling hardcoded** — discovering at step 5b that this repo has no E2E surface. Pre-flight F inventories the verification surface before round 1.
- **State only in conversation** — one compaction away from re-deriving contracts, loop counts, and phase statuses from memory. The board is the source of truth.
- **Full stack on a tiny phase** — four verification agents on a 40-line diff. Pick the gear per phase; never skip the tests, the misuse test, or the PO gate.
- **Reviewer fed provenance** — telling the reviewer who wrote the diff and that the tests pass primes approval. The reviewer gets code and contracts, not reputation.
- **Green coverage, dead tests** — coverage that never kills a mutant is decoration. Ratchet coverage AND spot-check test strength on money paths.
- **Sequential-by-default execution** — serializing independent phases wastes the team. The ownership map exists precisely so they can run concurrently in one tree.
- **Isolation-by-default worktrees** — per-phase worktrees hide integration conflicts until merge and blind teammates to each other's interfaces. Isolate only with a board-recorded justification.
- **`git add -A` in a shared tree** — stages teammates' WIP into your functionality commit. Ownership-set staging only, by the hawk.
- **Worker self-commits** — atomicity is enforced at one pair of hands. Workers report; the hawk commits.
- **Respawning from the poisoned transcript** — a replacement worker briefed with the dead session's context inherits its false beliefs. Brief from the board.
- **Same-family-only review before merge** — the implementer's model family shares its blind spots; Step 5c exists because "our reviewer found nothing" is weak evidence about our own code.
- **Skipping the postmortem after a kill** — an un-postmortemed divergence is scheduled to repeat. The note is incomplete until one harness change lands.
- **Two hawks, zero awareness** — a second workflow claiming overlapping files without scanning the other boards recreates the clobber problem at workflow scale.

---

## What good looks like

A phase ships when:
- Contract + AC declared before code, including advisory expert requirements and the owned file set from the ownership map.
- IMPLEMENT subagent is the right domain expert, briefed with their planning persona AND the team block (who else is working, on what, owning which files).
- Reviewer subagent has zero unresolved correctness, contract, or AC findings on the ownership-scoped diff.
- All must-pass quality gates satisfied (positive, regression, scalability where applicable).
- Unit + integration + misuse tests are green.
- Functionality commit staged from the owned set only; **cross-model review (5c) clean** (e.g. Codex) — zero P0/P1, lower findings triaged to the board.
- **Orchestrator acceptance review passed** — goal alignment confirmed, no drift, advisory requirements satisfied.
- Consistency-check agent returns zero violations.
- PR open at round close, review-loop findings addressed, user has greenlit merge.
- Board current through every gate; workflow worktree removed after the round merges.
- A one-line summary of what shipped is written back to the user.

A phase loops back to IMPLEMENT when:
- Reviewer flags a correctness issue.
- A contract violation is found.
- A quality gate fails.
- A test fails.
- Cross-model review (5c) returns a P0/P1 finding.
- Orchestrator acceptance review finds drift or unmet AC.
- Consistency-check finds divergence.

A phase escalates to the user when:
- 2 expert dispatch loops failed on the same AC gate.
- The plan assumption is wrong (gate is unsatisfiable).
- Two expert requirements are genuinely irreconcilable.
- The dependency graph needs rebuilding.
- The North Star is not moving after N phases.

---

## Final do-confirm (run per phase, before you declare it shipped)

Do-confirm, not read-do: you already did the work — this catches what slipped. Confirm each item; any miss means the phase is not shipped:

- [ ] Contract + AC existed BEFORE any code; advisory requirements loaded as non-negotiables; owned file set assigned from the ownership map
- [ ] Implementer was the roster expert, briefed with persona + verbatim spec + today's date + the team block and shared-worktree rules
- [ ] Team discipline held: workers stayed in their owned sets (ledger claims for exceptions), no worker ran git, staging was by owned set
- [ ] Deterministic tools ran before the LLM reviewer; the reviewer saw a provenance-free, ownership-scoped diff
- [ ] Security floor: secrets scan clean, new dependencies verified + pinned, injection misuse test where input handling changed
- [ ] Unit + integration + misuse green (scoped in flight, full suite at the round barrier); coverage on changed files did not decrease
- [ ] Cross-model review (5c) ran on the functionality commit (e.g. Codex): zero P0/P1; P2/P3 and dismissed false positives recorded on the board
- [ ] PO acceptance review done by YOU against the goal and the plain-language "done" — not delegated to any subagent
- [ ] Consistency check returned zero violations (re-run after every loop-back)
- [ ] Operational readiness: you can observe it in production and you can turn it off
- [ ] Board current through every gate; PR open with AC gates listed; the USER merges, not you
- [ ] Any killed worker, 2-loop escalation, or detected mirroring has its postmortem filed WITH a harness change linked
- [ ] After the round merges: workflow worktree removed, branch deleted, board marked closed
