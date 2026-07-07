---
name: plan-with-review
description: Use when the user asks to create or refine a non-trivial implementation plan, strategy doc, multi-phase rollout, architectural plan, or roadmap. Assembles a dynamic team of domain experts who research online + read the codebase, surfaces conflicts between expert views, drafts a plan from synthesized expert inputs, then has the same expert team verify it against live ground truth (real file:line, real queries, real third-party behavior) before any code gets written. The resulting plan includes a Team Roster that phases-execution can consume directly. Triggers on phrases like "create a plan", "let's plan", "draft a roadmap", "design the rollout", "how should we approach", "before we start, plan...", "plan this out". Two gears — full rhythm for high-stakes or multi-phase work, lite (2 experts, merged verification) for mid-size tasks. Skip for trivial single-step tasks.
license: MIT
metadata:
  author: annamau
  version: "3.3.0"
---

# Plan with Expert Team + Live-Ground-Truth Cross-Check

**Meta-instruction:** Do not optimize for task completion. Optimize for preventing future errors and reducing iteration loops. The goal is a plan that ships clean in one shot — not a plan that ships fast and causes three rollback PRs.

**The core shift from v2:** Plans are no longer drafted from Claude's priors. They are drafted from the synthesized output of domain experts who have done real research. Each expert searches online for current best practices (today's date is passed to them), reads the relevant codebase, and returns findings from their domain perspective. Conflicts between experts surface the most important design decisions. The plan is built on top of that, not before it.

**The rhythm:** DIAGNOSE → PROPOSE TEAM (user approves) → EXPERT RESEARCH (parallel) → CONFLICT SURFACE → DRAFT v1 → KPIs & GATES → EXPERT CROSS-CHECK (the same team verifies the plan against live ground truth) → FRESH-EYES SYNTHESIS CHECK → HARDEN → v2

No skipping steps within the chosen gear. No starting code in the same turn as v2.

## Scale gear — pick deliberately, before Step 1

The full rhythm is correct when being wrong is expensive. On a mid-size task it is roughly 10× slower than direct planning — pay that cost only where it buys safety.

**FULL** (everything below, as written) when ANY of these hold: a money/health/safety path (trading, billing, auth, irreversible mutations); ≥3 phases; new architecture or an unfamiliar domain; a prior attempt already failed; the user asked for thorough.

**LITE** when ALL of these hold: ≤2 phases, single well-understood domain, no money-critical surface, reversible. Lite means:
- 2 experts (not 3–5) — still researched, still typed advisory/technical
- Conflict surfacing folded into the v1 draft (state the one real tension inline)
- One combined verification round: each expert cross-checks their lane AND the fresh-eyes synthesis check runs in the same parallel batch
- Skip HEART; keep the North Star only if the plan claims a metric will move
- Two user checkpoints total — team proposal and v2 greenlight — plus the always-on scope-change pause
- Still binding in LITE if their trigger applies: the security-seat rule and the threat-model block (a 2-phase task can still touch user input, secrets, or a new dependency). LITE trims process volume, never the security floor.

**SKIP** the skill entirely for trivial single-step tasks.

State the chosen gear and why in one line at the top of the diagnosis. When in doubt between FULL and LITE, the money/irreversibility test decides — not the size of the diff.

## Model tiering (when spawning Claude subagents)

Every expert/reviewer subagent gets an explicit `model` matched to the work — never default blindly:

| Tier | Use for | Examples |
|------|---------|----------|
| **haiku** | Simple, mechanical, high-volume | research sweeps, inventory/health scans, doc lookups, table-state audits, consistency checks |
| **sonnet** | The default for most real work | domain research with judgment, focused implementation, independent code reviews, cross-checks |
| **opus** | Advanced reasoning / most technical | novel algorithm design, credit-assignment/attribution math, safety-critical mechanism design, deep multi-layer root-cause work |
| **fable** | **YMYL (Your Money or Your Life)** | anything where a wrong judgment costs real money, health, or safety: financial risk audits, position/portfolio judgment, go-live verdicts, final validation of money-critical changes |

