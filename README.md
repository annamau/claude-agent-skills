# claude-agent-skills

A toolkit of **agentic-engineering skills for [Claude Code](https://claude.com/claude-code)** — a supervised, multi-agent workflow for planning, building, reviewing, and remembering software work. Built and hardened in production, then generalized to be org-agnostic.

The through-line is one idea: **a single lead agent — the HAWK — runs a team of expert subagents as a distributed system, and nothing is "done" until a differently-trained model has checked it.** Agents drift, hallucinate, and rubber-stamp their own work; these skills are the guardrails that keep a long autonomous run honest.

## The skills

| Skill | Role | Use when |
|---|---|---|
| **plan-with-review** | Architect | You have a non-trivial idea and no plan. Assembles a domain-expert team that researches (online + in your codebase), surfaces conflicts, drafts a plan, then verifies it against live ground truth. Emits a **Team Roster + file-ownership map**. |
| **phases-execution** | The HAWK (Product Owner + Tech Lead) | You have an approved multi-phase plan. Dispatches the expert team as a **concurrent team in one shared worktree** (ownership map + lock ledger), supervises them live (steers drift, escalates, answers their questions via research), runs a **cross-model review** on every functionality commit, keeps a workflow board, and files postmortems when a session goes bad. |
| **copilot-review-loop** | Cross-model PR gate | A PR is open and not yet merged. Triggers a differently-trained reviewer (default: OpenAI Codex), loops on findings with a hard cap, root-causes repeats, and applies a Product-Owner acceptance gate before "ready to merge." |
| **phase-based-refactor** | Refactor rhythm | A risky refactor/rewrite where the danger is "piling on patches." Forces IMPLEMENT → TEST → PRODUCT-THINK → INDEPENDENTLY VERIFY → SHIP per phase. |
| **brain-builder** | Knowledge-base engineer | You want to build / bulk-ingest / deep-garden a repo-based **company brain** (a linked-markdown vault). Works at whole-vault scale with numeric health gates. |
| **vault-librarian** | Knowledge-base librarian | Day-to-day recall and filing into that brain — recall state before work, file findings/decisions/postmortems after. |

`plan-with-review → phases-execution → copilot-review-loop` is the main pipeline. `brain-builder` + `vault-librarian` are the memory layer the hawk reads from and writes to.

## Design principles (why these exist)

These skills encode a specific, sourced view of mid-2026 agentic-engineering practice:

- **Supervisor over the swarm.** A lead agent that *routes and steers* rather than implements; steering a running worker beats kill-and-respawn until a retry cap; escalate to the human only for genuine product/scope calls. (Anthropic multi-agent research system; LangGraph supervisor pattern.)
- **Team awareness, not isolation.** Workers share one worktree and a **file-ownership map + lock ledger** ("claim before edit"), and each knows what teammates own — the ownership map is the single most important coordination artifact. (Shared-workspace concurrency practice.)
- **Verify with a different model.** LLMs favor their own output (self-preference bias); a same-family reviewer shares the implementer's blind spots. Every functionality gets reviewed by a differently-trained model before it ships. (Self-preference-bias literature.)
- **A durable brain, not just context.** Long autonomous work needs memory that survives compaction: flat markdown in the repo, atomic notes, supersede-don't-overwrite, bi-temporal freshness (`updated` vs `verified`). (Agent-memory practice; ADR discipline; PKM methodology.)
- **Detect poisoned sessions.** Cheap tripwires (repeated failed edits, test-pass regression, diff-churn-without-progress, agents echoing each other's wrong belief) trigger quarantine + respawn-from-curated-state; every bad session mints a blameless postmortem whose exit criterion is a **landed harness fix**. (Context-rot + sycophancy-propagation research.)

## Install

Each directory under `skills/` is a self-contained Claude Code skill. Copy or symlink the ones you want into your skills directory:

```bash
# symlink all six into your user skills dir
for s in skills/*/; do
  ln -s "$(pwd)/$s" "$HOME/.claude/skills/$(basename "$s")"
done
```

Then `/plan-with-review`, `/phases-execution`, etc. become available (Claude Code discovers skills from that directory).

## Configuration (making them yours)

The skills are written generically. A few call sites reference **placeholders** you supply for your own project:

| Placeholder | Meaning | Example |
|---|---|---|
| `{{REPO}}` | GitHub `owner/repo` slug for PR/review commands | `octocat/hello-world` |
| `{{REVIEW_BOT_LOGIN}}` | Login of your cross-model reviewer bot (match with `startswith`, it has a `[bot]` suffix) | `chatgpt-codex-connector[bot]` |
| `{{CROSS_MODEL_REVIEW_CMD}}` | CLI invocation for local cross-model review | `codex exec review --commit <sha> -s read-only` |

The recommended pattern is a single local **`ADAPTER.<project>.md`** file (gitignored) that pins these values plus any project-specific keystone-note names and taxonomy. `ADAPTER.example.md` in this repo is a template — copy it, fill it in, keep it out of git.

## Provenance

Distilled from real production use and a July 2026 research sweep across supervisor/orchestrator patterns, shared-worktree concurrency, cross-model verification, poisoned-session detection, and the agentic-engineering canon (Anthropic, 12-Factor Agents, LYT/PKM, ADR practice, and the self-preference-bias literature). See each skill's header for its specific grounding.

## License

MIT — see [LICENSE](LICENSE).
