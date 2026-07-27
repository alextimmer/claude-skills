---
name: memory-harness
description: Install, verify, or maintain the Claude Code memory harness (CLAUDE.md + .claude/rules memory + SessionStart/PreCompact/Stop hooks) in a repository. Use when asked to "install the harness", "set up project memory", "verify the harness", or to prune/promote harness memory files.
---

# Memory harness — install & maintain

The harness makes a stateless Claude Code session behave like one with a persistent
lab notebook: `CLAUDE.md` (standing instructions, TDD-mandatory), `.claude/rules/`
(dated, attributed project memory), and three tested hooks (SessionStart orientation
+ cap audit, PreCompact block-once save-gate, Stop block-once memory reminder).

**Harness location:** `${CLAUDE_PLUGIN_ROOT}` — the installed plugin's root, containing
`template/`, `README.md`, `INSTALL.md`. It resolves automatically; nothing to configure.

## Which task?

| Request | Do |
|---------|-----|
| Install into a repo | Follow `references/install-procedure.md` |
| Verify / self-test | `bash .claude/hooks/selftest.sh` (33 checks) in the target repo; then `/hooks` should list SessionStart + PreCompact + Stop |
| Scan memory for secrets | `bash .claude/hooks/secret-scan.sh` before committing memory files (exit 1 = findings; report, never auto-edit) |
| Tune hook patterns | `references/hook-tuning.md` |
| Prune / promote / audit memory | `references/memory-conventions.md` |
| Understand the design | Read `${CLAUDE_PLUGIN_ROOT}/README.md` + `${CLAUDE_PLUGIN_ROOT}/DECISIONS.md` |

## Hard rules (all tasks)

- The target repo's existing `CLAUDE.md` / `.claude/` must NEVER be silently
  overwritten — inspect first, merge deliberately, ask on conflict.
- Unknown stays unknown — not observed ≠ absent. Never record unverified claims as
  fact in memory files; mark them unknown and date the observation.
- When writing any memory entry, use a `## YYYY-MM-DD: Description [Agent Name]`
  heading — attribution keeps multi-agent memory auditable.
- After any hook change: re-run the self-test before claiming success ("written"
  does not equal "working" — premature-victory prevention).
- The track-vs-exclude choice (commit the harness vs `.git/info/exclude`) is the
  USER's decision — always ask, never assume (see install procedure, step 4).
