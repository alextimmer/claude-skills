#!/usr/bin/env bash
# Harness self-test: machine-checks the claims made about the hooks.
# ("Written" does not equal "working" — run this after install and after any
# hook edit.) Inspects only; creates and removes ONLY its own temp files.
#
# Usage:  bash .claude/hooks/selftest.sh        (from the repo root)
# Exit 0 = all checks pass; exit 1 = at least one failure.

HERE="$(cd "$(dirname "$0")" && pwd)"
STOP_HOOK="$HERE/memory-reminder.sh"
START_HOOK="$HERE/session-context.sh"
PRECOMPACT_HOOK="$HERE/pre-compact.sh"
TMP="$(mktemp -d)"
PASS=0; FAIL=0

check() { # check <name> <expected-substring> <actual>
  if printf '%s' "$3" | grep -qF "$2"; then
    echo "PASS: $1"; PASS=$((PASS+1))
  else
    echo "FAIL: $1 (expected to contain: $2 | got: $3)"; FAIL=$((FAIL+1))
  fi
}

check_not() { # check_not <name> <forbidden-substring> <actual>
  if printf '%s' "$3" | grep -qF "$2"; then
    echo "FAIL: $1 (expected NOT to contain: $2 | got: $3)"; FAIL=$((FAIL+1))
  else
    echo "PASS: $1"; PASS=$((PASS+1))
  fi
}

payload() { # payload <transcript-path> <session-id> <stop_hook_active>
  printf '{"session_id":"%s","transcript_path":"%s","cwd":"%s","hook_event_name":"Stop","stop_hook_active":%s}' "$2" "$1" "$TMP" "$3"
}

# --- fixtures (mimic real JSONL transcript records, one per line) ---
LESSON="$TMP/lesson.jsonl"
cat > "$LESSON" <<'EOF'
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"<system-reminder>claudeMd: fixed the gotcha, turns out, workaround, memory-sessions.md</system-reminder>please look at the failing parser"}]}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I fixed the parser bug - turns out the cache was stale."}]}}
EOF
UPDATED="$TMP/updated.jsonl"
cat "$LESSON" > "$UPDATED"
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"Edit","input":{"file_path":"C:\\repo\\.claude\\rules\\memory-sessions.md"}}]}}' >> "$UPDATED"
NEUTRAL="$TMP/neutral.jsonl"
cat > "$NEUTRAL" <<'EOF'
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"<system-reminder>claudeMd: fixed the gotcha, turns out, workaround</system-reminder>rename the variable please"}]}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Renamed the variable in three files. Done."}]}}
EOF
NOISE="$TMP/noise.jsonl"
cat > "$NOISE" <<'EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"The fixed-width reader in FixedWidthFileScan.scala looks fine; documented fixedwidth-custom-scala."}]}}
EOF
REJECTED="$TMP/rejected.jsonl"
cat > "$REJECTED" <<'EOF'
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"The user doesn't want to proceed with this tool use."}]}}
EOF
CORRECTED="$TMP/corrected.jsonl"
cat > "$CORRECTED" <<'EOF'
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"No, use the shared config loader for that."}]}}
EOF

# --- fixture project dirs (for hooks that read .claude/rules/) ---
PROJ="$TMP/proj"                      # healthy: small, fresh memory files
mkdir -p "$PROJ/.claude/rules"
printf '# Session Log\n\n## Open TODOs (small)\n- none\n' > "$PROJ/.claude/rules/memory-sessions.md"
printf '# Past Decisions\n' > "$PROJ/.claude/rules/memory-decisions.md"
PROJ_FAT="$TMP/projfat"               # over caps: 200-line sessions log, fresh
mkdir -p "$PROJ_FAT/.claude/rules"
for i in $(seq 1 200); do echo "- filler line $i"; done > "$PROJ_FAT/.claude/rules/memory-sessions.md"
PROJ_STALE="$TMP/projstale"           # small but stale (mtime 10 min ago)
mkdir -p "$PROJ_STALE/.claude/rules"
printf '# Session Log\n' > "$PROJ_STALE/.claude/rules/memory-sessions.md"
touch -d '-10 minutes' "$PROJ_STALE/.claude/rules/memory-sessions.md"
PROJ_REFS="$TMP/projrefs"             # memory references a file that does not exist
mkdir -p "$PROJ_REFS/.claude/rules"
printf '# Past Decisions\n\n## 2026-07-20: Parser split [T]\n- moved logic into src/missing_module.py\n' > "$PROJ_REFS/.claude/rules/memory-decisions.md"
printf '# Session Log\n' > "$PROJ_REFS/.claude/rules/memory-sessions.md"
PROJ_MOVED="$TMP/projmoved"           # referenced file moved elsewhere in a git repo
mkdir -p "$PROJ_MOVED/.claude/rules" "$PROJ_MOVED/src/parsing"
git -C "$PROJ_MOVED" init -q 2>/dev/null
printf 'x = 1\n' > "$PROJ_MOVED/src/parsing/parser.py"
git -C "$PROJ_MOVED" add src/parsing/parser.py 2>/dev/null
printf '# Past Decisions\n\n## 2026-07-20: Parser fix [T]\n- fixed the tokenizer in src/util/parser.py\n' > "$PROJ_MOVED/.claude/rules/memory-decisions.md"
printf '# Session Log\n' > "$PROJ_MOVED/.claude/rules/memory-sessions.md"
PROJ_SEEDED="$TMP/projseeded"         # still contains the template seed example
mkdir -p "$PROJ_SEEDED/.claude/rules"
printf '# Past Decisions\n\n## YYYY-MM-DD: <Example — delete once you have real entries> [Agent Name]\n' > "$PROJ_SEEDED/.claude/rules/memory-decisions.md"
printf '# Session Log\n' > "$PROJ_SEEDED/.claude/rules/memory-sessions.md"
SECRETY="$TMP/secrety.md"             # memory file containing an obvious fake token
printf '# notes\ntoken used: ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n' > "$SECRETY"
CLEANY="$TMP/cleany.md"
printf '# notes\nnothing secret here, just a git SHA 0123456789abcdef0123456789abcdef01234567\n' > "$CLEANY"

