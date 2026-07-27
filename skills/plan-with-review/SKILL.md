---
name: plan-with-review
description: Plan non-trivial work, then verify the plan against live ground truth before any code is written. Use for implementation plans, multi-phase rollouts, architectural designs, and roadmaps ("create a plan", "how should we approach", "design the rollout", "plan this out"). Hands off to `ship` for execution.
when_to_use: When being wrong is expensive — money or safety paths, unfamiliar domains, three or more phases, or a prior attempt already failed. Skip for single-step tasks; a one-sentence diff needs no plan.
license: MIT
---

# Plan, then verify the plan

Plans get graded by nothing. The diff gets reviewed against the plan, so a
wrong plan passes review — a fabricated file path, a stale price, an API that
does not behave the way the plan assumes. Nobody catches it, because the plan
is the oracle.

This skill exists for one step: **before writing code, check the plan's
load-bearing claims against reality.** Everything else here is ordinary
planning, kept deliberately short.

Hallucinated references are measured at 4.6–6.1% in current models, and about
43% of them reproduce identically on retry — so asking again is not a check.
Going and looking is.

## Scale

Full rhythm costs roughly 10× direct planning on a mid-size task. Pay it when
being wrong is expensive: money, health, safety, irreversible mutations, ≥3
phases, unfamiliar architecture, or a prior attempt that already failed.

Otherwise run it small: one or two researchers, verification folded into one
pass. State which gear you chose and why, in one line.

The test is blast radius, not diff size.

## 1 — Diagnose

Before any planning, answer four things from the code and the conversation:

- **The goal as an outcome, not a task.** "Build topic discovery" is a task.
  "Publish 12 high-authority articles a week without more editorial time" is a
  goal. If given a task, find the goal behind it.
- **Current state, concretely.** Metrics, file paths, constraints. Read the
  code. No vague "we have issues."
- **Why this is not already solved.** Missing data, wrong abstraction, wrong
  sequencing, unclear ownership. This is what separates a plan from a patch.
- **What needs external research.** Specific current-state questions, not
  background reading.

Present it tight. The point is to show you understand the problem.

## 2 — Research

Spawn researchers only where genuinely different expertise changes the answer.
What makes this work is **diverse priors, not the number of agents** — two
perspectives that actually differ beat five that agree. Structural ceremony
around them buys nothing measurable.

Each researcher gets: today's date, the goal and current state verbatim,
specific questions, and a word budget (600–900). Without a budget they ramble.

Require file:line for code claims, URLs with a search date for external ones.

Run them in parallel, in one message. Read every output before drafting.

If research reveals the task is materially different from what was assumed — a
dependency is dead, a cost is 10× the estimate, the feature already exists —
**stop and confirm the revised scope.** Do not absorb a scope change silently.

## 3 — Draft

Full section formats in `reference/templates.md` §3. The plan must deliver:

- **Goal** — one sentence, quantified: number, unit, deadline.
- **Current state** — metrics and file paths, not adjectives.
- **Phases as vertical slices** — a user-visible capability end to end, never a
  horizontal layer. Greenfield starts with a walking skeleton: the thinnest
  end-to-end path, proven live before anything is built on it.
- **Math sanity check** — formula and plugged values for every number claimed.
- **Threat model** — required when a phase touches auth, user input, secrets,
  new dependencies, payments, or agent-executed tools. Spoofing, tampering,
  disclosure, privilege escalation: one concrete line each, each naming the
  test that covers it. A threat with no covering test is an open plan item.
- **Operational readiness** — per behavior-changing phase: the signal that
  proves it works in production, the rollout lever, the rollback path
  (migrations expand-contract), a one-line runbook.
- **Unit-of-work list** — what `ship` executes, in order. Each unit is the
  smallest independently shippable change and **carries the command that
  verifies it plus its pass condition**. A unit with no check is not ready to
  plan. Resolve that here, where it is cheap.
- **Open questions** — unresolved after research. Do not hide them.

Flag any phase over ~400 changed lines for a split. Review depth collapses past
that, and agent-written diffs trend larger than they need to be.

Every gate is a number with a unit and a command that measures it. See
`reference/kpis.md` for translating adjectives into numbers.

## 4 — Verify against ground truth

This is the step that justifies the skill.

Send the plan back to the researchers from step 2 — via `SendMessage` to their
existing agent IDs, or fresh spawns with the original findings pasted in. A
fresh spawn without its predecessor's research verifies with amnesia.

The brief matters, and it is **not** hostile:

> You researched this. Now verify the plan against LIVE ground truth in your
> domain. For every load-bearing claim, confirm or refute it with evidence:
> read the actual file:line, run the actual read-only query, check the actual
> current third-party behavior. Do not invent failure modes from priors. If the
> plan rests on a number — a word count, a row count, a price, a model
> behavior — go get the real number and report whether the assumption holds.
> Today is [date]. Your job is to make the plan TRUE, not to break it.

A reviewer told to find gaps reports some even when the work is sound, and
chasing invented findings produces over-engineering. Hostility is the wrong
setting here; verification is the right one.

Required back from each:

- **Claims confirmed or refuted**, each with the file:line, query result, or URL.
- **Numbers that were wrong** — the highest-value output. "Plan assumes 500-word
  articles; live p50 is 2,598."
- **Real failure modes**, grounded in verified current behavior only.
- **Sequencing corrections** — a phase needing data an earlier phase has not
  produced, checked against the live schema.
- **What holds** — so hardening does not thrash the parts that were right.

Then one **synthesis check**: a verifier who was not on the roster, given only
the plan and the raw research. Not the conversation, not the cross-checks.

> Verify the synthesis, not the world. The research is your only evidence.
> Does each phase follow from it, or does the plan over-extrapolate? Quote any
> finding the plan distorted, ignored, or stretched. Which findings did it
> silently drop? ≤500 words.

Domain experts each check their own lane; nobody checks the space between
lanes, and the synthesis is yours, so you cannot check it yourself.

If verification refutes a core assumption, that is a scope change. Surface it
before hardening.

## 5 — Harden

Rewrite the plan with the corrections applied. Two rules:

**Never quiet-rewrite.** Where a claim changed, show the original, the
correction, and the evidence that forced it. A plan that silently absorbs its
own corrections teaches nobody anything, including you.

**End with one concrete next action** and the open decision stated plainly.

Do not start implementing in the same turn. Hand off to `ship`.

## Anti-patterns

- Planning a task whose diff you could describe in one sentence.
- Expanding a bug fix into user stories with acceptance criteria. Measured
  case: the spec took longer to write and review than the fix would have.
- A plan so long it gets partially ignored at execution — the failure mode is
  real and it is not the executor's fault.
- Adjectives where numbers belong: "fast", "robust", "scalable".
- Verification that reasons from priors instead of going and looking.
- Starting code in the same turn as the finished plan.

## Detail

`reference/templates.md` — section formats.
`reference/kpis.md` — adjective→number translation, gate formats.
`reference/checklist.md` — pre-flight before presenting the plan.
