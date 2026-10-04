---
name: brain-lite
description: Keeps a small project brain in brain/ (architecture, design decisions, gotchas) so the agent never has to re-read the whole codebase to understand it. Use whenever a task touches architecture or design, asks "why did we...", makes or changes a decision, or hits a non-obvious trap or setup step worth recording, and whenever a project has no brain yet. Skip for small edits and routine fixes.
license: MIT
metadata:
  version: "0.1.0"
  adapted-from: "skills/brain in this repo"
---

# Brain (lite)

`brain/` stores what the code cannot say: why things are the way they are, constraints, and traps. Anything re-derivable from code or git in about a minute does not belong in it.

## Layout

```
brain/
  INDEX.md          one line per file: path — what it holds — read when …
  architecture.md   components, data flow, what owns what
  design.md         UI/UX or API rules and constraints
  gotchas.md        how to run/test/deploy, env var names, non-obvious traps
  decisions/NNNN-topic.md   one decision per file; superseded ones move to decisions/archive/
```

Create a file only when it has real content. Templates are in `references/templates.md`; read it only when creating a file.

## Reading: lazy by default

1. Small edit, typo, or a task inside a file you are already reading: skip the brain.
2. Otherwise read `brain/INDEX.md` only, then open a file only if its "read when" matches the task. Never read the whole brain. For decisions, `ls brain/decisions` (titles are in filenames) and open only the relevant ones.
3. Entries are claims, not facts. Each file's `covers:` lists the paths it describes. If a covered path is gone or clearly changed, tell the user the entry looks stale instead of relying on it.
4. `proposed` entries are context, not rules. Archived decisions are history.

## Writing: only on these events

A decision is made or changed, a constraint is set, a non-obvious trap is found, or a run/test/deploy step is learned. Never write session logs or progress notes (git has them).

- Read a file before editing it. Edit in place; do not append duplicates.
- Name paths, do not paste code.
- Never rewrite an active decision. Write a new one with `supersedes: NNNN`, set the old one to `status: superseded` plus `superseded_by`, and move it to `decisions/archive/`. Never delete decisions.
- When you check an entry against the code and it still holds, update its `verified:` date.
- Adding, renaming or removing a file means updating `INDEX.md` in the same change.
- Propose to the user before structural changes (new top-level file, split, merge, delete). Ordinary entries: just write.
- Write for a reader new to programming: plain words, define a term the first time, explain the why. If the why is unknown, write `why: unknown — ask the owner`. Never invent a rationale.
- Never write secrets (keys, tokens, passwords, `.env` values). Env var names only.
- Commit brain edits together with the change that caused them.

## Budgets

`INDEX.md` ≤60 lines, other files ≤150, a decision ≤20 (aim 5–15). At the limit, split or prune before adding. After editing the brain, run `python <this skill's folder>/scripts/brain_lint.py .` from the project root. Run it, do not read it. Fix errors; warnings are judgment calls.

## No brain yet

1. Start with `INDEX.md` and `gotchas.md`: the commands to run, test and deploy, and env var names.
2. Draft `architecture.md` from the README, package manifest, top-level folders and `git log --oneline -20`. Show the draft to the user before saving anything inferred from code. Set `verified:` only for what you checked.
3. Add this plain-text pointer to the project's CLAUDE.md (not an `@import`, which loads the file every session): `Architecture, design decisions and gotchas live in brain/. For non-trivial tasks read brain/INDEX.md first.`
4. Record decisions as they happen; do not back-fill history.

## Failure modes

- **Museum:** notes nobody uses. If tasks never touch a note, question it.
- **Collector:** notes holding no decision, constraint or trap. Prune them, with the user's OK.
- **Invented why:** confident but made-up rationale.
- **Overwritten history:** silently changing an accepted decision.
- **Load everything:** reading the whole brain "to be safe".