Rules of thumb: the PROPOSE TEAM table must carry a **Model** column per expert (the user approves tiering with the team). Cross-check verifiers usually match the original expert's tier. When a finding's blast radius is financial, escalate the verifier to **fable** even if the original researcher was smaller. Cost discipline: prefer the smallest tier that genuinely carries the reasoning load — but never put haiku on judgment calls or opus-class math. Brief by tier: haiku dispatches get low-freedom, prescriptive briefs (exact questions, exact output format, word budget); opus/fable dispatches get goals and constraints — over-specifying wastes their judgment.

---

## Step 1 — DIAGNOSE

Before assembling the team, understand the problem. This is not a planning step — it is a root-cause step. Answer these questions from the conversation context, existing code, and your own knowledge:

**What is the actual goal?**
State it as an outcome, not a task. "Build an agentic topic-discovery workflow" is a task. "Increase the number of high-authority articles published per week from 3 to 12 without increasing human editorial time" is a goal. If the user gave you a task, find the goal behind it.

**What is the current state?**
Concrete metrics, file paths, known constraints. No vague "we have issues" — name them. Read key files if needed.

**Why hasn't this been solved already?**
Name the actual blockers: missing data, wrong architecture, wrong abstraction, wrong sequencing, unclear ownership. This is what separates a real plan from a patch.

**Which disciplines does this problem touch?**
List them. Some are advisory (they shape what the solution must achieve), some are technical (they shape how it gets built). You will use this list to compose the expert team.

**What research is needed?**
Each expert will search online. Identify the specific questions that need external answers — not general background, but specific current-state questions (e.g. "what is the current state of GEO optimization for AI-cited articles as of [today]?", "what are the latency characteristics of Claude claude-sonnet-4-6 tool-use chains at 50 concurrent requests?").

Present the diagnosis to the user in one concise block before moving to team composition. Keep it tight — the point is to show you understand the problem, not to write a plan.

---

## Step 2 — PROPOSE EXPERT TEAM (user must approve before spawning)

Based on the diagnosis, propose 3–5 experts. For each, state:

- **Role name** — descriptive and specific (not "technical expert" — "AI pipeline architect" or "SEO/GEO/AEO specialist")
- **Type** — `advisory` or `technical`
  - *Advisory*: produces direction, constraints, and traps. Reads code to understand context. Does NOT own implementation files.
  - *Technical*: produces direction AND a concrete implementation approach. Owns specific domains in the codebase.
- **Why this expert is on the team** — which part of the problem they cover, and what blind spot goes uncovered without them
- **Research mandate** — 2–4 specific online questions they will search + which codebase areas they will read
- **What they will NOT handle** — explicit exclusion, so there is no overlap ambiguity

Present the proposed team as a table. Wait for the user to approve, add, remove, or swap experts before spawning anything.

**On team composition:**
- Don't default to generic roles. "Backend engineer" is weak. "Event-driven pipeline architect (message-queue + serverless functions)" is what you want.
- Advisory experts are not lesser — an SEO/GEO/AEO expert who has read the current literature shapes the entire article structure. Their absence means the technical experts build the wrong thing perfectly.
- 3 focused experts beat 6 shallow ones. Prefer depth.
- **Security seat rule**: if the plan touches auth, user input parsing, secrets, new dependencies, payments, or agent-executed tools, the roster MUST include a security-typed expert (advisory or technical). AI-generated code fails security testing at ~45% in current benchmarks; the missing security seat is the most common roster blind spot. Their requirements bind like any advisory expert's.
- If the problem is purely technical, you may have 0 advisory experts. If it is a product/strategy problem, you may have 0 implementors. Match the team to the problem.

---

## Step 3 — EXPERT RESEARCH PHASE (all experts run in parallel)

Once the user approves the team, spawn all experts as subagents in a **single message** (parallel, not sequential).

**Every expert subagent prompt must include:**

1. **Today's date** — pass it explicitly so online research is anchored to the current state of the world, not the model's training cutoff.
2. **Their role and type** (advisory or technical)
3. **The goal and current state** from Step 1 — verbatim, not paraphrased
4. **Their research mandate** — the specific online questions to answer + codebase areas to read
5. **Their exclusions** — what they are not responsible for
6. **Required output structure** (see below)
7. **A word budget** — typically 600–900 words. Experts who ramble without one produce noise.

**Required output structure for each expert:** read `reference/templates.md` §1 and paste it verbatim into every expert prompt (research summary with URLs and search date, codebase observations with file:line, falsifiable domain requirements, concrete traps, unresolved questions).

