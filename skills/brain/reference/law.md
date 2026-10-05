# The brain's law (full)

Read for gardening, bootstrap, law changes or a dispute about where something belongs. Daily filing needs only SKILL.md. A project's own `brain/00_Meta/` overrides these defaults.

## Governing principles

(a brain is judged by retrieval, not size — optimize for the reader-agent six months out): **atomic notes** (~50-second reads, one claim/concept/decision per note; a source with ten ideas becomes ten notes); **current-truth-at-top** (open with the one-paragraph current truth, history/evidence below); **indexes are derived** (every `_MOC.md` link list is rebuilt mechanically from note frontmatter — the agent reads the index first and never scans blindly; human curation sets reading order, not membership); **supersede, never overwrite** (accepted decisions/findings are immutable; reality changes → new note with `supersedes:`, old archived with `superseded_by:`); **bi-temporal freshness** (`updated:` = when text changed; **`verified:`** = when a human/hawk last confirmed it true — staleness is measured on `verified:`, not `updated:`); **single-writer** (agents propose, one accountable actor writes — this skill for notes, the hawk for boards; structural changes are proposed to the user first); **no live dedupe** (dedupe-on-write is a per-note Grep; deep merge/prune runs as a scheduled pass).

## The taxonomy (10 domain folders, max depth 2)

`Home.md` (dashboard) · `00_Meta/` (the law) · `10_Product/` · `20_Goals-and-Strategy/` · `30_Investigation/` · `40_Golden-Cases/` (depth-3 exception: `<category>/<slug>.md`) · `50_Roadmap-and-Checklist/` · `55_Execution/` (depth-3 exception: `boards/<workflow-slug>/…`) · `60_Decisions-and-Accomplishments/` · `70_Concepts/` · `80_References/` · `90_Archive/`. Every note lands in exactly one domain folder and links **up to its `_MOC.md`**. These are the brain's **default** domains; a project may name its own set in `00_Meta/Taxonomy.md` (W-BOOTSTRAP derives 5–8 domains from the org, not from another brain).

**`55_Execution/` — the hawk layer (special ownership rules):**
- `boards/<workflow-slug>/` (BOARD.md · LOCKS.md · DECISIONS.md) — **written by the hawk running that workflow, not by this skill.** Here we read boards (for W-RECALL), maintain their links, and **archive a board once its status is `closed`** (move the folder to `90_Archive/boards/`, leave a link from the 55 MOC). LOCKS.md is gitignored runtime state — never archive or repair it.
- `postmortems/YYYY-MM-DD-<slug>.md` — agent-session postmortems (type `postmortem`). Enforce: every postmortem names a landed harness fix; ones that don't get flagged in maintenance as incomplete.

## The rules it enforces (the law)

**What this pattern is called.** The brain is an **LLM Wiki** (Karpathy, 2026 —
an agent-maintained interlinked markdown knowledge base with typed frontmatter
and ingest/query/lint operations) whose decision layer follows **ADR**
discipline (Nygard, 2011 — decisions are immutable; a reversal keeps the old
record and marks it superseded). Both are established, both have tooling, and
saying so makes the design legible to anyone who has met either. Decision notes
should carry an ADR-compatible `status:` (proposed / accepted / superseded).

1. **Repo-vs-brain split** — code-coupled facts get a SUMMARY + `repo_link`, never a duplicate.
2. **Taxonomy** — one domain folder per note; max depth 2 (golden-cases and 55/boards depth-3 only); no new top-level folder without updating `00_Meta/Taxonomy.md`.
3. **Naming** — per `00_Meta/Naming-Conventions.md` (Title-Case singletons; slug for golden/memory; date-suffix only on versioned artifacts; no spaces).
4. **Frontmatter** — every note has the required keys with a valid `type` + `status` enum; repair on sight.
5. **Link hygiene** — every leaf links up to its MOC and across to dependencies; no broken `[[wikilinks]]`; no MOC-orphans.
6. **Dedupe** — `Grep` the title/claim before creating; if a near-duplicate exists, UPDATE it (and `supersedes`/archive the old) rather than fork a second truth.
7. **Archive-not-delete** — superseded knowledge moves to `90_Archive/` with `superseded_by` set; live knowledge is never hard-deleted.
8. **Checklist integrity** — a checklist item flipping to `done` MUST mint an `accomplishment` note (the how/why + evidence `repo_link`) and link it; the `Checklist-to-MVP` dashboard is re-rendered from the item notes; distance-to-MVP = count of unmet `MVP-Definition` exit conditions.
9. **Board ownership** — live boards belong to their hawk; here we only read, link, and archive-on-close. Postmortems without a landed harness fix are flagged, not silently accepted.

## Anti-patterns (each with its test)
- **Museum vault** — elaborate taxonomy, no output. Test: are decisions/articles/plans actually citing brain notes? The scorecard that matters most is output, not structure.
- **Collector's fallacy** — clipping without synthesis. Test: zero-downstream-link notes accumulating.
- **Hand-maintained indexes** — a MOC whose links were added by memory rather than derived from frontmatter. Test: a note whose frontmatter places it in a domain but which its `_MOC.md` does not list.
- **Tag explosion / over-foldering** — taxonomy as procrastination. Tests: tag ratio >0.15; folders deeper than the law allows.
- **Overwrite instead of supersede** — silently rewriting an accepted decision. Test: git diff shows semantic reversal without a `supersedes` chain.
- **Agent-writes-without-gate** — bulk structural changes landing unproposed. Test: mass moves in git history with no user approval recorded.
- **Staleness by `updated:`** — treating untouched-but-true notes as rot, or touched-but-wrong notes as fresh. Measure on `verified:`.
- **Prose where a check belongs** — a note stating a rule the agent must follow ("never call X directly", "migrations must be expand-contract") is a lint rule or a test that has not been written yet. Test: any `decision` whose consequence is a rule, with no `repo_link` to something that enforces it. File the note, then convert it — a rule the harness enforces cannot be forgotten, and the note becomes the explanation rather than the enforcement.
- **Monotonic growth** — supersede-never-overwrite only ever adds. Without archival the brain accumulates until retrieval degrades, and the token-compounding economics that justify a brain hold only while the domain stays concentrated. Test: live-note count rising while citations per note fall. Archive aggressively; a brain is judged by what it returns, not what it holds.
