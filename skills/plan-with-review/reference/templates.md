# plan-with-review — output formats & templates

Loaded on demand from SKILL.md at the step that uses each section. Paste formats verbatim into prompts or the plan doc — do not paraphrase them.

## 1. Expert research output structure (Step 3)

```
## Expert findings: [Role name]
### Online research summary
[What you found. Cite sources with URLs. Flag anything that surprised you or contradicts conventional wisdom. State the date you searched — today's date was provided.]

### Codebase observations
[What you read. file:line citations for every claim. What the current code does well. What it cannot do without changes.]

### What the solution needs from my domain
[2–5 concrete requirements the plan must satisfy. Numbered. Specific enough to be falsifiable.]

### Traps and failure modes I see
[2–4 things that will go wrong if the plan ignores my domain. Concrete, not theoretical.]

### Open questions I could not resolve
[Things I searched for but couldn't find definitive current answers on. Flag these for the plan author.]
```

## 2. Conflict surfacing format (Step 4)

```
## Expert conflicts and tensions

### Conflict 1: [short name]
- [Expert A] says: [their position, with citation to their output]
- [Expert B] says: [their position, with citation to their output]
- Stakes: what goes wrong if we pick one and ignore the other
- Resolution options: [2–3 ways to address this — not a decision yet]

### Conflict 2: ...

## Gaps no expert covered
[Things that fall between expert domains and were not addressed by anyone. These are planning risks.]

## Surprising findings
[Things the experts found online that change the problem framing — updated API pricing, a new library that makes a previous approach obsolete, a published case study that contradicts the assumed approach.]
```

## 3. v1 plan structure (Step 5)

```
## Goal
[One-sentence outcome. Quantified if possible — number + unit + deadline.]

## Current state
[Concrete metrics, file paths, code references. No vague "we have issues" — name them.]

## Phases
For each phase:
- What it changes (files, tables, formulas)
- Why this slot in the sequence
- Expected metric impact (with math)
- Risk level (low/medium/high) and primary risk
- Which expert's findings drive this phase
- Expected diff size in changed lines (flag > ~400 for a split)

## Math sanity check
[If the plan claims a number — score, percent, time — show the formula and plug values.]

## Threat model (lightweight)
REQUIRED when any phase touches auth, user input parsing, secrets, new dependencies,
payments, or agent-executed tools. Per exposed phase, one line each — concrete, not theoretical:
- Spoofing/auth: how could a request pretend to be someone else? Covered by [gate/test].
- Tampering/injection: which inputs reach an interpreter (SQL, shell, HTML, prompt)? Each covered by [misuse test].
- Info disclosure: what could leak into logs, errors, or LLM context? Covered by [gate/test].
- Privilege elevation: can the change make any actor (user, agent, tool) exceed intended permissions? Covered by [gate/test].
A threat line without a covering gate or misuse test is an open plan item — resolve it before v2.

## Operational readiness
Per phase that changes runtime behavior:
- Observability: the specific log line / metric / alert that will prove this phase works in production
- Rollout: flag / canary / kill switch for risky behavior changes — or state why plain deploy is safe
- Rollback: the concrete path back (DB migrations must be expand-contract: old code runs against the new schema)
- Runbook line: one sentence — when X breaks, do Y

## Test-first scaffold (REQUIRED — before any code)
For each phase:
- Unit tests: 3–10 cases. Cover happy path + 2+ failure modes.
- Integration tests: 1–3 cases hitting the real boundary the phase changes.
- Misuse test: ONE test proving the system behaves safely when called wrong
  (bad input, race condition, partial state, permission edge, concurrent call).
The implementer in phases-execution will run these BEFORE writing production code.

## Open questions
[Things unresolved after expert research. Don't hide them — the reviewer will surface them anyway.]

## Team Roster
[See §4 — this block is consumed directly by phases-execution.]
```

## 4. Team Roster format (Step 5)

