---
name: phase-based-refactor
description: Use when the user asks to do a non-trivial refactor, architectural rewrite, or multi-phase system overhaul. Enforces the IMPLEMENT → TEST → PRODUCT-THINK → INDEPENDENTLY VERIFY → SHIP rhythm for each phase. Prevents the "pile more patches on" trap by forcing an honest patch-or-real-solution assessment between phases and spinning up a fresh subagent to verify each phase's changes before committing.
license: MIT
metadata:
  author: annamau
  version: "1.0.0"
---

# Phase-based refactor

**The rule:** Every phase of a multi-phase refactor goes through the same 5-step gate before the next phase starts. No skipping steps. No "I'll verify later."

The five steps per phase, in order:

1. **IMPLEMENT** — write the code for ONE phase's scope.
2. **TEST** — run the full test suite + phase-specific canary/round-trip/smoke test. Must be green.
3. **PRODUCT-THINK** — write an honest "patch or real solution?" analysis. Quote the diff, name the concrete behaviour changes, name the weaknesses, name what's deferred.
4. **VERIFY** — spawn an independent subagent with no shared context to audit this phase's changes against the stated goals. The subagent reports RESOLVED / PARTIALLY RESOLVED / DEFERRED / REGRESSED for each phase goal.
5. **SHIP** — only after all four above are green. Commit with a message that names the phase, push, and note the phase boundary in the todo list so the NEXT phase starts clean.

This rhythm is slower per phase than "write, commit, move on." That's the point. Long refactors compound bugs silently when you skip product-think + independent verification; slowing the cadence surfaces them while they're still cheap to fix.

## When to apply

Trigger this skill when:

- The user asks for a structural refactor, architectural rewrite, or multi-phase plan (e.g. "let's do a real solution not another patch", "clean sheet rewrite", "phase A / phase B / phase C", "let's restructure X").
- The user has a roadmap doc with 3+ phases they want to execute sequentially.
- The user explicitly invokes this pattern ("do it phase by phase with testing in between").
- You yourself draft a plan with labeled phases and need discipline on executing them honestly.

Do NOT trigger for:

- Single-file bug fixes.
- One-off additions that don't change the architecture.
- PRs with a single scope where ordinary test + commit suffices.

## The 5 steps in detail

### Step 1 — IMPLEMENT

- Scope the phase strictly to what's in the plan. Don't pull items forward from a later phase even if they look easy. Cross-phase scope creep is how refactors become patches.
- Write code + ancillary unit tests for THIS phase only.
- When you hit a choice between "add a flag to preserve old behaviour" vs "commit to the new shape" — pick the new shape if the phase is a structural rewrite. Flags accumulate as debt.
- Update the todo list in real time: one task in-progress at a time.

### Step 2 — TEST

Always run all three of these, in order:

1. **Full unit suite** (`pytest -x -q`). Zero failures. If a legacy test is now obsolete because the contract changed, DELETE it — don't add a skip. An orphaned skip is a lie.
2. **Phase-specific canary or round-trip test**. Every phase has something to assert against its own goals:
   - Foundation/schema phase → round-trip test on N real fixtures.
   - Writer/generator phase → canary agentic run, output structural verifier.
   - Evaluator phase → re-score N historical articles, compare distributions.
   - Decommission phase → full niche suite, verifier stays green.
3. **Smoke test of the rest of the system** — import the app, hit a trivial endpoint (`/api/v1/health`), make sure nothing downstream broke.

Green all three, or stop and fix before step 3.

### Step 3 — PRODUCT-THINK (the "patch or real?" gate)

Write a short analysis with these explicit sections. This goes into the commit message OR into a roadmap doc. It does NOT go into ephemeral chat — the analysis has to be durable so a reviewer (human or subagent) can audit it later.

```md
## Phase {X} — Patch or Real Solution?

### What this phase actually changes (files modified, net LOC)

### Is this a patch?
Honest answer (yes/no), one paragraph of evidence. A patch is:
- another regex trying to repair the previous step's output, OR
- a flag that preserves legacy behaviour alongside new behaviour, OR
- a single-instance fix that doesn't generalise to the pattern.

### Is this a real solution?
Name the invariants the new code enforces by construction. Name the bugs it makes impossible (not "less likely" — impossible, enforced by types / schemas / tests).

### Honest weaknesses
What's deferred, what's best-effort, what's a known workaround. Don't hide these; next phase needs to pick them up.

### Recommendation
Ship / iterate / rollback.
```

