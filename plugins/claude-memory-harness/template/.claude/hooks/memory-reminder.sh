#!/usr/bin/env bash
# Stop hook: model-facing memory reminder (block-once design).
#
# Fires when Claude finishes a response. If the session transcript shows signs of
# a fix/discovery/decision AND the memory files were NOT updated this session,
# it blocks the stop ONCE with a reason telling Claude to update
# .claude/rules/memory-sessions.md / memory-decisions.md. Claude performs the
# update (or judges there is nothing to record) and stops on the next turn.
#
# Guards against nagging:
#   1. stop_hook_active  -> never block twice in a row (Claude Code sets this on
#      the stop that follows a hook-forced continuation).
#   2. memory-write guard -> if the transcript already contains a Write/Edit to a
#      memory-*.md file, the job is done: stay silent.
#   3. once-per-session marker -> after one block, a marker file in $TMPDIR
#      silences the hook for the rest of the session, even if Claude decided
#      nothing was worth recording.
#
# Input (stdin): Stop-event JSON payload — metadata ONLY:
#   {"session_id":"...","transcript_path":"...","cwd":"...",
#    "hook_event_name":"Stop","stop_hook_active":false}
#   The conversation itself is NOT on stdin; it must be read from transcript_path
#   (plain JSONL, one message record per line).
# Output (stdout): {} to allow stopping, or {"decision":"block","reason":"..."}.
#
# Tune STRONG_PATTERNS per repo. Beware substring collisions with your domain
# vocabulary (e.g. a repo full of "FixedWidth"/"fixed-width" identifiers is why
# "fixed" is matched as a phrase, not a bare word).

# Opt-out for one-shot / CI sessions (e.g. `claude -p`) that merely share a cwd
# with the harness and never opted into it: CLAUDE_MEMORY_HARNESS_DISABLED=1 makes
# the hook consume its payload and exit silently (exit 0, no output = proceed).
[ "${CLAUDE_MEMORY_HARNESS_DISABLED:-}" = "1" ] && { cat >/dev/null; exit 0; }

PAYLOAD=$(cat)

# Guard 1: we already blocked on the previous stop — let Claude stop now.
case "$PAYLOAD" in
  *'"stop_hook_active":true'*) echo '{}'; exit 0;;
esac

SESSION_ID=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"session_id":"\([^"]*\)".*/\1/p')
MARKER="${TMPDIR:-/tmp}/claude-memory-reminder-${SESSION_ID:-unknown}"

# Guard 3: already reminded once this session.
[ -n "$SESSION_ID" ] && [ -f "$MARKER" ] && { echo '{}'; exit 0; }

# The transcript path arrives JSON-escaped (C:\\Users\\...); normalize to /.
TRANSCRIPT=$(printf '%s' "$PAYLOAD" \
  | sed -n 's/.*"transcript_path":"\([^"]*\)".*/\1/p' \
  | sed 's/\\\\/\//g')
[ -f "$TRANSCRIPT" ] || { echo '{}'; exit 0; }

# Guard 2: memory files were already written/edited this session — nothing to do.
if grep -qE '"name":"(Write|Edit|MultiEdit|NotebookEdit)".*memory-[a-z]+\.md' "$TRANSCRIPT"; then
  echo '{}'; exit 0
fi

# Signal detection. Only genuine user/assistant message lines count:
#  - system-reminder lines are excluded (they embed CLAUDE.md + the memory files
#    themselves, which are full of words like "fixed" — guaranteed false positives).
#  - phrases, not bare words, where a bare word collides with common code/docs
#    vocabulary ("fixed" -> "fixed the/a/an/it/this", "bug fix").
#  - correction signals (adapted from hung12ct/culi): "not what I asked/meant",
#    "I told you", and a leading "No,"/"Wait," message opener ("no" mid-text is
#    ordinary prose; as an opener it is a correction). Claude Code's own tool-
#    rejection strings ("doesn't want to proceed", "interrupted by user") are
#    the strongest correction signal there is.
STRONG_PATTERNS='fixed (the|a|an|it|this)|bug ?fix|workaround|gotcha|that.s wrong|check again|we already|should have|discovered|realized|turns out|root cause|breaking change|refactor|not what (i|we) (asked|meant|wanted)|i told you|i already (said|told)|doesn.t want to proceed|interrupted by user|"text":"(no|wait),'

if grep -E '"role":"(user|assistant)"' "$TRANSCRIPT" \
     | grep -v 'system-reminder' \
     | grep -qiE "$STRONG_PATTERNS"; then
  [ -n "$SESSION_ID" ] && touch "$MARKER"
  echo '{"decision":"block","reason":"Memory check before stopping: this session appears to contain a fix, discovery, or design decision. If so, update .claude/rules/memory-sessions.md (and memory-decisions.md if it is durable) following the attribution format, then stop. If nothing is genuinely worth recording, just stop again — you will not be asked twice this session."}'
else
  echo '{}'
fi
