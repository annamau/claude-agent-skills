# Workflows

Read only the section you are running.

## Daily

### W-RECALL — recall current state (start of strategy work)
Default: Read `brain/Home.md` and report from it. Go further only if Home is stale or the task needs it:

Full recall (only when asked, or Home is clearly stale): Parallel-`Read` the keystone notes (e.g. `brain/Home.md`, `brain/30_Investigation/Thesis.md`, `brain/50_Roadmap-and-Checklist/Checklist-to-MVP.md`, `brain/50_Roadmap-and-Checklist/MVP-Definition.md` — a project may have differently-named keystone notes) → `Grep -l '^status: (doing|blocked)'` (files only) across `brain/**/*.md` → `Glob brain/55_Execution/boards/*/BOARD.md` and read any with `status: active` → report: the current thesis, distance-to-MVP (count of unmet exit conditions), what's in flight, what's blocked, **which hawk workflows are active and what files they own**. **Do this before acting on any project-strategy work** so you build on the brain, not from scratch — and so a new workflow doesn't claim files an active board already owns.

### W-FILE-FINDING — file a new finding
`Grep` for dups → pick the `finding` template (`00_Meta/Templates/`) → `Write` into `30_Investigation/{waves|canary|forensics}/` with `source`/`repo_link` → `Edit` `30_Investigation/_MOC.md` timeline + link from any goal/checklist-item it changes → if it spawns work, create a `checklist-item` and add it to the dashboard.

### W-RECORD-WIN — record an accomplishment
`Edit` the `checklist-item` frontmatter `status: done` → `Write` an `accomplishment` note (how/why/evidence `repo_link`) in `60_Decisions-and-Accomplishments/accomplishments/` → cross-link item↔accomplishment → re-render the `Checklist-to-MVP` Done section → `Edit` Home's pulse + distance-to-MVP.

### W-ANSWER — "what does the brain say about X"
`Grep` X across `brain/` → `Read` the top hits → synthesize a cited answer with `[[wikilinks]]`, flagging any `status: superseded` hits as stale.

### W-INGEST — ingest one repo doc or memory file
Read the source → classify: durable strategy → SUMMARY (or full copy if no code coupling); code-coupled → SUMMARY + `repo_link`; stale → no-ingest (flag in `80_References/Memory-Index.md`) → `Grep` dedupe → write in the mapped folder with `source` + `repo_link` → link from its MOC. For memory files apply the test **"would a new hire need this to understand the company's strategy in a year?"** — yes → brain note (collapse clusters into one `decision`/`accomplishment`); "only matters while touching that code path" → stays in memory.

### W-MAINTAIN — light structure-maintenance pass (end of session / on request)
Start by running `scripts/brain_lint.py` and fix its errors; then: The per-session sweep — mechanical hygiene on what changed this session (contrast W-GARDEN, the deep, scheduled, numeric-gated pass). `git log -- brain/` + `Glob` inventory vs taxonomy → check changed/new notes against the rules via `Grep` (missing frontmatter, MOC-orphans, dup titles, broken `[[links]]`) → repair via `Edit` → refresh every `_MOC.md` + Home's "recently changed" → archive anything now `superseded` → **archive closed boards** (`status: closed` → `90_Archive/boards/`) → flag postmortems missing a landed harness fix. Output a short maintenance report.

## Vault-scale

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
| Freshness (strategy notes) | `verified:` within the note type's window | re-verify + stamp, or supersede/archive |
| Owner present on verifiable notes | every note with a `verified:` has an `owner:` | assign, or drop the freshness claim |
| Collector's fallacy | 0 notes with zero downstream links AND zero edits since creation | synthesize into a real note or drop |
| MOC coverage | every note reachable from a MOC | rebuild the index from frontmatter |
| Postmortem integrity | every postmortem names a LANDED harness fix | flag as incomplete on the board/MOC |
| Supersession hygiene | no two live notes claiming the same truth | merge; loser to archive with `superseded_by` |
| **Contradiction** | no two live notes asserting opposite facts | surface both, re-verify, supersede the loser |

**Indexes are derived, not curated.** Rebuild each `_MOC.md` link list
mechanically from note frontmatter on every pass — a hand-maintained index
drifts from the notes it indexes, and the drift is invisible until a recall
misses something. Human curation belongs in the MOC's *reading order and
framing*, not in remembering to add the link.

**The contradiction gate is the one that matters most.** The others are
structural — links resolve, enums are valid, ratios are sane — and a brain can
pass all of them while telling you something false. Stale knowledge is worse
than no knowledge: it makes the agent *confidently* wrong. Run it as: grep the
claim vocabulary of notes touched since the last pass, read any pair covering
the same subject, and flag semantic conflicts for re-verification.

**Staleness thresholds are per note type, not global.** A pricing note and a
thesis note do not rot at the same rate. Set the window in
`00_Meta/Frontmatter-Standard.md` per `type`; six months is a default for
strategy, not a universal law.

**Calibration note.** The tag ratio (0.15), MOC ratio (0.1), the ~50-second
note length and the freshness window are internal heuristics tuned on this
brain. They are not established practice and no published study backs the
specific numbers. Treat them as house style; adjust them when this brain's own
retrieval says otherwise.

Finish every pass by updating Home: pulse, "recently changed" (from `git log -- brain/`), and a one-table **health scorecard** so drift is visible between passes. Mechanical fixes: just do them. Structural moves (folder changes, mass archives, MOC merges): propose to the user first — agents propose, humans approve.

### W-EVOLVE — changing the law itself
Adding a domain, a note type, a status, or renaming folders touches the brain's constitution. Do it as one atomic change-set, never piecemeal: update `Taxonomy.md` (tree + purpose table + invariants) AND `Frontmatter-Standard.md` (enums) AND `00_Meta/Templates/` AND `Home.md` navigation in the same pass, with a dated note in the taxonomy explaining why. A law change without all four updated creates two versions of the law — worse than no change.

### W-REPORT — "how is the brain doing?"
On demand: census per domain (note counts, newest `updated:`), the W-GARDEN scorecard computed read-only, top 3 risks, and distance-to-target for anything mid-campaign. Deliver as chat summary; write it into Home's health section only if a garden pass ran.
