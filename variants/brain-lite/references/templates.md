# Brain templates

Read only when creating a file. Frontmatter is the only required structure. `covers:` lists the repo paths the entry describes (the lint script checks they exist). Dates are `YYYY-MM-DD`.

## INDEX.md

```
# Brain index
- architecture.md — components and data flow — read when changing how parts connect
- gotchas.md — run/test/deploy, env var names, traps — read when setup or a build/test fails
- decisions/ — one file per live decision, `NNNN-topic.md`; `ls` to scan — read when changing something that looks like a past choice
```

One line per file. Keep it under 60 lines. Do not list individual decisions.

## architecture.md, design.md, gotchas.md

```
---
verified: 2026-10-03
covers: [src/, package.json]
---
# Architecture
Current truth first, in a short paragraph. Then details.

## <component or topic>
What it does, what owns it, what it must not do. Name files, do not paste code.
```

For `gotchas.md`, use one bullet per trap: symptom, cause, fix. Env var names only, never values.

## decisions/NNNN-topic.md

```
---
status: active          # active | proposed (superseded ones live in archive/)
date: 2026-10-03
verified: 2026-10-03
covers: [src/queue/]
supersedes:             # id of the decision this replaces, e.g. 0003
superseded_by:          # filled in when this one is replaced
---
# 0007 Use a queue instead of cron
**Decision:** one sentence.
**Why:** plain words; or `unknown — ask the owner`.
**Rejected:** option — reason.
**Revisit if:** the condition that would change this.
```

Aim for 5–15 lines. To supersede: write the new decision with `supersedes: 0007`, then set the old file to `status: superseded` and `superseded_by: 0012`, and move it to `decisions/archive/`.
