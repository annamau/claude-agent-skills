# Adapter — <YOUR PROJECT>

Copy this file to `ADAPTER.<project>.md` (which is gitignored) and fill it in.
It pins the project-specific values the generic skills reference as placeholders,
so the published skills stay org-agnostic while working smoothly for you.

Point your session at this file (e.g. reference it in your project's `CLAUDE.md`)
so the hawk and review skills resolve the placeholders below.

## Repository

- `{{REPO}}` = `owner/name`            # GitHub slug for gh api / PR commands
- Default branch = `main`

## Cross-model review

- `{{REVIEW_BOT_LOGIN}}` = `chatgpt-codex-connector[bot]`   # match with startswith(), not equality (the [bot] suffix)
- `{{CROSS_MODEL_REVIEW_CMD}}` = `codex exec review --commit <sha> -s read-only -o <findings-file> "<brief>"`
- Reviewer must be a DIFFERENT vendor/family than the implementer (that is the whole point).
- Setup (OpenAI Codex default): install the GitHub app for `{{REPO}}` and create a Codex cloud environment for it, else it posts a setup prompt instead of a real review.

## Company brain (brain-builder / vault-librarian)

- Brain root: `brain/`
- Keystone notes W-RECALL should read first (project-specific — rename as yours):
  - `brain/30_Investigation/Thesis.md` (or your equivalent north-star note)
  - `brain/50_Roadmap-and-Checklist/Checklist-to-MVP.md`
  - `brain/50_Roadmap-and-Checklist/MVP-Definition.md`
- Domain taxonomy: the default numbered domains, unless overridden in `brain/00_Meta/Taxonomy.md`.

## Anything else project-specific

- Test/demo account, local-env guardrails, deploy targets, house rules the hawk must respect.