Use `general-purpose` subagents (they have web search). Run all in **foreground** — you need all outputs before proceeding to conflict surfacing.

---

## Step 4 — CONFLICT SURFACING

Read all expert outputs. Before writing a single line of the plan, surface the tensions explicitly.

This step exists because the most important design decisions live in the conflicts, not the agreements. An SEO expert who wants daily re-crawls and an AI pipeline architect who says daily re-crawls will cost $8/day at current pricing are not both wrong — they are revealing a design constraint that must be resolved before the plan is written.

Structure the conflict surface per `reference/templates.md` §2: each conflict with both positions cited, stakes, and 2–3 resolution options (not a decision yet); then gaps no expert covered; then surprising findings that change the problem framing.

Present this to the user. **Two classes of conflict require a hard pause before proceeding:**

1. **Scope-changing findings** — if expert research reveals that the stated task is materially different from what was assumed (e.g. a dependency is unmaintained, a third-party cost is 10× higher than expected, a key feature already exists), surface it explicitly and ask the user to confirm the revised scope before writing v1. Example: "Expert research found that pytrends was archived in April 2025. This changes the feature from 'add GEO scoring' to 'fix trend data source + add GEO scoring.' Confirm scope?" Do not quietly absorb scope changes into the plan.

2. **Consequential design decisions** — if experts disagree on something that determines the architecture (e.g. "do we accept $8/day re-crawl cost or constrain frequency?"), ask the user to decide now. Present the options and stakes; don't pick unilaterally.

For conflicts you can resolve without the user (e.g. a technical tradeoff with a clear best answer based on expert evidence), resolve it and document why. Not every conflict needs a user decision — but scope changes and architecture choices always do.

---

## Step 5 — DRAFT v1

Write the v1 plan. Full section formats are in `reference/templates.md` §3 (plan structure) and §4 (Team Roster) — follow them verbatim. The required sections, and what each must deliver:

- **Goal** — one-sentence outcome, quantified (number + unit + deadline)
- **Current state** — concrete metrics, file paths, code references; name the issues
- **Phases** — per phase: what changes, why this slot, expected metric impact with math, risk level + primary risk, which expert's findings drive it, and expected diff size (flag > ~400 changed lines for a split — review depth drops past that, and AI-assisted diffs trend larger than they need to be)
- **Math sanity check** — formula + plugged values for every number the plan claims
- **Threat model (lightweight)** — REQUIRED when any phase touches auth, user input parsing, secrets, new dependencies, payments, or agent-executed tools: spoofing / tampering-injection / info-disclosure / privilege-elevation, one concrete line each, and every threat names the gate or misuse test that covers it. A threat without a covering test is an open plan item.
- **Operational readiness** — per behavior-changing phase: the observability signal that proves it works in production, the rollout lever (flag / canary / kill switch — or why plain deploy is safe), the rollback path (migrations must be expand-contract), and a one-line runbook
- **Test-first scaffold** — REQUIRED before any code: per phase, unit (3–10) + integration (1–3) + ONE misuse test; the implementer in phases-execution runs these BEFORE production code
- **Open questions** — unresolved after expert research; don't hide them
- **Team Roster + file-ownership map** — the block phases-execution consumes directly (§4); advisory experts listed with binding requirements, technical experts with owns / does-not-touch / mandate / depends-on, AND a per-phase **exclusive file set**. Execution runs the team concurrently in ONE shared worktree, so disjoint ownership is what makes phases parallelizable — two phases needing the same file must be merged, split, or sequenced HERE, at plan time; files shared by nature (barrel exports, route tables, migration indexes) are declared ledger files

**Decompose phases as vertical slices** — a user-visible capability end-to-end — not horizontal layers. Greenfield plans start with a walking skeleton phase: the thinnest end-to-end path through the architecture, proven live before anything is built on top.

---

## Step 6 — MEASURABLE KPIs & QUALITY GATES

Every metric and gate is a number with a unit — not an adjective.

### Adjective → number translation

| Adjective | Required form |
|-----------|--------------|
| "good performance" | `p95 latency < 200ms over 1h window` |
| "no regressions" | `North Star within ±2pts of baseline for 7d` |
| "high quality" | `≥ 95% of test cohort meets exit gate G3` |
| "scales well" | `tested at 10x current QPS; p95 budget holds` |
| "secure" | `OWASP top-10 checklist signed off + 1 hostile-input test green` |