# --- Stop hook: memory-reminder.sh ---
rm -f "${TMPDIR:-/tmp}/claude-memory-reminder-st"*
check "stop: lesson w/o memory update -> block"        '"decision":"block"' "$(payload "$LESSON" st1 false | bash "$STOP_HOOK")"
check "stop: second stop same session -> quiet marker" '{}'                 "$(payload "$LESSON" st1 false | bash "$STOP_HOOK")"
check "stop: stop_hook_active -> quiet"                '{}'                 "$(payload "$LESSON" st2 true  | bash "$STOP_HOOK")"
check "stop: memory already updated -> quiet"          '{}'                 "$(payload "$UPDATED" st3 false | bash "$STOP_HOOK")"
check "stop: neutral session -> quiet"                 '{}'                 "$(payload "$NEUTRAL" st4 false | bash "$STOP_HOOK")"
check "stop: domain-vocabulary noise -> quiet"         '{}'                 "$(payload "$NOISE" st5 false | bash "$STOP_HOOK")"
check "stop: missing transcript -> quiet"              '{}'                 "$(payload "$TMP/nope.jsonl" st6 false | bash "$STOP_HOOK")"
check "stop: tool-use rejection signal -> block"       '"decision":"block"' "$(payload "$REJECTED" st7 false | bash "$STOP_HOOK")"
check "stop: 'No,' correction opener -> block"         '"decision":"block"' "$(payload "$CORRECTED" st8 false | bash "$STOP_HOOK")"
rm -f "${TMPDIR:-/tmp}/claude-memory-reminder-st"*

# --- SessionStart hook: session-context.sh ---
OUT=$(echo '{"session_id":"ss1","hook_event_name":"SessionStart","source":"startup"}' | bash "$START_HOOK")
check "start: always points at Open TODOs"             "Open TODOs"         "$OUT"
if git -C "$HERE" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  OUT2=$(echo '{}' | CLAUDE_PROJECT_DIR="$HERE" bash "$START_HOOK")
  check "start: git repo -> injects repo state"        "Session-start repo state" "$OUT2"
fi
OUT3=$(echo '{}' | CLAUDE_PROJECT_DIR="$TMP" bash "$START_HOOK"); RC3=$?
check "start: non-git dir -> still exits 0 with pointer" "Open TODOs"       "$OUT3"
[ "$RC3" -eq 0 ] && { echo "PASS: start: non-git exit code 0"; PASS=$((PASS+1)); } \
                 || { echo "FAIL: start: non-git exit code $RC3"; FAIL=$((FAIL+1)); }

# --- SessionStart hook: cap-triggered memory-discipline audit ---
OUT_FAT=$(echo '{}' | CLAUDE_PROJECT_DIR="$PROJ_FAT" bash "$START_HOOK")
check "start: sessions log over caps -> discipline audit" "Memory discipline"  "$OUT_FAT"
OUT_OK=$(echo '{}' | CLAUDE_PROJECT_DIR="$PROJ" bash "$START_HOOK")
check_not "start: sessions log under caps -> no audit"    "Memory discipline"  "$OUT_OK"

