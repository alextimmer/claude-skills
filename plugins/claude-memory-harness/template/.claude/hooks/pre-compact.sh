#!/usr/bin/env bash
# PreCompact hook: the save-gate (block-once design).
#
# Compaction is the other moment context gets lost (besides session end, which
# the Stop hook covers). This hook fires BEFORE auto-/manual compaction and
# blocks it ONCE if the memory looks unsaved (stale) or unpruned (over caps) —
# the model gets one turn to write/prune memory while the details are still in
# context, then compaction proceeds. The post-compaction nudge in
# session-context.sh stays as the backstop for whatever slipped through.
#
# Gate (adapted from awrshift/claude-memory-kit): allow compaction only when
# memory-sessions.md was modified recently (< 120 s) AND is under all three
# size caps (180 lines / 32 KB / 3000 chars per line — the third exists
# because content can densify into ever-longer lines while `wc -l` stays
# flat). Fresh-but-bloated still blocks: that forces a prune, not a panic-dump.
#
# Anti-wedge guards:
#   1. once per session (marker file) — a block can never repeat, so an
#      auto-compaction with a full context is delayed by at most one turn.
#   2. no memory file -> proceed quietly (repo without the harness memory).
#
# Input (stdin): PreCompact JSON payload (session_id, transcript_path, cwd,
#   trigger: "manual"|"auto") — metadata only.
# Output (stdout): {} to allow compaction, or {"decision":"block","reason":...}.

# Opt-out for one-shot / CI sessions (e.g. `claude -p`) that merely share a cwd
# with the harness and never opted into it: CLAUDE_MEMORY_HARNESS_DISABLED=1 makes
# the hook consume its payload and exit silently (exit 0, no output = proceed).
[ "${CLAUDE_MEMORY_HARNESS_DISABLED:-}" = "1" ] && { cat >/dev/null; exit 0; }

PAYLOAD=$(cat)

SESSION_ID=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"session_id":"\([^"]*\)".*/\1/p')
MARKER="${TMPDIR:-/tmp}/claude-memory-precompact-${SESSION_ID:-unknown}"

# Guard 1: already gated once this session — let compaction proceed.
[ -n "$SESSION_ID" ] && [ -f "$MARKER" ] && { echo '{}'; exit 0; }

# Guard 2: no harness memory in this repo — nothing to gate.
SESSIONS="${CLAUDE_PROJECT_DIR:-.}/.claude/rules/memory-sessions.md"
[ -f "$SESSIONS" ] || { echo '{}'; exit 0; }

NOW=$(date +%s)
MTIME=$(stat -c %Y "$SESSIONS" 2>/dev/null || stat -f %m "$SESSIONS" 2>/dev/null || echo 0)
AGE=$((NOW - MTIME))
LINES=$(wc -l < "$SESSIONS")
BYTES=$(wc -c < "$SESSIONS")
MAXLINE=$(awk '{ if (length($0) > m) m = length($0) } END { print m + 0 }' "$SESSIONS")

# Fresh AND under all three caps -> compaction may proceed.
if [ "$AGE" -lt 120 ] && [ "$LINES" -le 180 ] && [ "$BYTES" -le 32768 ] && [ "$MAXLINE" -le 3000 ]; then
  echo '{}'
  exit 0
fi

[ -n "$SESSION_ID" ] && touch "$MARKER"
echo '{"decision":"block","reason":"COMPACTION IMMINENT - the context is about to be summarized (lossy). memory-sessions.md was last updated '"$AGE"'s ago ('"$LINES"'/180 lines). Before compaction proceeds: record any un-recorded fix, discovery, or decision in .claude/rules/memory-sessions.md (attribution format) and refresh Open TODOs. If the file is over its caps (180 lines / 32 KB / 3000 chars per line), prune it: promote patterns seen on 3+ different dates into memory-decisions.md and drop absorbed entries. If everything is already recorded, simply continue - you will not be gated again this session."}'