If you cannot translate an adjective into a number with a unit, drop it.

### North Star + input metrics

Formats: `reference/templates.md` §5. ONE externally validated North Star — something the world tells us, not something we compute about ourselves — with precise definition, cadence, today's baseline, and milestone targets. Then 3–6 input metrics max, each with definition, today's value, target, and owning phase.

Each phase must move at least one input metric. If a phase doesn't, it doesn't belong.

### HEART (user-facing health — orthogonal to North Star)

When the plan changes a system users depend on, include the HEART table (`reference/templates.md` §5): Happiness, Engagement, Adoption, Retention, Task Success — each with a metric and a numeric red-flag threshold.

**Baseline capture — required when any HEART threshold says "vs. baseline":**
For each HEART metric that uses a comparative threshold (e.g. "drop > 30% vs. 14d baseline"),
explicitly state:
- **When** the baseline is captured (e.g. "7 days before Phase 1 ships" — not "before we start")
- **Who** captures it (the planner? a cron? a specific script?)
- **Where** it is stored so it can be compared later

A HEART threshold without a named baseline capture plan is decorative — add a Phase 0 or
pre-execution step if needed. The expert cross-check will catch ungated baselines; fix them in v1.

If a phase trips a HEART red flag, halt. Don't ship the next phase on top of a regression.

### Quality gates — falsifiable, with numbers

Each phase has **entry criteria** (must be true to start) and **exit criteria** (must be true to ship).

**Universal exit criteria:**
- All existing tests pass + new tests added — green
- North Star and input metrics do not regress beyond explicit allowance
- HEART metrics within threshold
- Independent reviewer subagent on the PR returns zero unresolved correctness findings
- Code coverage for changed files ≥ 80% (or project standard, named explicitly), and coverage on changed files never decreases
- Performance budget: p95 / p99 target stated and load tested
- Security floor: secrets scan on the diff is clean; every NEW dependency verified real on the public registry (mature, known maintainer) and pinned in the lockfile — ~20% of AI-suggested package names are hallucinated and squatters register them; SAST clean where the repo has it configured

**Phase-specific gates:** format in `reference/templates.md` §5 — every exit criterion falsifiable with a number and a unit, plus a scalability check where the plan named a load ceiling.

### Stop conditions

Format: `reference/templates.md` §5. Name the conditions under which the thesis is wrong (pivot), the software is unusable (halt), or a phase must roll back — each with a number and a time window.

### KPI anti-patterns (fix these in v1 — reviewer will catch them)

- **Self-graded North Star** — the metric must be externally validated
- **Adjective KPIs** — translate or delete
- **Too many input metrics** — > 6 means nobody watches them
- **Lagging-only metrics** — mix leading and lagging
- **Gates that always pass** — real gates fail sometimes; decorative gates are theater
- **Ungated billing** — any charge to users needs a billing-correctness exit criterion

---

## Step 7 — EXPERT CROSS-CHECK (the dedicated team verifies the plan against live ground truth)

There is no generic hostile red-team. A context-free reviewer reasons from priors and stale assumptions — it will "break" the plan against a version of the system that no longer exists, and push the team backward. Instead, the **same domain experts who researched the problem** now verify the v1 plan against **live ground truth**. They have the context; they are accountable to their field; they check the plan with real data, not invented failure modes.

Re-engage the experts from the Team Roster — via `SendMessage` to their existing agent IDs, or spawn fresh experts of the same roles. When spawning fresh, paste the original expert's Step-3 findings verbatim into the prompt: a fresh spawn without its predecessor's research verifies with amnesia. Technical experts verify code and data claims. Advisory experts whose requirements are load-bearing in v1 re-engage too — their claims (a ranking behavior, a compliance rule, a market convention) are verified against current online sources exactly the way code claims are verified against file:line. Run them in **foreground** — you need their output before hardening.

Each expert's cross-check prompt must include:

