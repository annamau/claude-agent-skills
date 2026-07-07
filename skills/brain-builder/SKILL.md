---
name: brain-builder
description: >-
  Vault-SCALE engineering for a repo-based company brain (an Obsidian-style linked markdown vault like a repo's brain/ directory). Use when the user wants to BUILD a brain from scratch in a repo ("bootstrap a brain/vault for this project"), run a bulk INGESTION campaign ("ingest these docs/memories into the brain"), run a deep GARDENING/health pass ("garden the brain", "health check the vault", "brain report"), or EVOLVE the taxonomy (add/rename a domain, change the frontmatter law). Complements vault-librarian — the librarian is the note-scale law + daily in/out manager; brain-builder is the construction crew and health engineer that works at whole-vault scale. Do NOT use for filing a single finding/decision (that's vault-librarian) or for hawk boards (the hawk owns those).
license: MIT
metadata:
  author: annamau
  version: "1.0.0"
---

# Brain Builder — construct, grow, and garden a repo-based company brain

**Meta-instruction:** A brain is judged by retrieval, not by size. Every structural choice below exists to make the right note findable by an agent (grep/Glob-first) and trustworthy when found (fresh, superseded-not-overwritten, linked to its evidence). When in doubt, optimize for the reader-agent six months from now, not for the writer today.

**Division of labor:** `vault-librarian` enforces the note-scale law (frontmatter, naming, dedupe, MOC links) and runs daily in/out. `brain-builder` works at vault scale: bootstrap, ingestion campaigns, deep gardening with numeric health gates, and taxonomy evolution. Builder actions always obey the vault's own law in `00_Meta/` — read it before structural work.

## The principles (industry-grounded, mid-2026)

1. **Flat markdown in a versioned repo folder is the production standard** for agent-read brains — human-auditable (git blame), offline, no retrieval API. Graph/vector layers only earn their cost at ~100K+ facts; below that, grep + index files win.
2. **Atomic notes, ~50-second reads.** One claim/concept/decision per note. A focused 40-line note retrieves far better for an LLM than a 200-line synthesis it must decompose. A source with ten ideas becomes ten notes.
3. **Current-truth-at-top layout.** Agents read top-first: the note opens with the one-paragraph current truth; history, evidence, and timeline go below.
4. **MOCs emerge bottom-up.** Don't scaffold index pages for content that doesn't exist. Mint a MOC when a topic accumulates **~15–20 related notes**; connect MOC-to-MOC only after several exist. (Domain-level MOCs from the taxonomy are the exception — they're the law's navigation floor.)
5. **Supersede, never overwrite** (ADR discipline): accepted decisions and findings are immutable; reality changes → new note with `supersedes:`, old note archived with `superseded_by:`. This preserves the decision timeline agents need to avoid re-making old mistakes.
6. **Bi-temporal freshness:** `updated:` says when the text changed; **`verified:`** says when a human/hawk last confirmed it still true. Staleness is measured on `verified:`, not `updated:` — a note nobody touched can still be checked and re-stamped.
7. **Single-writer ceremonies.** Agents propose, one accountable actor writes (librarian for notes, hawk for boards); structural changes (new domain, mass moves) are proposed to the user before execution. Multi-writer brains rot into conflicts.
8. **No live dedupe — scheduled compaction.** Dedupe-on-write is a per-note Grep check; deep merge/prune runs as a scheduled pass, not opportunistically.

## W-BOOTSTRAP — build a brain from zero (any repo)

1. **Derive the domains from the org, don't copy another brain's.** Interview the repo + user: what is the product, what evidence exists, what decisions recur, what does "done" mean here? 5–8 domains max, numbered with gaps (`10_`, `20_`, …) so new domains slot in later.
2. **Scaffold the minimum law first:** `Home.md` (dashboard with a "pulse" section), `00_Meta/` (Taxonomy with the split-source-of-truth contract + ingestion map, Frontmatter-Standard with controlled `type`/`status` enums incl. `verified:`, Naming-Conventions, one template per note type), and a `_MOC.md` per domain. Nothing else — content earns structure, not vice versa.
3. **Encode the split-source-of-truth contract on day one:** strategy lives in the brain; code-coupled detail (`file:line`, migrations, raw data) stays in the repo with the brain holding a SUMMARY + `repo_link`. Splitting by volatility is what keeps the brain trustworthy for years.
4. **Add the execution layer** (`55_Execution/`-style: `boards/` + `postmortems/`) if agents will run supervised workflows in this repo; gitignore the lock ledgers.
5. Seed with a first ingestion campaign (below), then hand steady-state to a librarian-style skill.

## W-INGEST-CAMPAIGN — bulk ingestion of a source set

For waves of material (repo docs, memory files, transcripts, research reports):

1. **Map before writing.** Build an ingestion table (source → target folder → note type → disposition: FULL COPY only if pure strategy / SUMMARY+`repo_link` if code-coupled / NO-INGEST if stale or raw data). Show it to the user if the set is large or anything gets dropped.
2. **The new-hire test** decides borderline cases: "would a new hire need this to understand the company's strategy in a year?" Yes → note. "Only matters while touching that code path" → stays out, referenced.
3. **Batch and link as you go:** per batch — Grep-dedupe, write atomically (principle 2), link each note up to its MOC and across to dependencies immediately. A linking debt at campaign end never gets paid.
4. **Close the campaign:** refresh affected MOCs and Home's pulse, re-run the census (below), and record the campaign as a `decision`/`accomplishment` note with the ingestion map as evidence.

## W-GARDEN — the deep gardening pass (the health engineer)

Cadence: **monthly** under ~500 notes, **weekly** above; always after a large campaign. (The librarian's W-MAINTAIN stays the light per-session pass.) A pass computes the scorecard, fixes what's mechanical, and PROPOSES what's structural:

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

## W-EVOLVE — changing the law itself

Adding a domain, a note type, a status, or renaming folders touches the brain's constitution. Do it as one atomic change-set, never piecemeal: update `Taxonomy.md` (tree + purpose table + invariants) AND `Frontmatter-Standard.md` (enums) AND `00_Meta/Templates/` AND `Home.md` navigation in the same pass, with a dated note in the taxonomy explaining why. A law change without all four updated creates two versions of the law — worse than no change.

## W-REPORT — "how is the brain doing?"

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

A builder action is done when: the law in `00_Meta/` still has exactly one version; every touched note passes the librarian's note-scale rules; the health scorecard is computed and visible on Home (garden passes); structural changes were user-approved; and the pass itself is traceable (git history + a pulse line).
