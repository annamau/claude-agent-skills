---
name: skill-audit
description: Audit a Claude Code skill for whether it will actually work — survives compaction, triggers correctly, enforces what it claims. Use when writing a new skill, reviewing an existing one, or when a skill "stops being followed" partway through a session.
when_to_use: Before publishing a skill, and whenever one seems to be ignored mid-session. Run the analyzer first; it answers most questions without reading anything.
license: MIT
---

# Skill audit

Most skill defects are arithmetic, not taste. Measure first.

```bash
python3 scripts/analyze_skill.py                 # all skills
python3 scripts/analyze_skill.py path/to/skill   # one, in detail
```

This reports token count against the compaction budget, where truncation
falls, frontmatter length, restated doctrine, and the ratio of lines naming a
check to lines exhorting effort. Read its output before forming an opinion.

## The failure that matters most

A skill enters the conversation once and is **never re-read**. After
auto-compaction only its **first ~5,000 tokens** come back. Everything past
that is gone, silently, at exactly the point a long session needs it.

So a skill written as a long ordered procedure fails in a specific way: the
early setup survives, the later gates disappear, and the session looks like
the model "stopped following the skill." It did not. The text is not there.

**A skill must be a set of standing rules that hold in any order, not a script
executed front to back.** If step 12 only makes sense after step 11, step 12
belongs in `reference/`, loaded at the moment it is needed.

## What to check

**Size.** Over 5,000 tokens, the analyzer reports which line gets cut and what
fraction is lost. Move detail to `reference/` and point at it. Under budget,
the whole skill is always present.

**Triggering.** `description` plus `when_to_use` truncate at 1,536 characters
combined. They exist to answer *should I invoke this now* — not to summarize
what the skill does. A description spending 1,500 characters describing
internal machinery has crowded out the trigger it was supposed to provide.

**Enforcement.** For every MUST, ALWAYS, and NEVER: what happens if the model
does it anyway? If the answer is "nothing," the rule is advisory no matter how
it is capitalized. Rules worth keeping are worth making mechanical:

| Rule shaped like | Becomes |
|---|---|
| never run X | `PreToolUse` hook denying X |
| always run Y before finishing | `Stop` hook running Y |
| never edit Z | `PreToolUse` deny on the path |
| stop after N attempts | a counter file plus a gate |

A hook holds whether or not the skill text is still in context. That is the
whole reason to prefer it.

**Repetition.** The analyzer counts restated doctrine. Saying a rule eleven
times does not make it stick — the model reads the skill once, so the second
through eleventh statements cost budget and change nothing. State it once,
then spend the budget on the check that enforces it.

**Exhortation versus signal.** "Be rigorous," "think hard," "do not skip this"
are instructions to try harder. They are what a skill reaches for when it has
no check to name. When the analyzer reports more exhortation than signal, the
fix is to name a command with a pass condition, not to phrase the plea better.

**Subagents.** Three uses are justified: isolating context, getting a review
from someone who did not write the code, and fanning out research. Named roles
and org charts are not a fourth. If a subagent owns no files and produces no
artifact, delete it and do the work inline.

## What the analyzer cannot tell you

It counts; it does not judge. After running it, read for:

- **Gates that cannot fail.** Any self-assessment where the honest answer is
  always available. "Confirm this is a real solution, not a patch" is not a
  gate — a model can always confirm it.
- **Ceremony formatted as measurement.** Numeric thresholds with no way to
  compute them read like signal and behave like vibes.
- **Rules the harness already enforces.** Delete them; they are noise.
- **Advice that was true of older models.** Reread with today's behavior in
  mind, not the behavior that prompted the rule.

## Verdicts

- **KEEP** — under budget, triggers cleanly, rules are enforced or genuinely
  advisory by choice.
- **COMPRESS** — right shape, too long. Move detail to `reference/`.
- **RESTRUCTURE** — a sequential procedure that cannot survive compaction, or
  mandates with no mechanism. Rewrite as standing rules plus hooks.
- **DELETE** — one step of another skill, or fully superseded.

## Before publishing

```bash
python3 scripts/analyze_skill.py            # exits non-zero on a breach
python3 scripts/test_analyze_skill.py       # the analyzer's own tests
```

Wire the first into CI. Both failures this repo shipped with — a skill losing
66% of itself to compaction, and a description 35 characters from silent
truncation — are caught by running it.
