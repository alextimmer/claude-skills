#!/usr/bin/env bash
# SessionStart hook: the "initialization phase" of the harness.
#
# Whatever this script prints to stdout (exit 0) is INJECTED INTO THE MODEL'S
# CONTEXT at session start — unlike Stop, SessionStart supports model-facing
# injection natively. We use it to orient the model: repo state at a glance and
# a pointer to the memory micro-backlog.
#
# Keep the output SHORT. Every line here is paid for in every session's context
# budget, on top of CLAUDE.md and the auto-loaded .claude/rules/*.md files.
#
# Input (stdin): SessionStart JSON payload (session_id, transcript_path, cwd,
#   hook_event_name, source). `source` is one of: startup, resume, clear,
#   compact, fork — "compact" means SessionStart re-fired MID-SESSION right
#   after auto-/manual compaction, and stdout is injected then too.
# Output (stdout): plain text -> model context. Never blocks anything.

# Opt-out for one-shot / CI sessions (e.g. `claude -p`) that merely share a cwd
# with the harness and never opted into it: CLAUDE_MEMORY_HARNESS_DISABLED=1 makes
# the hook consume its payload and exit silently (exit 0, no output = proceed).
[ "${CLAUDE_MEMORY_HARNESS_DISABLED:-}" = "1" ] && { cat >/dev/null; exit 0; }

PAYLOAD=$(cat)

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

# Post-compaction memory flush: compaction is the other moment context gets
# lost (besides session end, which the Stop hook covers). The compact summary
# is lossy, but the full pre-compact transcript survives on disk — point at it.
SOURCE=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"source":"\([^"]*\)".*/\1/p')
if [ "$SOURCE" = "compact" ]; then
  # The transcript path arrives JSON-escaped (C:\\Users\\...); normalize to /.
  TRANSCRIPT=$(printf '%s' "$PAYLOAD" \
    | sed -n 's/.*"transcript_path":"\([^"]*\)".*/\1/p' \
    | sed 's/\\\\/\//g')
  echo "Context was just compacted. If the compacted conversation contained a fix, discovery, or design decision that is NOT yet in .claude/rules/memory-*.md, record it now (attribution format) — the summary above is lossy.${TRANSCRIPT:+ Details are recoverable from the full pre-compact transcript: $TRANSCRIPT}"
fi

# Cap-triggered memory-discipline audit (adapted from awrshift/claude-memory-kit).
# The rolling session log must stay a note, not a chronicle. Three caps, each
# catching a different shape of bloat: line count, total bytes, and chars-per-
# line (content can densify into ever-longer lines while `wc -l` stays flat).
SESSIONS=".claude/rules/memory-sessions.md"
if [ -f "$SESSIONS" ]; then
  S_LINES=$(wc -l < "$SESSIONS")
  S_BYTES=$(wc -c < "$SESSIONS")
  S_MAXLINE=$(awk '{ if (length($0) > m) m = length($0) } END { print m + 0 }' "$SESSIONS")
  if [ "$S_LINES" -gt 180 ] || [ "$S_BYTES" -gt 32768 ] || [ "$S_MAXLINE" -gt 3000 ]; then
    echo "Memory discipline: $SESSIONS tripped its size caps (${S_LINES}/180 lines, ${S_BYTES}/32768 bytes, longest line ${S_MAXLINE}/3000 chars). Before other work: promote patterns that appear on 3+ different dates into memory-decisions.md, prune absorbed or stale entries, and keep 'Open TODOs (small)' current. The log is a note, not a transcript."
  fi
fi

# Stale-reference advisory (adapted from awrshift/claude-memory-kit): file paths
# mentioned in memory are claims those files existed WHEN THE ENTRY WAS WRITTEN.
# Flag the ones that no longer resolve — advisory only, never auto-delete. For a
# missing path, a same-name file elsewhere in the git index usually means a
# rename: suggest it ("moved to X?") instead of just reporting an absence.
SEEN=""
STALE=""
for f in .claude/rules/memory-decisions.md .claude/rules/memory-sessions.md; do
  [ -f "$f" ] || continue
  for p in $(grep -oE '[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)+\.(md|sh|py|ts|tsx|js|jsx|json|jsonl|yaml|yml|toml|scala|java|go|rs|rb|sql|txt)' "$f" 2>/dev/null | sort -u); do
    case "$p" in http*|*'*'*|tmp/*|*..*) continue;; esac
    [ -e "$p" ] && continue
    case " $SEEN " in *" $p "*) continue;; esac
    SEEN="$SEEN $p"
    BASE=$(basename "$p")
    HIT=$(git ls-files -- "*/$BASE" "$BASE" 2>/dev/null | head -1)
    if [ -n "$HIT" ]; then
      STALE="$STALE $p (moved to $HIT?)"
    else
      STALE="$STALE $p"
    fi
  done
done
if [ -n "$STALE" ]; then
  echo "Stale memory references (not found on disk — renamed? moved? deleted?):${STALE}. A memory naming a file is a claim it existed when the entry was written — verify each, update or remove the entry, and trust what you observe now."
fi

# Seeded-memory honesty (adapted from hung12ct/culi): an empty/seeded memory must be
# distinguishable from an unaware one, or the model over-trusts the silence.
if grep -q '<Example' .claude/rules/memory-decisions.md .claude/rules/memory-sessions.md 2>/dev/null; then
  echo "Memory note: the memory files still contain only the seed example — nothing has been recorded yet. When memory is silent on a topic, verify against the code instead of assuming there is nothing to know; when you record the first real entry, delete the seed example."
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  BRANCH=$(git branch --show-current 2>/dev/null)
  DIRTY=$(git status --porcelain 2>/dev/null | grep -c .)
  echo "Session-start repo state: branch '${BRANCH:-detached}', ${DIRTY} uncommitted change(s)."
  echo "Recent commits:"
  git log --oneline -3 2>/dev/null | sed 's/^/  /'
fi

# Age stamp on the pointer: memory freshness at a glance (a stale log is a signal,
# not a secret — memories are point-in-time observations, not live state).
AGE_NOTE=""
if [ -f "$SESSIONS" ]; then
  NOW=$(date +%s)
  MT=$(stat -c %Y "$SESSIONS" 2>/dev/null || stat -f %m "$SESSIONS" 2>/dev/null || echo "$NOW")
  AGE_NOTE=" (memory-sessions.md last updated $(( (NOW - MT) / 86400 ))d ago)"
fi
echo "Before starting: check 'Open TODOs (small)' at the top of .claude/rules/memory-sessions.md. Update memory files AS YOU GO (see CLAUDE.md Project Memory triggers).$AGE_NOTE"
exit 0
