---
name: copilot-review-loop
description: After opening or pushing to a PR, trigger a cross-model reviewer to review it via PR comment, loop on findings against explicit exit criteria (including plan AC gates and advisory expert requirements), apply the PO acceptance gate, and track recurring patterns so repeated issues escalate to root-cause fixes. Use this whenever a PR is open and not yet merged — do not declare a PR "ready to merge" without the PO gate passing.
license: MIT
metadata:
  author: annamau
  version: "3.1.0"
---

# PR review loop — cross-model review + PO acceptance gate

## Configuration

This skill uses `{{REPO}}` for the GitHub `owner/repo` slug and `{{REVIEW_BOT_LOGIN}}` for the cross-model reviewer bot's login. Set them for your project (in a local ADAPTER file or by substituting inline). Defaults below assume OpenAI's Codex GitHub app.

The cross-model reviewer is **a cross-model reviewer (default: OpenAI Codex GitHub app)** — swappable for any GitHub-app reviewer from a different model family than the implementer. The concrete setup instructions below assume Codex; substitute your reviewer's install steps and trigger phrase if you use another.

---

**Meta-instruction:** Do not optimize for task completion. Optimize for preventing future errors and reducing iteration loops. A PR that ships clean in one shot beats one that ships fast and causes three rollback PRs.

**The rule:** A PR is not mergeable until **all exit criteria pass** — including the PO acceptance gate. Reviewer silence ≠ done. Reviews are inputs to a learning system: the same comment appearing twice triggers a root-cause fix, not another patch.

**The reviewer:** The cross-model reviewer (default: OpenAI Codex GitHub app, `{{REVIEW_BOT_LOGIN}}`) reviews the diff. Claude implements → the reviewer reviews. Different model family = genuinely independent perspective on the same diff.

**Two nets, not one:** during execution, `phases-execution` Step 5c already ran a LOCAL cross-model CLI review on each functionality commit (with the default reviewer: `codex exec review --commit <sha>`). This PR-level loop is the second net — it sees the *integrated* round, which per-commit reviews structurally can't. If the board shows 5c was skipped for any commit (rate limit, auth), this loop is the only cross-model gate left — do not soften it.

---

## Exit criteria (must ALL be true to merge)

1. **Local pre-push review CLEAN.** A local subagent reviewed the diff against the goal, phase contract, and acceptance criteria — no BLOCKERs.
2. **Cross-model review CLEAN.** Preferred: the cross-model reviewer (default: Codex, once wired to `{{REPO}}`) has no unresolved P0/P1 findings on the latest commit. Fallback (reviewer not yet connected): a local `general-purpose` subagent acting as independent reviewer returns no BLOCKERs. Nits with replies don't block; bugs do.
3. **No repeated comments.** No issue has appeared 2+ times in this PR. If one has, it's been root-caused.
4. **All tests pass.** CI green on the latest commit — unit, integration, misuse test from the plan scaffold.
5. **Acceptance criteria satisfied.** Every must-pass AC gate from the phase contract passes. Reviewer silence ≠ AC satisfied — separate check.
6. **Advisory expert requirements held.** Any advisory expert requirements from the plan's Team Roster that apply to this phase are present in the diff.
7. **PO acceptance gate passed.** Orchestrator reviewed the deliverable against the plan's goal — goal alignment confirmed, no quiet drift.
8. **Review reflects latest commit.** The reviewer's review was posted after the latest commit's push timestamp. No stale-review merges.

---

## Step 0 — Local pre-push review

Before pushing, spawn a local `general-purpose` subagent. Cheapest gate — catches everything before CI or Codex burns time.

Subagent prompt must include:
- **Stated goal** — what the PR accomplishes in 1–2 sentences
- **Phase contract** — owned files, exclusions (from `phases-execution`). Check: did the diff touch files outside the contract?
- **Acceptance criteria** — the must-pass AC gates. Check: does the diff plausibly satisfy each one?
- **Advisory expert requirements** — any non-negotiables from the plan's Team Roster
- **The diff** — `git diff origin/main..HEAD`
- **Brief**: *"Does this diff achieve the stated goal? Stay within the phase contract? Satisfy the AC gates? Preserve advisory expert requirements? List BLOCKERs (goal drift, contract violations, AC gaps, expert requirement missing) and NOTEs (minor concerns). Recommend push or fix first."*

Any BLOCKER → fix before pushing. CLEAN → proceed to step 1.

---