If the phase is actually a patch, don't apologise — rename the phase as a patch and defer the real solution to its own future phase. Lying to the plan is worse than shipping a patch.

### Step 4 — VERIFY (independent subagent)

Spawn a fresh subagent via the Agent tool with `subagent_type: "general-purpose"` or `"Explore"`. The subagent has NO context from the implementing conversation. Give it:

- The phase's stated goals (copy verbatim from the roadmap).
- The file paths that were supposed to change.
- The product-think document from step 3.

Ask it to answer, for each stated goal:

- **RESOLVED** — the phase fully delivered this goal, verified by reading the code.
- **PARTIALLY RESOLVED** — partly delivered, name what's missing.
- **DEFERRED** — explicitly documented as deferred in the product-think gate.
- **REGRESSED** — something that was working before is now broken.

If the subagent comes back with anything REGRESSED, stop and fix before shipping. If something is PARTIALLY RESOLVED and you didn't flag it in step 3, amend the product-think doc to match reality before committing.

**Never skip this step.** The implementing assistant is the worst reviewer of its own work because it's primed to see the intended outcome rather than the delivered one.

### Step 5 — SHIP

Only ship when:

- Step 2 test gate passed (green).
- Step 3 product-think produced an honest answer.
- Step 4 subagent verification came back with no REGRESSED items and no undocumented PARTIALLY RESOLVED items.

Commit message structure:

```
{type}({scope}): {phase name} — {one-line outcome}

{product-think summary — 3-5 bullets}

Test results: N unit tests + canary/round-trip details.
Subagent verification: {RESOLVED N / PARTIAL N / DEFERRED N counts}.

Deferred to next phase: {explicit list or "none"}.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

Push the branch. Update the todo list: mark this phase's tasks completed, surface the NEXT phase's tasks as pending.

## Heuristics that keep this rhythm from bloating

- **Time-box the product-think analysis to ~15 minutes of drafting.** Longer means you're dressing up a patch as a real solution.
- **The subagent prompt should fit in 400 words max.** If you need more than that, the phase's scope is too big — break it.
- **One phase, one commit.** Don't stack phases in one commit "because they're related." The whole point is phase-boundary visibility.
- **Use fixtures from a baseline snapshot taken BEFORE the refactor.** When comparing "does Phase B output beat Phase A output", you need the frozen baseline to be meaningful.

## Common failure modes

- **Skipping step 4 because "tests are green."** Tests verify the things you wrote tests for. The subagent verifies what you DIDN'T think to test.
- **Optimistic product-think.** If you can't write an honest "is this a patch" without hedging, it's a patch. Own it, scope a real phase after.
- **Fixing subagent findings by modifying the phase goals instead of the code.** Moving goalposts is the sibling of shipping patches.
- **Forgetting the baseline snapshot.** Once Phase B ships, the Phase A output is the old production output — you cannot A/B compare if you didn't save it.

## Example skeletons

### Step 3 product-think (good)

> Phase B (structured-output writer) replaces the monolithic 1,600-token prompt with a Plan agent that emits a typed Article schema directly. Invariants enforced by construction: H1+byline cannot merge (separate fields), heading+body cannot merge (separate fields), hallucinated URLs fail Pydantic URL validation. Weaknesses: Plan agent still uses a single LLM call (no per-section agents yet — deferred to B.2). Recommendation: ship.

### Step 4 subagent prompt (good, tight)

> Audit Phase B of the writer pipeline refactor. Goal: replace monolithic WRITER_PROMPT with a Plan agent producing typed Article. Files changed: `src/nodes/generate.py` (replaced WRITER_PROMPT usage), new `src/agents/plan_agent.py`. Product-think doc at `docs/roadmap.md#phase-b`. For each goal (schema-constrained output, URL validation, no more merged H2s in output), report RESOLVED / PARTIAL / DEFERRED / REGRESSED with file:line evidence. Report under 400 words.

### Commit message (good)

> feat(writer): Phase B — structured-output writer via Plan agent
>
> Replaces monolithic WRITER_PROMPT string with build_writer_prompt-driven
> Plan agent that emits a typed Article directly. The LLM cannot physically
> produce merged H1+byline or hallucinated URL-scheme links because the
> Pydantic schema rejects them during decoding.
>
> - Tests: 895 unit green (was 885); canary run scored 91/A, all 15
>   structural invariants passed.
> - Subagent verification: 3 RESOLVED, 1 DEFERRED (per-section agents →
>   Phase B.2), 0 REGRESSED.
>
> Deferred to Phase C: Ragas-style claim grounding.
