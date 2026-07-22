# Hook tuning guide

The hooks live in the target repo's `.claude/hooks/` and are wired in
`.claude/settings.json` (each with `"timeout": 10`). After ANY change here:
`bash .claude/hooks/selftest.sh` — 33 passed required.

## Stop hook (`memory-reminder.sh`) — the one that needs per-repo tuning

Design recap: reads the transcript at `transcript_path` (the Stop stdin payload is
metadata only — it never contains the conversation), and blocks the stop ONCE with a
model-facing "update memory" reason when a lesson-signal is found and no
`memory-*.md` was written this session. Guards: `stop_hook_active` (never twice in a
row), a `$TMPDIR` marker (once per session), and the already-updated check.

### Tuning `STRONG_PATTERNS`

- Patterns are **phrases, not bare words**, where a bare word collides with code
  vocabulary: `fixed (the|a|an|it|this)` instead of `fixed` — a repo full of
  `FixedWidth`/`fixed-width` identifiers proved why.
- Before adding a word, grep the repo for it (`grep -ric <word> .`); if it appears
  in identifiers, paths, or docs, phrase-ify it or leave it out.
- NEVER add phrases true of every healthy session in the repo's workflow
  (`all tests pass`, `new test`, `TDD` in a TDD-mandated repo) — with a blocking
  hook they are pure nag and destroy the signal.
- The grep intentionally covers only genuine user/assistant lines and excludes
  `system-reminder` lines (those embed CLAUDE.md + the memory files, which are full
  of trigger words).
- The correction-signal tier (`not what (i|we) (asked|meant|wanted)`, `i told you`,
  `doesn.t want to proceed`, `interrupted by user`, the `"text":"(no|wait),` message
  opener) detects user pushback — the strongest lesson signal. The opener pattern is
  JSON-anchored on purpose: "no" mid-text is ordinary prose; "No, ..." opening a
  message is a correction.

### If the reminder fires too often / never

- Too often: find which pattern matches (`grep -iE "<pattern>" <transcript>`),
  phrase-ify or remove it.
- Never: confirm the hook is loaded (`/hooks`), then check the transcript actually
  contains a `"role":"assistant"` line matching a pattern outside system-reminders.

## SessionStart hook (`session-context.sh`)

Rarely needs tuning. Keep the output SHORT — injected stdout is paid for in every
session's context budget. If the repo isn't git-based, it degrades to just the
Open-TODOs pointer automatically. It also runs the size-cap audit on
`memory-sessions.md` (180 lines / 32 KB / 3000 chars-per-line); raise the caps only
deliberately — they are the rolling log's decay mechanism.

## PreCompact hook (`pre-compact.sh`)

Blocks compaction ONCE per session when `memory-sessions.md` is stale (>120 s) or
over its caps, so the model saves/prunes while details are still in context. Tuning
knobs: the 120 s freshness window and the same three caps (keep them identical to
the SessionStart audit). The once-per-session marker is the anti-wedge guarantee —
do not remove it: auto-compaction fires when context is FULL, and an unconditional
block could wedge the session.

## Renaming memory files

If the memory files are renamed, update: the `reason` string and the
`memory-[a-z]+\.md` guard regex in `memory-reminder.sh`, the pointer text in
`session-context.sh`, the CLAUDE.md Project Memory table — then re-run the self-test
(and update its fixtures if the names no longer match `memory-*`).
