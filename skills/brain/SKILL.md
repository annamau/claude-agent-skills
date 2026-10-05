---
name: brain
description: >-
  Recall and file project knowledge in the repo's brain/ vault (status, strategy, decisions, findings, golden cases, checklist-to-MVP, boards, postmortems); writes go through the brain-librarian subagent. Use at the start of project-strategy work, when a decision, finding or accomplishment needs filing, when the user says "update the brain", "file this", "ingest this" or "what does the brain say about X", and for vault-scale work (bootstrap, garden, health check, taxonomy change). Not for code-coupled docs or live hawk boards.
license: MIT
metadata:
  author: annamau
  version: "2.1.0"
---

# Brain

`brain/` (repo root) is the project's long-term memory: what the project is, the strategy, the evidence, the decisions and what shipped. It is plain markdown, edited with Read/Glob/Grep/Write/Edit. Its own rules live in `brain/00_Meta/` (Taxonomy, Frontmatter-Standard, Naming-Conventions, Templates); read the relevant one before any structural change, since it overrides the defaults here.

**Split-source law.** The brain holds strategy and execution state. Code-coupled detail (`file:line`, migrations, audits) and raw artifacts (data dumps, logs, archives, eval corpora, screenshots) stay in the repo outside `brain/`; the brain holds a short summary plus `repo_link`. A brain that stores raw output becomes slow to search and expensive to read.

## Two roles: lead reads, librarian writes

The **lead** (the main agent that owns the product) keeps its context for product work. The **`brain-librarian`** subagent (Sonnet; definition in this repo's `agents/brain-librarian.md`, installed in `~/.claude/agents/`) is the vault's only writer, so dedupe, linking, linting and search noise never enter the lead's context.

**The lead does:**
1. **Recall = read `brain/Status.md`** (the project's status file: goal, distance-to-MVP, features with state and next step, blocked, founder decisions, recently shipped). Fall back to `brain/Home.md` if there is no Status.md. Small edit or routine fix: skip the brain.
2. Read a specific note only when the task needs it, found by name (`Glob`) or by a cited link. For anything that needs searching, send an ANSWER request instead of grepping the vault yourself.
3. Decide what is true and what is done. The librarian decides where it goes.

**The lead sends the librarian** (`Agent` with `subagent_type: "brain-librarian"`, in the background):
- **FILE** at milestones: a decision made or changed, a finding, a feature done, a golden case, a postmortem with its harness fix. One request can carry several items. Per item: the claim in one to three sentences, the evidence (commit, test, `repo_link`) and related notes if known.
- **STATUS** when a feature's state, a blocker or the next step changes.
- **ANSWER** for "what does the brain say about X".
- **MAINTAIN** at the end of a session that changed product state; **GARDEN** on a schedule or when lint shows drift.

Batch items; never spawn one librarian per item. The reply is a receipt of at most 10 lines; do not ask for note bodies. Never write session logs or progress narration to the brain; git has them.

If the `brain-librarian` agent type is unavailable, spawn a general-purpose agent with model `sonnet` and the prompt "Act as the brain librarian defined in <this skill's folder>/../../agents/brain-librarian.md" plus the request.

## The rules the librarian enforces

- **Dedupe:** update the existing note instead of forking a second truth.
- **Atomic notes:** one claim or decision per note, current truth first, evidence below.
- **Supersede, never overwrite:** a new note with `supersedes:`; the old one becomes `status: superseded` with `superseded_by:` and moves to `90_Archive/`.
- **Valid notes:** required frontmatter per `00_Meta/Frontmatter-Standard.md`, a link up to the domain `_MOC.md`, and `[[links]]` that resolve.
- **Checklist completions:** a checklist item flipping to `done` mints an `accomplishment` note and updates Status.md.
- **Honest freshness:** `verified:` is bumped only when the claim was actually checked. Never invent a rationale, and never write secrets.
- **Approval first:** structural changes (new domain, folder move, mass archive, data moved out of `brain/`) are proposed to the user first.
- **Board ownership:** live boards in `55_Execution/boards/` belong to the agent running them; the librarian archives a board once it is `closed`.

## Workflows

The librarian runs these; steps are in `reference/workflows.md`, and it reads only the section it is running.

| Workflow | When |
|---|---|
| W-RECALL | lead, start of strategy work: read Status.md |
| W-ANSWER | librarian ANSWER request: scoped search, cited answer |
| W-FILE-FINDING | librarian FILE request: a new finding or decision |
| W-RECORD-WIN | librarian FILE request: a feature or checklist item done |
| W-INGEST | one doc or memory file to absorb |
| W-MAINTAIN | librarian, end of session: lint, fix, refresh MOCs, Status.md |
| W-BOOTSTRAP, W-INGEST-CAMPAIGN, W-GARDEN, W-EVOLVE, W-REPORT | vault-scale, occasional |

The full rule set, taxonomy defaults and anti-patterns (museum vault, collector's fallacy, monotonic growth, prose where a check belongs) are in `reference/law.md`. Read it for gardening, bootstrap or law changes, not for daily filing.

## Lint: run it, don't read it

After editing the brain, and at the start of any garden or health pass:

```
python3 <this skill's folder>/scripts/brain_lint.py <repo root>
```

It takes required keys and enums from `00_Meta/Frontmatter-Standard.md` and checks frontmatter, broken wikilinks, orphans, supersede hygiene, stale `verified:`, oversized notes, raw artifacts and data dumps inside `brain/`, leaked secrets, and `@import`s of the brain in CLAUDE.md. Output is bounded (counts plus a few examples; `--all` lists everything). Fix errors, treat warnings as judgment calls, and report data-dump findings to the user rather than moving data yourself.

## Budgets

- `Status.md` ≤ 60 lines and `Home.md` ≤ 120 lines (navigation only), because recall reads them.
- Notes ≤ 200 lines; split anything longer.
- A folder with hundreds of files is data, not knowledge: move it out of `brain/` and link to it.
- Point to the brain from CLAUDE.md in plain text (`Project status: brain/Status.md. Brain writes go through the brain-librarian subagent.`), never with `@brain/...`, which loads it into every session.

## Done means

Notes in the right folder with valid frontmatter, linked to their MOC, with no broken links or duplicate truths. Status.md reflects any change in feature state, blockers, distance-to-MVP or next steps. Lint shows no errors. The user approved any structural change.