1. **The full v1 plan** — verbatim.
2. **Today's date.**
3. **Their domain** — the same one they researched. They check ONLY the claims and phases in their lane.
4. **A verification brief (not a hostile one):**
   > "You researched this problem. Now verify the v1 plan against LIVE ground truth in your domain. For every load-bearing claim the plan makes, confirm or refute it with evidence — read the actual file:line, run the actual query against live data (read-only), check the actual current third-party behavior online. Do NOT invent failure modes from priors; if the plan rests on a number (a word count, a row count, a price, a model behavior), GO GET THE REAL NUMBER and report whether the plan's assumption holds. Today's date is [date]. Your job is to make the plan TRUE, not to break it."
5. **Required output per expert:**
   - **Claims verified** — each load-bearing claim in their lane → confirmed/refuted, with the file:line, query result, or URL that proves it.
   - **Numbers that were wrong** — any quantitative assumption the plan made that the live data contradicts (the single highest-value output — e.g. "plan says articles are 500w; live p50 is 2,598w").
   - **Real failure modes** — only those grounded in verified current behavior (a gate that will actually fire on real packs, a real rate limit, a real cost), with the evidence.
   - **Sequencing / dependency corrections** — any phase that demands data a prior phase hasn't produced yet, verified against the live schema.
   - **What the plan got RIGHT** — explicitly confirm the parts that hold, so hardening doesn't thrash them.
6. **Word budget**: 600–900 words per expert. file:line for code, query results for data, URLs for third-party claims.

Spawn the experts in **parallel** (single message), **foreground**. Read every cross-check before Step 8. If the experts surface a **scope-changing** correction (a core assumption is false against live data), pause and surface it to the user before hardening — the same way Step 4 pauses on scope changes.

### Step 7b — FRESH-EYES SYNTHESIS CHECK (one verifier, no prior context)

Each domain expert verifies their own lane; nobody checks the space between the lanes — and the synthesis is yours, so you cannot fresh-eyes it yourself. Spawn ONE verifier who was not on the roster and has no conversation context. They receive exactly two things: the v1 plan and the raw Step-3 expert findings. Not the conversation, not the cross-check outputs.

Brief:
> "Verify the synthesis, not the world. The experts' findings are your only evidence — do not research beyond them, do not invent failure modes from priors. Answer: (1) Does each phase actually follow from the evidence, or does the plan over-extrapolate somewhere? Quote any expert finding the plan distorted, ignored, or stretched. (2) Is there an alternative framing of the SAME evidence that would change a phase or the sequencing? Propose at most one, and only if it is load-bearing. (3) Which expert findings did the plan silently drop? Cite the expert section for every claim. ≤500 words."

Model: sonnet by default; escalate to fable when the plan touches money paths (per the tiering table). Run it in the same parallel batch as the expert cross-checks — it needs only v1 and the Step-3 findings, both already available.

This restores fresh-context review without restoring the context-free hostile reviewer the v3 redesign removed: the verifier is identity-fresh but evidence-bound. Its findings feed Step 8 alongside the expert cross-checks.

---

## Step 8 — HARDEN (produce v2 as explicit deltas on v1)