## Step 1 — Verify the reviewer is wired, then trigger

**First — confirm the reviewer has ever reviewed this repo.** Run this before posting any trigger comment:

```bash
# Check if the reviewer bot has posted on a recent PR.
# Match with startswith(), NOT equality — the login carries a "[bot]" suffix.
gh api repos/{{REPO}}/issues/<recent-pr>/comments \
  --jq '[.[] | select(.user.login | startswith("{{REVIEW_BOT_LOGIN}}"))] | .[] | {login: .user.login, body: .body[:120]}'
```

If that returns nothing → **the reviewer is not connected to this repo.** Do not post the trigger comment — it will be silently ignored.

**To connect the reviewer (default: OpenAI Codex GitHub app — two steps):**
1. Install the GitHub App: go to `https://github.com/apps/chatgpt-codex-connector/installations/new` → grant access to `{{REPO}}`
2. Create a repo environment: go to `https://chatgpt.com/codex/cloud/settings/environments` → create an environment for `{{REPO}}` (without this, Codex posts a setup prompt instead of a real review)
3. Verify: post `@codex_review` on any PR — you should get a real review within 4 minutes, not a setup link

**Once wired — confirm the exact bot login:**
```bash
# After your first real review, run this to get the exact login:
gh api repos/{{REPO}}/issues/<any-pr-with-a-review>/comments \
  --jq '[.[] | select(.user.type == "Bot")] | .[].user.login'
```
Set `{{REVIEW_BOT_LOGIN}}` (and the `startswith()` filter in Step 3) to whatever login this returns. Do not assume the Codex default (the app's slug shown in the install URL above) — verify from an actual review, because the exact login (including its `[bot]` suffix) is what the filters depend on.

**Trigger (once confirmed wired):**
```bash
gh pr comment <PR> --body "@codex_review"
```

Re-trigger after every push by posting the comment again — the reviewer reviews the commit snapshot at request time.

**If the reviewer is not yet wired:** skip steps 2–3 and substitute a local `general-purpose` subagent as the cross-model reviewer. Brief it as: *"You are an independent reviewer. You did not write this code. Review the diff as a hostile outsider — find bugs, contract violations, AC gaps, security risks. Cite file:line for every finding."* This is a weaker substitute (same model family as the implementer) but satisfies the independent review exit criterion until the reviewer is connected.

---

## Step 2 — Schedule a wakeup, do not poll

The reviewer takes 1–4 minutes. Yield the conversation rather than sleep-looping — use the
`ScheduleWakeup` tool if available (it appears in the deferred tool list as `ScheduleWakeup`
and can be fetched via ToolSearch). If it is not available in the current session, tell the
user "I'll check back in ~90 seconds" and wait for them to re-invoke, or use
`mcp__scheduled-tasks__create_scheduled_task` as an alternative.

- First check: 90s after comment posted
- Subsequent: 60s if still in progress, 30s to read final output

Pass the same loop prompt back so the wakeup re-enters this skill.

---

## Step 3 — Read the review

```bash
# Top-level review state
gh api repos/{{REPO}}/pulls/<PR>/reviews \
  --jq '[.[] | select(.user.login | startswith("{{REVIEW_BOT_LOGIN}}"))] | .[-1] | {state, submitted_at, body}'

# Inline comments (the substantive findings)
gh api repos/{{REPO}}/pulls/<PR>/comments \
  --jq '[.[] | select(.user.login | startswith("{{REVIEW_BOT_LOGIN}}"))] | sort_by(.created_at) | .[] | {id, path, line, body, created_at}'

# NOTE: use startswith(), not equality — the actual bot login carries a bracket "[bot]" suffix
# (Codex's default login is its app slug + "[bot]"). Equality match causes the polling loop to
# return empty forever. Verify the exact login once from any real review on the repo and set
# {{REVIEW_BOT_LOGIN}} to it:
# gh api repos/{{REPO}}/pulls/<any-pr>/reviews --jq '.[].user.login'
```

Three states:
- **APPROVED, no inline comments** → proceed to PO acceptance gate (step 5)
- **Still pending** → wakeup again
- **Inline comments present** → triage (step 4)

Verify `submitted_at` is after the latest commit's push time. If stale → re-trigger with a new `@codex_review` comment.

---

## Step 4 — Triage + pattern tracking

Classify each comment as **Reviewer A (correctness)** or **Reviewer B (readability)**, then check the pattern log.

### Per-comment classification

- **Bug, correctness, security, contract violation, AC gap, advisory expert requirement missing (A)** → fix. New commit. Tag in pattern log.
- **Style/nit (B)** → fix if cheap; reply explaining the trade-off. Tag.
- **False positive** → reply with one-line explanation. Tag.
- **Pre-existing issue out of scope** → `mcp__ccd_session__spawn_task` + reply noting it. Tag.

Always new commit — never amend or force-push. The reviewer needs a clean diff on re-trigger.

### Pattern tracking — escalate repeats

Keep an in-conversation log with a running iteration counter (hard cap is 5 — make it visible):

```
PR #N pattern log — iteration 1/5:
- iter 1: missing null check on org_id (X:42) — A
- iter 2: missing null check on user_id (X:67) — A  ← REPEAT → root-cause fix triggered
```

The counter makes the 5-iteration cap visible and prevents quietly running a 6th round.

**2+ occurrences of the same pattern → root-cause fix, not another patch:**
- What underlying gap produced both? (Missing helper, missing lint rule, missing type guard, missing test.)
- Fix the root cause as one commit.
- Save to memory (`feedback` type, include "Why" line citing the repeats) so future PRs don't trip it.

Patterns across PRs go to memory regardless.

---

## Step 5 — PO acceptance gate

Automated reviewers check code quality. The PO gate checks whether the deliverable achieves the plan's goal. These are different — both are required.

**Goal alignment:**
- Does the diff actually move the plan's North Star, or a proxy?
- Can you walk the user journey this phase enables and observe the expected outcome?
- Does the "plain language done" from the AC document hold end-to-end?

**AC gate check (hard):**
- Go through each must-pass AC gate from the phase contract.
- For code-verifiable gates: confirmed in the diff?
- For metric/E2E gates: have those checks been run?

**Advisory expert requirements (hard):**
- List every advisory requirement that applies to this phase.
- Is each one genuinely present — not technically satisfied but actually implemented?
- For **negative-constraint requirements** (things the implementation must NOT do), verify
  the forbidden behavior is absent — not just that the related feature exists. Example:
  "never block articles on old topics" means confirming the date filter is applied to the
  comparison corpus, not to the new article's topic. Presence of a date filter is not enough
  — confirm it filters the right thing.
- Would the advisory expert approve if they saw the full implementation?

**Drift check:**
- Any quiet scope changes — renamed fields, swapped vendors, adjusted formulas — not in the plan?

**Verdict:**
- **ACCEPTED** → all gates pass, goal aligned, no drift. Proceed to merge request.
- **NEEDS FIX** → dispatch the right domain expert with a precise brief (per `phases-execution` failure protocol). Not a generic retry.
- **ESCALATE** → problem is deeper than an implementation gap. Surface with diagnosis + options.

---

## Step 6 — Push and re-trigger

```bash
git push origin <branch>
gh pr comment <PR> --body "@codex_review"
```

Then wakeup at ~90s. Repeat steps 3–5 until all exit criteria pass.

Re-trigger with the reviewer's trigger phrase (default: `@codex_review`).

---

## Anti-loops

- **Hard cap: 5 iterations.** Still finding new things after 5 fix-commits → escalate. Either split the PR or route to `plan-with-review`.
- **3 iterations of B-only comments.** Ask the user: merge as-is + spawn polish task, or keep going?
- **Same pattern 3 times after a root-cause attempt.** Stop patching — the area needs a real refactor. Escalate.
- **B alone never blocks merge.** Aesthetic-only = ship + spawn task.

---

## Merge

The **user merges** — you never merge without explicit greenlight. When all exit criteria pass, ask for greenlight and provide the exact merge command for them to run.

---

## Heuristics

- **Batch fixes.** All comments in one commit, not one per comment.
- **Re-trigger immediately after push.** The reviewer and CI run in parallel — don't wait for CI first.
- **Log patterns from iteration 1.** Second hit is the trigger; the log is the record.
- **AC check in step 0.** Catching an AC gap locally before the reviewer runs saves a full round-trip.

---

## Why this skill exists

PR #15 R1 nearly shipped a `current_user` SECURITY DEFINER bug that would have allowed any user to mutate pipeline columns — automated review caught it. PR #18 was declared "ready to merge" before any reviewer had run. Same null-check and RLS bugs kept appearing across PRs because fixes were applied comment-by-comment without root-causing.

This skill closes both loops: enforces exit criteria including the PO gate before merge, and turns the review queue into a learning signal so the same comment isn't written twice.
