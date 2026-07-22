# `.claude/rules/` — auto-loaded project memory

Every `.md` file in this folder is **automatically loaded into context at the start of
every Claude Code session** in this repo, alongside the root `CLAUDE.md`. You do not
need to reference these files or ask Claude to read them — they are always present.

## What lives here

| File | Role | Lifecycle |
|------|------|-----------|
| `memory-decisions.md` | Durable architecture/design decisions + reasoning | Ages slowly |
| `memory-sessions.md` | Rolling, newest-first log of work and lessons | Ages fast |
| `memory-attribution.md` | The `[Agent Name]` heading convention all entries follow | Stable |

## Rules of thumb

- **Everything here is paid for in every session's context budget.** Keep entries as
  signal, not noise. Prune stale session entries; promote durable lessons to decisions.
- **Every entry gets a dated, attributed heading:** `## YYYY-MM-DD: Description [Agent]`
  (see `memory-attribution.md`).
- **Unknown stays unknown — not observed ≠ absent.** Never record an unverified claim
  as fact; mark it unknown/unverified and date the observation. This is what keeps
  `memory-decisions.md` trustworthy over time.
- **Add files freely** — any new `*.md` here also auto-loads. Keep the count small and
  purposeful (modular instruction design beats one monolithic instruction sheet, but
  every file costs context).
- **`memory-decisions.md` has two extra sections:** "Ruled out" (dead ends actually
  tried, with the WHY — what stops future sessions from re-attempting them) and
  "Candidates (unconfirmed)" (one-sighting lessons; promote on the second date they
  reappear, prune otherwise).
- **Size caps on `memory-sessions.md`** (180 lines / 32 KB / 3000 chars-per-line):
  the SessionStart hook flags a breach and the PreCompact hook enforces it before
  compaction — prune and promote instead of raising the caps. The log is a note,
  not a transcript.

## Coexisting with other agents

Other AI agents may keep their own config in the same repo (e.g. GitHub Copilot's
`.github/copilot-instructions.md` / agent files, a `GEMINI.md`, ...). This harness makes
no claims over those — but these memory files are the **common ground**: any agent
working here should read them and tag its entries with its own `[Agent Name]` (see
`memory-attribution.md`). The attribution tag is what keeps a multi-agent workspace
auditable.

## Repo-level vs. per-user memory

This folder is **repo-level** memory: commit it, and every teammate/agent who clones the
repo gets the same context. For *personal* preferences you don't want in a shared repo,
use Claude Code's **built-in per-user memory** instead
(`~/.claude/projects/<slug>/memory/`), which is scoped to you and never committed.
