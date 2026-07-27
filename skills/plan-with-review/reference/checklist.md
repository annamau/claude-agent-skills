# Plan quality checklist

Read after drafting v2, before presenting it.

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
