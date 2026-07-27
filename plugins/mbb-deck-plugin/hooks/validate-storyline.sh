#!/usr/bin/env bash
# PostToolUse hook: auto-validate MBB storyline JSONs the moment they are
# written or edited, so Step 5 of the workflow cannot be forgotten.
#
# Contract (fail-open, like every hook in this marketplace):
#   - ALWAYS exits 0.
#   - Silent ({}) unless the written file is a *storyline*.json AND the
#     validator finds problems — then it emits {"decision":"block","reason":...}
#     which feeds the validator output straight back to the model.
#   - No Python available -> silent (the model still runs Step 5 manually).
#
# This hook fires on every Write/Edit in sessions where the plugin is enabled;
# the filename guard below makes non-storyline writes cost a single sed.

PAYLOAD=$(cat)

FILE=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"file_path":[[:space:]]*"\([^"]*\)".*/\1/p')
case "$FILE" in
  *[Ss]toryline*.json) ;;
  *) echo '{}'; exit 0;;
esac

# JSON-escaped Windows paths arrive as C:\\Users\\... — normalize to /.
FILE=$(printf '%s' "$FILE" | sed 's/\\\\/\//g')
[ -f "$FILE" ] || { echo '{}'; exit 0; }

VALIDATOR="$CLAUDE_PLUGIN_ROOT/skills/mbb-deck/scripts/validate_storyline.py"
[ -f "$VALIDATOR" ] || { echo '{}'; exit 0; }

# Find a WORKING python (the Windows Store alias stub exists but cannot run).
PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import sys" >/dev/null 2>&1; then
    PY="$cand"
    break
  fi
done
[ -n "$PY" ] || { echo '{}'; exit 0; }

"$PY" - "$FILE" "$VALIDATOR" <<'PYEOF'
import json, subprocess, sys

storyline, validator = sys.argv[1], sys.argv[2]
try:
    r = subprocess.run([sys.executable, validator, storyline],
                       capture_output=True, text=True, timeout=15)
except Exception:
    print("{}")
    sys.exit(0)

if r.returncode == 0:
    print("{}")
else:
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    reason = ("validate_storyline.py flagged the storyline you just wrote. "
              "Fix the ERRORs (and ideally the WARNINGs) before rendering "
              "(workflow Step 5):\n" + out[:3000])
    print(json.dumps({"decision": "block", "reason": reason}))
sys.exit(0)
PYEOF
exit 0