Produce v2 per `reference/templates.md` §6 — the required sections, in order: **what v1 got wrong** (quote the v1 claim, then the correction, with the file:line / query result / URL — or the distorted expert finding — that proved it; never quiet-rewrite); **numbers the cross-check corrected** (v1 assumption → real value → which phase changes); **real failure modes → how v2 addresses each** (new gate / test / phase / sequencing change); **missing edge cases now covered** (each mapped to a named test); **scalability risk → mitigation** (ceiling stated, load test in a phase exit gate); **what the cross-check confirmed was right** (so hardening doesn't thrash it); **corrected sequencing, math, KPIs & gates** (show deltas); **updated test-first scaffold**; **updated Team Roster**; **ready-to-start step** (ONE concrete next action).

End by asking the user to greenlight a specific decision before code starts. Do NOT start implementing in the same turn as v2.

---

## Unattended mode

Only active when the user explicitly pre-authorized autonomous planning ("plan it overnight, don't wait for me"). Ambiguity means attended. A plan is a document, not a deployment, so checkpoints degrade instead of blocking:

- **Team approval (Step 2)** → log the proposed team with one line of justification per expert and proceed.
- **Scope-change and design-decision pauses (Steps 4 and 7)** → apply the same test as below: if a conservative interpretation exists (smaller scope, cheaper option, reversible default), take it, plan for it, and record what you would have asked; if the correction is architecture-determining with no conservative default, halt per the rule below. A Step-7 live-data refutation of a core assumption usually has no safe default — expect it to halt.
- **v2 greenlight (Step 8)** → the plan ends with the open decision stated, not with code started.

Every auto-resolved checkpoint goes into a **"Decisions made without you"** block at the TOP of v2 — the first thing the user reads, before the goal. One thing still halts: a consequential, architecture-determining decision with no conservative default. Deliver the decision brief as the output instead of a guessed plan.

---

## What good looks like

A v2 plan that:
- Was built from expert research, not from Claude's priors
- Names exactly which v1 claims were wrong, with corrections next to them
- Lists 3 failure scenarios with the gate / test / phase change that catches each
- Has a sequencing table where every phase's slot is justified
- Closes the math (the target is reachable given the formula, OR the formula is being changed)
- Has zero adjective-only metrics
- Lists per-phase unit + integration + misuse tests, with misuse tests visibly adversarial
- States a scalability ceiling and how phase N's exit gate proves it holds
- Carries a Team Roster that phases-execution can consume without re-deriving the team
- States its gear (FULL/LITE) up front and carries the fresh-eyes verifier's verdict on the synthesis
- Ends with one specific question for the user, not "shall I proceed?"

## Anti-patterns this skill prevents

- **Planning from priors**: drafting a plan before consulting domain experts and current online research. The experts shape the plan, not vice versa.
- **Aligned expert teams**: picking experts who will agree with each other. The conflict surfacing step only has value if the experts have genuinely different perspectives.
- **Advisory experts as decoration**: listing an SEO expert but not letting their requirements constrain the technical design. Advisory requirements are non-negotiable inputs.
- **Plan-and-ship in one breath**: writing a plan and starting code in the same turn skips the review gate.
- **False code citations**: the expert cross-check reads actual files and will catch this.
- **Math that doesn't close**: the cross-check plugs the numbers against live data.
- **Self-graded victory**: choosing an internal score as North Star.
- **Ungated billing**: billing without a phase exit criterion proving Stripe idempotency + refund path.
- **Context-free reviewer reasoning from priors**: a generic hostile reviewer with no shared context "breaks" the plan against a version of the system that no longer exists, pushing the team backward. The cross-check is done by the dedicated experts who have the context and verify against LIVE ground truth — they make the plan true, not break a strawman.
- **Assuming instead of measuring**: when the plan rests on a number (word count, row count, price, model behavior), GO GET THE REAL NUMBER from live data before hardening — never harden against an assumed value.
- **Test-after-code**: test scaffold ships with the plan, before any production code.
- **Stale research**: experts receive today's date and cite search dates. Plans built on 18-month-old API pricing or deprecated library patterns are rejected.
- **One-size process**: running the FULL rhythm on a mid-size task burns tokens and user patience without buying safety. Pick the gear deliberately and say which in the diagnosis.
- **Unverified synthesis**: every expert checks their own lane; the gaps BETWEEN lanes are where a plan quietly fails. That is the fresh-eyes verifier's lane — don't skip it because the experts all passed.

---

## Final do-confirm (run after drafting v2, before presenting it)

Do-confirm, not read-do: you already did the work — this catches what slipped. Confirm each item; any miss means v2 is not ready to present:

- [ ] Gear declared (FULL/LITE) with a one-line justification at the top of the diagnosis
- [ ] Every expert searched online with today's date and cited their search dates
- [ ] Conflicts surfaced BEFORE drafting; scope changes were user-confirmed, never quietly absorbed
- [ ] Security seat on the roster if the plan touches auth / input / secrets / deps / payments / agent tools
- [ ] Cross-check verified every load-bearing claim against LIVE data (file:line, query result, URL) — no number hardened from an assumption
- [ ] Fresh-eyes synthesis check ran, and its findings are addressed (or explicitly rebutted) in v2
- [ ] Zero adjective-only metrics; the math closes; every comparative baseline has a named capture plan (when / who / where)
- [ ] Threat model + operational readiness blocks present where required
- [ ] Test-first scaffold per phase; misuse tests visibly adversarial
- [ ] Team Roster complete and typed, with a file-ownership map whose in-flight sets are disjoint (shared-by-nature files declared as ledger files); v2 ends with ONE specific question for the user
