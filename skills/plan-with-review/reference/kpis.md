# KPIs and quality gates

Read at Step 6, when turning plan goals into falsifiable numbers.

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
