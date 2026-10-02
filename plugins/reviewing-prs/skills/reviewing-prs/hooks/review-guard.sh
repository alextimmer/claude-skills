#!/usr/bin/env bash
# PreToolUse hook backing the reviewing-prs approval gate (matchers: Bash, Skill).
#
# Denies, with a model-facing reason:
#   1. code-review / security-review invoked with --comment or --fix (posting and fixing go
#      through the reviewing-prs gate, never through the generator).
#   2. post_review.py WITHOUT --dry-run unless a dry run of the SAME review file ran earlier in
#      this session (marker in $TMPDIR). A dry run always passes and sets the marker.
#   3. Direct vote/approve calls on the host: `gh pr review`, `glab mr approve|note`, an Azure
#      DevOps reviewers API PUT/PATCH. The vote is a human act in the UI.
# Allows everything else (prints nothing, exit 0).
#
# Input (stdin): PreToolUse JSON {session_id, tool_name, tool_input:{command | skill, args}, ...}
# Output: {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny",
#          "permissionDecisionReason":"..."}} to deny; empty to allow.

PAYLOAD=$(cat)

SESSION=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"session_id":"\([^"]*\)".*/\1/p')
TOOL=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"tool_name":"\([^"]*\)".*/\1/p')

# The text to inspect: Bash -> tool_input.command; Skill -> tool_input.skill + tool_input.args.
case "$TOOL" in
  Bash)  TEXT=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"command":"\(.*\)".*/\1/p') ;;
  Skill) TEXT=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"skill":"\([^"]*\)".*/\1/p')" "$(printf '%s' "$PAYLOAD" | sed -n 's/.*"args":"\([^"]*\)".*/\1/p') ;;
  *)     exit 0 ;;
esac

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1"
  exit 0
}

# 1. generators must not post or fix
if printf '%s' "$TEXT" | grep -qE '(^|[^a-z-])(code-review|security-review)([^a-z-]|$)' \
   && printf '%s' "$TEXT" | grep -qE -- '--(comment|fix)([^a-z]|$)'; then
  deny "reviewing-prs gate: code-review/security-review are finding generators here; run them without --comment/--fix. Posting goes through post_review.py after the dry-run preview is approved."
fi

# 2. post_review.py: dry run first, same review file
if printf '%s' "$TEXT" | grep -q 'post_review\.py'; then
  REVIEW=$(printf '%s' "$TEXT" | grep -oE '[^ "]+\.json' | head -1 | sed 's#.*[\\/]##')
  MARKER="${TMPDIR:-/tmp}/claude-review-dryrun-${SESSION:-nosession}-${REVIEW:-unknown}"
  if printf '%s' "$TEXT" | grep -qE -- '--dry-run'; then
    touch "$MARKER" 2>/dev/null
    exit 0
  fi
  if [ ! -f "$MARKER" ]; then
    deny "reviewing-prs gate: run post_review.py --dry-run on this review file first, show the preview, and post only after the requester said yes."
  fi
  exit 0
fi

# 3. no votes from the terminal
if printf '%s' "$TEXT" | grep -qE 'gh pr review|glab mr (approve|note)|/pullRequests/[0-9]+/reviewers/' ; then
  deny "reviewing-prs gate: the vote is cast by the reader in the host UI, never from a tool call."
fi

exit 0
