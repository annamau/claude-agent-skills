---
name: vault-librarian
description: A repo-based company brain (linked-markdown vault) librarian — the long-term-memory manager for the company brain, which lives IN THE REPO at brain/ (plain .md files). Use at the START of any project-strategy work session to recall current state (thesis, distance-to-MVP, what's in flight, active hawk boards) BEFORE acting; and whenever a finding, decision, accomplishment, golden case, concept, postmortem, or checklist change needs filing, when the user says "update the vault / update the brain / file this / what does the brain say about X / run a maintenance pass / ingest this", or to ingest durable strategy from repo docs or auto-memory. NOT for code-coupled docs (those stay in docs/ and the code; the brain links to them) and NOT for writing live hawk boards (the hawk owns those; the librarian archives them when closed).
license: MIT
metadata:
  author: annamau
  version: "2.0.0"
---

# Vault Librarian — the company's long-term memory

The brain at **`brain/` in the repo root** is the company brain: what the project is, the goal, the strategy, the investigation evidence, the golden cases, the living checklist-to-MVP, the log of what we decided and shipped — and, since v2, the **execution layer**: hawk workflow boards and agent-session postmortems. This skill is the **in/out manager** for it.

The brain is plain markdown managed with Read/Glob/Grep/Write/Edit — no external app or MCP required (Obsidian can still open `brain/` directly if you like wikilink navigation).

**The split-source-of-truth law (never violate):** the brain holds **STRATEGY + EXECUTION STATE** (durable, years-lived knowledge; live workflow boards). **CODE-COUPLED** detail (anything tied to `file:line`, migrations, raw data dumps, code audits) stays in **`docs/` and the code** — the brain carries a *summary note + a `repo_link`*, never a duplicate. If a note would restate `file:line` content, it links instead.

The brain's own operating rules live at `brain/00_Meta/` (Taxonomy, Naming-Conventions, Frontmatter-Standard, Tag-Dictionary, Templates/). **Read `00_Meta/` for the live law before a structural action** — taxonomy can evolve without re-editing this skill.

**Vault-SCALE work is not this skill:** bootstrapping a brand-new brain, bulk ingestion campaigns, deep gardening/health passes with numeric gates, and taxonomy evolution belong to the `brain-builder` skill. This skill is the note-scale law + daily in/out; W-MAINTAIN here is the light per-session pass, not the deep garden.

## The brain is plain files — tool mapping

| Operation | Tool |
|---|---|
| Read one note | `Read brain/<folder>/<Note>.md` |
| Read several (Home + Thesis + Checklist) | parallel `Read` calls in one message |
| Keyword search | `Grep` over `brain/` (`-i`, `glob: *.md`) |
| Frontmatter/tag/status search | `Grep` pattern like `^status: doing` with `glob: brain/**/*.md` |
| Inventory / find a note by name | `Glob brain/**/*.md` |
| Create a note | `Write brain/<folder>/<Note>.md` (full note incl. frontmatter) |
| Surgical edit (preferred) | `Edit` — flip a checklist status, patch a MOC line, repair a frontmatter key |
| Recent changes | `Bash: git log --oneline -15 -- brain/` (or `ls -t` for uncommitted) |
| Archive-move | `Bash: git mv brain/<path> brain/90_Archive/<path>` (preserves history) |

- **Read before write, always.** Never Edit a note you haven't Read this session.
- Wikilinks `[[Note-Title]]` resolve by filename — verify targets exist with `Glob` before linking; a broken link is a filing bug.
- Brain edits ride normal git flow: they get committed with the work that produced them (the hawk's board commits, a session's finding commits). Don't create a separate commit ceremony for the brain.

## The taxonomy (10 domain folders, max depth 2)

`Home.md` (dashboard) · `00_Meta/` (the law) · `10_Product/` · `20_Goals-and-Strategy/` · `30_Investigation/` · `40_Golden-Cases/` (depth-3 exception: `<category>/<slug>.md`) · `50_Roadmap-and-Checklist/` · `55_Execution/` (depth-3 exception: `boards/<workflow-slug>/…`) · `60_Decisions-and-Accomplishments/` · `70_Concepts/` · `80_References/` · `90_Archive/`. Every note lands in exactly one domain folder and links **up to its `_MOC.md`**. These are the brain's default domains; a project may name its own set in `00_Meta/Taxonomy.md`.

**`55_Execution/` — the hawk layer (special ownership rules):**
- `boards/<workflow-slug>/` (BOARD.md · LOCKS.md · DECISIONS.md) — **written by the hawk running that workflow, not by the librarian.** The librarian reads boards (for W-RECALL), maintains their links, and **archives a board once its status is `closed`** (move the folder to `90_Archive/boards/`, leave a link from the 55 MOC). LOCKS.md is gitignored runtime state — never archive or repair it.
- `postmortems/YYYY-MM-DD-<slug>.md` — agent-session postmortems (type `postmortem`). Librarian enforces: every postmortem names a landed harness fix; ones that don't get flagged in maintenance as incomplete.

## The rules it enforces (the law)

1. **Repo-vs-brain split** — code-coupled facts get a SUMMARY + `repo_link`, never a duplicate.
2. **Taxonomy** — one domain folder per note; max depth 2 (golden-cases and 55/boards depth-3 only); no new top-level folder without updating `00_Meta/Taxonomy.md`.
3. **Naming** — per `00_Meta/Naming-Conventions.md` (Title-Case singletons; slug for golden/memory; date-suffix only on versioned artifacts; no spaces).
4. **Frontmatter** — every note has the required keys with a valid `type` + `status` enum; repair on sight.
5. **Link hygiene** — every leaf links up to its MOC and across to dependencies; no broken `[[wikilinks]]`; no MOC-orphans.
6. **Dedupe** — `Grep` the title/claim before creating; if a near-duplicate exists, UPDATE it (and `supersedes`/archive the old) rather than fork a second truth.
7. **Archive-not-delete** — superseded knowledge moves to `90_Archive/` with `superseded_by` set; live knowledge is never hard-deleted.
8. **Checklist integrity** — a checklist item flipping to `done` MUST mint an `accomplishment` note (the how/why + evidence `repo_link`) and link it; the `Checklist-to-MVP` dashboard is re-rendered from the item notes; distance-to-MVP = count of unmet `MVP-Definition` exit conditions.
9. **Board ownership** — live boards belong to their hawk; the librarian only reads, links, and archives-on-close. Postmortems without a landed harness fix are flagged, not silently accepted.

## The workflows (named playbooks)

### W-RECALL — recall current state (run FIRST, every session, mandatory)
Parallel-`Read` the keystone notes (e.g. `brain/Home.md`, `brain/30_Investigation/Thesis.md`, `brain/50_Roadmap-and-Checklist/Checklist-to-MVP.md`, `brain/50_Roadmap-and-Checklist/MVP-Definition.md` — a project may have differently-named keystone notes) → `Grep '^status: (doing|blocked)'` across `brain/` → `Glob brain/55_Execution/boards/*/BOARD.md` and read any with `status: active` → report: the current thesis, distance-to-MVP (count of unmet exit conditions), what's in flight, what's blocked, **which hawk workflows are active and what files they own**. **Do this before acting on any project-strategy work** so you build on the brain, not from scratch — and so a new workflow doesn't claim files an active board already owns.

### W-FILE-FINDING — file a new finding
`Grep` for dups → pick the `finding` template (`00_Meta/Templates/`) → `Write` into `30_Investigation/{waves|canary|forensics}/` with `source`/`repo_link` → `Edit` `30_Investigation/_MOC.md` timeline + link from any goal/checklist-item it changes → if it spawns work, create a `checklist-item` and add it to the dashboard.

### W-RECORD-WIN — record an accomplishment
`Edit` the `checklist-item` frontmatter `status: done` → `Write` an `accomplishment` note (how/why/evidence `repo_link`) in `60_Decisions-and-Accomplishments/accomplishments/` → cross-link item↔accomplishment → re-render the `Checklist-to-MVP` Done section → `Edit` Home's pulse + distance-to-MVP.

### W-MAINTAIN — structure-maintenance pass (end of session / on request)
`git log -- brain/` + `Glob` inventory vs taxonomy → check changed/new notes against the rules via `Grep` (missing frontmatter, MOC-orphans, dup titles, broken `[[links]]`) → repair via `Edit` → refresh every `_MOC.md` + Home's "recently changed" → archive anything now `superseded` → **archive closed boards** (`status: closed` → `90_Archive/boards/`) → flag postmortems missing a landed harness fix. Output a short maintenance report.

### W-INGEST — ingest a repo doc or memory file
Read the source → classify: durable strategy → SUMMARY (or full copy if no code coupling); code-coupled → SUMMARY + `repo_link`; stale → no-ingest (flag in `80_References/Memory-Index.md`) → `Grep` dedupe → write in the mapped folder with `source` + `repo_link` → link from its MOC. For memory files apply the test **"would a new hire need this to understand the company's strategy in a year?"** — yes → brain note (collapse clusters into one `decision`/`accomplishment`); "only matters while touching that code path" → stays in memory.

### W-ANSWER — "what does the brain say about X"
`Grep` X across `brain/` → `Read` the top hits → synthesize a cited answer with `[[wikilinks]]`, flagging any `status: superseded` hits as stale.

## Done means
A brain action is done when: the note(s) are in the right folder with valid frontmatter, linked up to their MOC and across to dependencies; no broken links or duplicate truths were introduced; for a completed checklist item — an accomplishment note exists and the dashboard + distance-to-MVP reflect it; and for a maintenance pass — closed boards are archived and incomplete postmortems flagged.