# --- PreCompact hook: save-gate (block-once) before compaction ---
pcpayload() { # pcpayload <session-id>
  printf '{"session_id":"%s","transcript_path":"%s/t.jsonl","cwd":"%s","hook_event_name":"PreCompact","trigger":"auto"}' "$1" "$TMP" "$TMP"
}
rm -f "${TMPDIR:-/tmp}/claude-memory-precompact-pc"*
check "precompact: stale memory -> block with save demand" '"decision":"block"' "$(pcpayload pc1 | CLAUDE_PROJECT_DIR="$PROJ_STALE" bash "$PRECOMPACT_HOOK")"
check "precompact: second call same session -> proceed"    '{}'                 "$(pcpayload pc1 | CLAUDE_PROJECT_DIR="$PROJ_STALE" bash "$PRECOMPACT_HOOK")"
touch "$PROJ/.claude/rules/memory-sessions.md"
check "precompact: fresh + under caps -> proceed"          '{}'                 "$(pcpayload pc2 | CLAUDE_PROJECT_DIR="$PROJ" bash "$PRECOMPACT_HOOK")"
touch "$PROJ_FAT/.claude/rules/memory-sessions.md"
check "precompact: fresh but over caps -> block (prune)"   '"decision":"block"' "$(pcpayload pc3 | CLAUDE_PROJECT_DIR="$PROJ_FAT" bash "$PRECOMPACT_HOOK")"
check "precompact: no memory files -> proceed quietly"     '{}'                 "$(pcpayload pc4 | CLAUDE_PROJECT_DIR="$TMP" bash "$PRECOMPACT_HOOK")"
rm -f "${TMPDIR:-/tmp}/claude-memory-precompact-pc"*

# --- SessionStart hook: conditional advisories (stale refs, age stamp, seeded note) ---
OUT_REFS=$(echo '{}' | CLAUDE_PROJECT_DIR="$PROJ_REFS" bash "$START_HOOK")
check "start: dead file reference in memory -> stale-ref advisory" "Stale memory references" "$OUT_REFS"
check_not "start: healthy memory -> no stale-ref advisory"         "Stale memory references" "$OUT_OK"
OUT_MOVED=$(echo '{}' | CLAUDE_PROJECT_DIR="$PROJ_MOVED" bash "$START_HOOK")
check "start: moved file -> advisory suggests new location"        "moved to src/parsing/parser.py" "$OUT_MOVED"
check "start: moved file -> still flags the old path"              "src/util/parser.py"             "$OUT_MOVED"
check "start: pointer carries memory age stamp"                    "last updated"             "$OUT_OK"
OUT_SEEDED=$(echo '{}' | CLAUDE_PROJECT_DIR="$PROJ_SEEDED" bash "$START_HOOK")
check "start: seed-example memory -> honesty note"                 "seed example"             "$OUT_SEEDED"
check_not "start: real entries -> no honesty note"                 "seed example"             "$OUT_OK"

# --- secret-scan.sh: Class-A detection, Class-B (long tokens / SHAs) stay quiet ---
SCAN_HOOK="$HERE/secret-scan.sh"
SCAN_HIT=$(bash "$SCAN_HOOK" "$SECRETY"); SCAN_HIT_RC=$?
check "scan: fake github token -> flagged"              "github-token"       "$SCAN_HIT"
[ "$SCAN_HIT_RC" -ne 0 ] && { echo "PASS: scan: findings -> exit nonzero"; PASS=$((PASS+1)); } \
                         || { echo "FAIL: scan: findings -> exit nonzero (got 0)"; FAIL=$((FAIL+1)); }
SCAN_OK=$(bash "$SCAN_HOOK" "$CLEANY"); SCAN_OK_RC=$?
[ "$SCAN_OK_RC" -eq 0 ] && { echo "PASS: scan: git SHA is not a secret -> exit 0"; PASS=$((PASS+1)); } \
                        || { echo "FAIL: scan: git SHA is not a secret -> exit $SCAN_OK_RC ($SCAN_OK)"; FAIL=$((FAIL+1)); }

# --- SessionStart hook, source=compact: the post-compaction memory flush ---
# SessionStart re-fires right after auto-/manual compaction with source:"compact";
# its stdout is injected into the model's context (documented behavior). The hook
# must then nudge a memory flush and point at the surviving on-disk transcript.
COMPACT_OUT=$(printf '{"session_id":"cc1","transcript_path":"%s","hook_event_name":"SessionStart","source":"compact"}' "$LESSON" \
  | CLAUDE_PROJECT_DIR="$TMP" bash "$START_HOOK")
check "start: source=compact -> memory-flush nudge"    "compacted"          "$COMPACT_OUT"
check "start: source=compact -> names transcript path" "$LESSON"            "$COMPACT_OUT"
check_not "start: source=startup -> no compact nudge"  "compacted"          "$OUT"

rm -rf "$TMP"
echo "---"
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
