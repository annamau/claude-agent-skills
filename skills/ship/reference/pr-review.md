# Cross-model PR review

For work that ships through a pull request, a second reviewer from a different
model family reviews the diff on the PR itself. Gate 7 in the table is a local
fresh-context reviewer; this is the same idea at PR scope, with a model trained
by someone else.

Configure `{{REPO}}` (the `owner/repo` slug) and `{{REVIEW_BOT_LOGIN}}` in a
local adapter file. Skip this file entirely if the work does not go through a PR.

## Find the bot's real login first

This is the step that silently breaks everything if skipped.

```bash
gh api repos/{{REPO}}/issues/<any-pr-with-a-review>/comments \
  --jq '[.[] | select(.user.type == "Bot")] | .[].user.login'
```

**The login carries a `[bot]` suffix.** Filter with `startswith()`, never
equality — an equality match returns empty forever, and a polling loop built on
it waits indefinitely for comments that are already there. Verify the exact
login from a real review on your repo rather than assuming the app's slug.

## Trigger

```bash
gh pr comment <PR> --body "@codex_review"
```

Re-trigger after every push. The reviewer reviews the commit snapshot as of the
request, so a review from before your last push describes code that no longer
exists.

## Collect findings

```bash
gh api repos/{{REPO}}/pulls/<PR>/comments \
  --jq '[.[] | select(.user.login | startswith("{{REVIEW_BOT_LOGIN}}"))]
        | sort_by(.created_at) | .[] | {id, path, line, body, created_at}'
```

Inline comments carry the substance. A top-level "approved" with no inline
comments means proceed; silence with no review posted means the trigger did not
land — check the login filter before concluding the diff is clean.

## Loop, with a cap

Cap at 5 rounds. Track the count in a file, not in your head:

```bash
echo $(( $(cat .claude/review-round 2>/dev/null || echo 0) + 1 )) > .claude/review-round
```

A count kept in conversation dies at compaction, which is how a 5-round cap
quietly becomes a 9-round loop. Hitting the cap means the diff needs splitting
or the design needs revisiting — not a sixth round.

## Repeats are a signal about the codebase

The same finding appearing in two different PRs is not two review findings. It
is one missing guardrail:

- What gap produced both? A missing helper, lint rule, type guard, or test.
- Fix that gap in its own commit.
- Record it, with the two occurrences cited, so the next PR cannot repeat it.

This is the same move as the session-health hook: convert a recurring failure
into a mechanical check, once, instead of catching it by hand every time.

## Before merging

Ask the user. Merging is theirs to authorize — the hook denies `gh pr merge`
for exactly this reason.

If the PR is part of a stack, retarget dependent PRs to the base branch
*before* merging. Merging with `--delete-branch` closes every PR still pointing
at the deleted branch.
