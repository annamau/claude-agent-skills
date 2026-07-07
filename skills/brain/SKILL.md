---
name: brain
description: >-
  Owns the repo-based company brain (a linked-markdown vault at brain/, plain .md files) end to end, routed internally by SCALE. Use at the START of any project-strategy work session to recall current state (thesis, distance-to-MVP, what's in flight, active hawk boards) BEFORE acting; whenever a finding, decision, accomplishment, golden case, concept, postmortem, or checklist change needs filing; when the user says "update the brain / file this / what does the brain say about X / run a maintenance pass / ingest this"; AND for vault-scale work — "bootstrap a brain/vault for this project", "ingest these docs/memories into the brain", "garden the brain", "health check the vault", "brain report", or evolving the taxonomy (add/rename a domain, change the frontmatter law). NOT for code-coupled docs (those stay in docs/ and the code; the brain links to them via repo_link) and NOT for writing live hawk boards (the hawk owns those; the brain archives them when closed).
license: MIT
metadata:
  author: annamau
  version: "1.0.0"
---

# Brain — the company's long-term memory, end to end

The brain at **`brain/` in the repo root** is the company brain: what the project is, the goal, the strategy, the investigation evidence, the golden cases, the living checklist-to-MVP, the log of what we decided and shipped — plus the **execution layer**: hawk workflow boards and agent-session postmortems. This one skill is its whole lifecycle: recall + single-item filing (daily in/out) AND bootstrap / bulk ingest / deep garden / evolve (whole-vault scale). It routes internally by scale — you don't pick a skill by size; for a single finding use **W-FILE-FINDING**, for a bulk campaign use **W-INGEST-CAMPAIGN**.

The brain is plain markdown managed with Read/Glob/Grep/Write/Edit — no external app or MCP required (Obsidian can still open `brain/` directly if you like wikilink navigation).

**The split-source-of-truth law (never violate):** the brain holds **STRATEGY + EXECUTION STATE** (durable, years-lived knowledge; live workflow boards). **CODE-COUPLED** detail (anything tied to `file:line`, migrations, raw data dumps, code audits) stays in **`docs/` and the code** — the brain carries a *summary note + a `repo_link`*, never a duplicate. If a note would restate `file:line` content, it links instead.

The brain's own operating rules live at `brain/00_Meta/` (Taxonomy, Naming-Conventions, Frontmatter-Standard, Tag-Dictionary, Templates/). **Read `00_Meta/` for the live law before any structural action** — taxonomy can evolve without re-editing this skill.

**Governing principles** (a brain is judged by retrieval, not size — optimize for the reader-agent six months out): **atomic notes** (~50-second reads, one claim/concept/decision per note; a source with ten ideas becomes ten notes); **current-truth-at-top** (open with the one-paragraph current truth, history/evidence below); **MOCs emerge bottom-up** (mint at ~15–20 related notes; domain MOCs are the exception — the law's navigation floor); **supersede, never overwrite** (accepted decisions/findings are immutable; reality changes → new note with `supersedes:`, old archived with `superseded_by:`); **bi-temporal freshness** (`updated:` = when text changed; **`verified:`** = when a human/hawk last confirmed it true — staleness is measured on `verified:`, not `updated:`); **single-writer** (agents propose, one accountable actor writes — this skill for notes, the hawk for boards; structural changes are proposed to the user first); **no live dedupe** (dedupe-on-write is a per-note Grep; deep merge/prune runs as a scheduled pass).

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

`Home.md` (dashboard) · `00_Meta/` (the law) · `10_Product/` · `20_Goals-and-Strategy/` · `30_Investigation/` · `40_Golden-Cases/` (depth-3 exception: `<category>/<slug>.md`) · `50_Roadmap-and-Checklist/` · `55_Execution/` (depth-3 exception: `boards/<workflow-slug>/…`) · `60_Decisions-and-Accomplishments/` · `70_Concepts/` · `80_References/` · `90_Archive/`. Every note lands in exactly one domain folder and links **up to its `_MOC.md`**. These are the brain's **default** domains; a project may name its own set in `00_Meta/Taxonomy.md` (W-BOOTSTRAP derives 5–8 domains from the org, not from another brain).

**`55_Execution/` — the hawk layer (special ownership rules):**
- `boards/<workflow-slug>/` (BOARD.md · LOCKS.md · DECISIONS.md) — **written by the hawk running that workflow, not by this skill.** Here we read boards (for W-RECALL), maintain their links, and **archive a board once its status is `closed`** (move the folder to `90_Archive/boards/`, leave a link from the 55 MOC). LOCKS.md is gitignored runtime state — never archive or repair it.
- `postmortems/YYYY-MM-DD-<slug>.md` — agent-session postmortems (type `postmortem`). Enforce: every postmortem names a landed harness fix; ones that don't get flagged in maintenance as incomplete.

## The rules it enforces (the law)

1. **Repo-vs-brain split** — code-coupled facts get a SUMMARY + `repo_link`, never a duplicate.
2. **Taxonomy** — one domain folder per note; max depth 2 (golden-cases and 55/boards depth-3 only); no new top-level folder without updating `00_Meta/Taxonomy.md`.
3. **Naming** — per `00_Meta/Naming-Conventions.md` (Title-Case singletons; slug for golden/memory; date-suffix only on versioned artifacts; no spaces).
4. **Frontmatter** — every note has the required keys with a valid `type` + `status` enum; repair on sight.
5. **Link hygiene** — every leaf links up to its MOC and across to dependencies; no broken `[[wikilinks]]`; no MOC-orphans.
6. **Dedupe** — `Grep` the title/claim before creating; if a near-duplicate exists, UPDATE it (and `supersedes`/archive the old) rather than fork a second truth.
7. **Archive-not-delete** — superseded knowledge moves to `90_Archive/` with `superseded_by` set; live knowledge is never hard-deleted.
8. **Checklist integrity** — a checklist item flipping to `done` MUST mint an `accomplishment` note (the how/why + evidence `repo_link`) and link it; the `Checklist-to-MVP` dashboard is re-rendered from the item notes; distance-to-MVP = count of unmet `MVP-Definition` exit conditions.
9. **Board ownership** — live boards belong to their hawk; here we only read, link, and archive-on-close. Postmortems without a landed harness fix are flagged, not silently accepted.

## The workflows (named playbooks — daily to heavy)

### W-RECALL — recall current state (run FIRST, every session, mandatory)
Parallel-`Read` the keystone notes (e.g. `brain/Home.md`, `brain/30_Investigation/Thesis.md`, `brain/50_Roadmap-and-Checklist/Checklist-to-MVP.md`, `brain/50_Roadmap-and-Checklist/MVP-Definition.md` — a project may have differently-named keystone notes) → `Grep '^status: (doing|blocked)'` across `brain/` → `Glob brain/55_Execution/boards/*/BOARD.md` and read any with `status: active` → report: the current thesis, distance-to-MVP (count of unmet exit conditions), what's in flight, what's blocked, **which hawk workflows are active and what files they own**. **Do this before acting on any project-strategy work** so you build on the brain, not from scratch — and so a new workflow doesn't claim files an active board already owns.

### W-FILE-FINDING — file a new finding
`Grep` for dups → pick the `finding` template (`00_Meta/Templates/`) → `Write` into `30_Investigation/{waves|canary|forensics}/` with `source`/`repo_link` → `Edit` `30_Investigation/_MOC.md` timeline + link from any goal/checklist-item it changes → if it spawns work, create a `checklist-item` and add it to the dashboard.

### W-RECORD-WIN — record an accomplishment
`Edit` the `checklist-item` frontmatter `status: done` → `Write` an `accomplishment` note (how/why/evidence `repo_link`) in `60_Decisions-and-Accomplishments/accomplishments/` → cross-link item↔accomplishment → re-render the `Checklist-to-MVP` Done section → `Edit` Home's pulse + distance-to-MVP.

### W-ANSWER — "what does the brain say about X"
`Grep` X across `brain/` → `Read` the top hits → synthesize a cited answer with `[[wikilinks]]`, flagging any `status: superseded` hits as stale.

### W-INGEST — ingest one repo doc or memory file
Read the source → classify: durable strategy → SUMMARY (or full copy if no code coupling); code-coupled → SUMMARY + `repo_link`; stale → no-ingest (flag in `80_References/Memory-Index.md`) → `Grep` dedupe → write in the mapped folder with `source` + `repo_link` → link from its MOC. For memory files apply the test **"would a new hire need this to understand the company's strategy in a year?"** — yes → brain note (collapse clusters into one `decision`/`accomplishment`); "only matters while touching that code path" → stays in memory.

### W-MAINTAIN — light structure-maintenance pass (end of session / on request)
The per-session sweep — mechanical hygiene on what changed this session (contrast W-GARDEN, the deep, scheduled, numeric-gated pass). `git log -- brain/` + `Glob` inventory vs taxonomy → check changed/new notes against the rules via `Grep` (missing frontmatter, MOC-orphans, dup titles, broken `[[links]]`) → repair via `Edit` → refresh every `_MOC.md` + Home's "recently changed" → archive anything now `superseded` → **archive closed boards** (`status: closed` → `90_Archive/boards/`) → flag postmortems missing a landed harness fix. Output a short maintenance report.

### W-BOOTSTRAP — build a brain from zero (any repo)
1. **Derive the domains from the org, don't copy another brain's.** Interview the repo + user: what is the product, what evidence exists, what decisions recur, what does "done" mean here? 5–8 domains max, numbered with gaps (`10_`, `20_`, …) so new domains slot in later.
2. **Scaffold the minimum law first:** `Home.md` (dashboard with a "pulse" section), `00_Meta/` (Taxonomy with the split-source-of-truth contract + ingestion map, Frontmatter-Standard with controlled `type`/`status` enums incl. `verified:`, Naming-Conventions, one template per note type), and a `_MOC.md` per domain. Nothing else — content earns structure, not vice versa.
3. **Encode the split-source-of-truth contract on day one:** strategy lives in the brain; code-coupled detail (`file:line`, migrations, raw data) stays in the repo with the brain holding a SUMMARY + `repo_link`. Splitting by volatility is what keeps the brain trustworthy for years.
4. **Add the execution layer** (`55_Execution/`-style: `boards/` + `postmortems/`) if agents will run supervised workflows in this repo; gitignore the lock ledgers.
5. Seed with a first ingestion campaign (below), then hand steady-state to W-FILE-FINDING / W-MAINTAIN.

### W-INGEST-CAMPAIGN — bulk ingestion of a source set
For waves of material (repo docs, memory files, transcripts, research reports):
1. **Map before writing.** Build an ingestion table (source → target folder → note type → disposition: FULL COPY only if pure strategy / SUMMARY+`repo_link` if code-coupled / NO-INGEST if stale or raw data). Show it to the user if the set is large or anything gets dropped.
2. **The new-hire test** decides borderline cases: "would a new hire need this to understand the company's strategy in a year?" Yes → note. "Only matters while touching that code path" → stays out, referenced.
3. **Batch and link as you go:** per batch — Grep-dedupe, write atomically (atomic-notes principle), link each note up to its MOC and across to dependencies immediately. A linking debt at campaign end never gets paid.
4. **Close the campaign:** refresh affected MOCs and Home's pulse, re-run the census (W-REPORT), and record the campaign as a `decision`/`accomplishment` note with the ingestion map as evidence.

### W-GARDEN — the deep gardening pass (the health engineer)
Cadence: **monthly** under ~500 notes, **weekly** above; always after a large campaign. (W-MAINTAIN stays the light per-session pass; this is the deep numeric-gated one.) A pass computes the scorecard, fixes what's mechanical, and PROPOSES what's structural:

| Health gate | Target | Action on breach |
|---|---|---|
| Frontmatter compliance | 100% valid type/status enums | repair on sight |
| Broken `[[wikilinks]]` | 0 | fix or remove |
| Strategic orphans (no inbound MOC link) | 0 (transient notes exempt) | link or archive |
| Tag hygiene | unique tags / notes **< 0.15** | consolidate vocabulary (>0.3 = chaos) |
| MOC sprawl | MOCs / content notes **< 0.1** | merge MOCs (>0.2 = crisis) |
| Freshness (strategy notes) | `verified:` within **6 months** | re-verify + stamp, or supersede/archive |
| Collector's fallacy | 0 notes with zero downstream links AND zero edits since creation | synthesize into a real note or drop |
| MOC emergence | topic with ~15–20 unindexed related notes | propose a new MOC |
| Postmortem integrity | every postmortem names a LANDED harness fix | flag as incomplete on the board/MOC |
| Supersession hygiene | no two live notes claiming the same truth | merge; loser to archive with `superseded_by` |

Finish every pass by updating Home: pulse, "recently changed" (from `git log -- brain/`), and a one-table **health scorecard** so drift is visible between passes. Mechanical fixes: just do them. Structural moves (folder changes, mass archives, MOC merges): propose to the user first — agents propose, humans approve.

### W-EVOLVE — changing the law itself
Adding a domain, a note type, a status, or renaming folders touches the brain's constitution. Do it as one atomic change-set, never piecemeal: update `Taxonomy.md` (tree + purpose table + invariants) AND `Frontmatter-Standard.md` (enums) AND `00_Meta/Templates/` AND `Home.md` navigation in the same pass, with a dated note in the taxonomy explaining why. A law change without all four updated creates two versions of the law — worse than no change.

### W-REPORT — "how is the brain doing?"
On demand: census per domain (note counts, newest `updated:`), the W-GARDEN scorecard computed read-only, top 3 risks, and distance-to-target for anything mid-campaign. Deliver as chat summary; write it into Home's health section only if a garden pass ran.

## Anti-patterns (each with its test)
- **Museum vault** — elaborate taxonomy, no output. Test: are decisions/articles/plans actually citing brain notes? The scorecard that matters most is output, not structure.
- **Collector's fallacy** — clipping without synthesis. Test: zero-downstream-link notes accumulating.
- **Top-down MOC scaffolding** — index pages for content that doesn't exist yet. Test: MOCs with <5 links outside the domain floor.
- **Tag explosion / over-foldering** — taxonomy as procrastination. Tests: tag ratio >0.15; folders deeper than the law allows.
- **Overwrite instead of supersede** — silently rewriting an accepted decision. Test: git diff shows semantic reversal without a `supersedes` chain.
- **Agent-writes-without-gate** — bulk structural changes landing unproposed. Test: mass moves in git history with no user approval recorded.
- **Staleness by `updated:`** — treating untouched-but-true notes as rot, or touched-but-wrong notes as fresh. Measure on `verified:`.

## Done means
A brain action is done when: the note(s) are in the right folder with valid frontmatter, linked up to their MOC and across to dependencies; no broken links or duplicate truths were introduced; for a completed checklist item — an accomplishment note exists and the dashboard + distance-to-MVP reflect it; for a maintenance pass — closed boards are archived and incomplete postmortems flagged; for a garden pass — the health scorecard is computed and visible on Home; for a law change — `00_Meta/` still has exactly one version; structural changes were user-approved; and the pass itself is traceable (git history + a pulse line).