```
## Team Roster

| Expert | Type | Owned domains | Explicit exclusions | Key findings summary |
|--------|------|---------------|--------------------|--------------------|
| [Role] | advisory / technical | [files, tables, services, or domain areas] | [what they don't touch] | [1–2 sentence summary of their most important findings] |

### Role contracts (for phases-execution)
For each technical expert:
- **Owns**: [specific files, directories, or system boundaries]
- **Does not touch**: [explicit exclusions]
- **Implementation mandate**: [what they will build, in one sentence]
- **Depends on**: [other experts' outputs they need before starting]

Advisory experts are listed but have no implementation mandate. Their findings shape requirements; they do not write code.

### File-ownership map (for phases-execution's shared-worktree team)

```
| Phase | Owner (technical expert) | Exclusive file set |
|-------|--------------------------|--------------------|
| 1 | [role] | [exact paths — files or directories] |
| 2 | [role] | [exact paths] |

Ledger files (owned by no one; edited only via a LOCKS.md claim, one holder at a time):
- [paths shared by nature — barrel exports, route tables, migration indexes — or "none"]
```

Invariant: every file appears in at most ONE in-flight phase's set. Two phases needing the same file = merge them, split the file's concern, or sequence the phases — resolve it in the plan, not during execution.

Note to phases-execution: this roster is a starting point. You may spawn additional agents based on implementation findings. You may not remove an advisory expert's requirements from the plan without explicit user approval.
```

## 5. KPI & gate formats (Step 6)

```
## North Star Metric
[ONE metric. Externally validated — something the world tells us, not something we compute about ourselves.]
- Definition (precise formula or query)
- Cadence (daily / weekly / monthly rollup)
- Today's value (baseline, with units)
- Targets at milestones (with units)

## Input metrics (3–6 max)
| # | Metric | Definition | Today | Target | Phase |
```

HEART table (when the plan changes a system users depend on):

```
| Dimension | Metric | Red-flag threshold |
|-----------|--------|-------------------|
| Happiness | NPS / CSAT | < 7 or 7d trend negative |
| Engagement | Core action frequency | drop > 30% vs. 14d baseline |
| Adoption | New-user activation rate | drop > 20% |
| Retention | 30-day retention | < 80% |
| Task Success | % attempts completing | < 75% on N=100+ |
```

Phase-specific gates:

```
### Phase N — [name]
- *Entry*: [what must already exist, with numbers]
- *Exit*:
  - [falsifiable criterion with number and unit]
  - [another]
  - [scalability check: tested at Nx current load]
```

Stop conditions:

```
## Stop conditions
- North Star doesn't move > X units after phase N ships + Y weeks → thesis is wrong, pivot
- HEART metric Y < threshold for 14d → shipping unusable software
- Phase exit fails on test cohort but you ship to others → using customers as QA
- Hard regression on metric Z > N points sustained 7d → rollback the phase
```

## 6. HARDEN v2 structure (Step 8)

```
## What v1 got wrong (3–5 items)
[Quote the v1 claim, then the correction from the expert cross-check or the fresh-eyes synthesis check. Never quiet-rewrite. Each correction cites the file:line / query result / URL — or the distorted expert finding — that proved it.]

## Numbers the cross-check corrected
- [v1 assumption] → [real value from live data] → [which phase changes as a result]

## Real failure modes the cross-check found → how v2 addresses each
- Mode 1: [name, with evidence] → addressed by [new gate / new test / new phase / sequencing change]
- Mode 2: ...
- Mode 3: ...

## Missing edge cases now covered
- Edge 1: [name] → covered by test [name] in phase [N]

## Scalability risk → mitigation
[Risk: design fails at X (verified against live load/limits). Mitigation: load test in phase N exit gate; ceiling stated explicitly.]

## What the cross-check confirmed was right
[The verified-correct parts, so hardening doesn't thrash them.]

## Corrected sequencing
[Table: # | Phase | Why this slot | Risk | Depends on]

## Corrected math
[Restate honestly. Either change the target or change the formula.]

## Corrected KPIs & gates
[Show deltas. If North Star was self-graded, swap it. If gates were unfalsifiable, rewrite with numbers.]

## Updated test-first scaffold
[Per phase: unit + integration + misuse, with new edge cases folded in.]

## Updated Team Roster
[If the cross-check surfaced a domain gap, add the expert or update existing contracts.]

## Ready-to-start step
[The single concrete next action. One thing.]
```
