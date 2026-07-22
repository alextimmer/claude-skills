#!/usr/bin/env bash
# Secret scan for memory files — run BEFORE committing/pushing them.
#
# Memory files are committable and get written as-you-go, which makes them the
# easiest place to leak a token. This scans with two tiers (adapted from
# mworldorg/markdown-memory's pattern set and harness-mem's SECRET_RULES;
# guiding rule: "over-redaction is acceptable; leakage is not"):
#
#   Class A (high precision -> FINDING, exit 1): provider-keyed formats that are
#     near-certainly secrets. Never auto-edited — the scan reports, the human
#     (or agent, with explicit user approval) fixes.
#   Class B (broad -> deliberately NOT flagged): generic 32+ char tokens collide
#     with git SHA-40s and UUIDs, which memory files are legitimately full of.
#
# Usage:  bash .claude/hooks/secret-scan.sh [file ...]
#         (default: .claude/rules/memory-*.md, CLAUDE.md, CLAUDE.local.md)
# Exit 0 = clean; exit 1 = at least one Class-A finding (printed as
# "<label>: <file>:<line>").

if [ "$#" -gt 0 ]; then
  FILES="$@"
else
  FILES=""
  for f in .claude/rules/memory-*.md CLAUDE.md CLAUDE.local.md; do
    [ -f "$f" ] && FILES="$FILES $f"
  done
fi
[ -n "$FILES" ] || exit 0

FOUND=0

scan() { # scan <label> <extended-regex>
  for f in $FILES; do
    HITS=$(grep -nE "$2" "$f" 2>/dev/null | cut -d: -f1)
    for line in $HITS; do
      echo "$1: $f:$line"
      FOUND=1
    done
  done
}

scan "anthropic-key"  'sk-ant-[A-Za-z0-9_-]{20,}'
scan "openai-key"     'sk-[A-Za-z0-9_-]*T3BlbkFJ[A-Za-z0-9_-]*'
scan "github-token"   'gh[posru]_[0-9A-Za-z]{36}'
scan "aws-key"        '(A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16}'
scan "slack-token"    'xox[baprs]-[0-9A-Za-z-]{10,}'
scan "google-key"     'AIza[0-9A-Za-z_-]{35}'
scan "google-oauth"   'ya29\.[0-9A-Za-z_-]{20,}'
scan "telegram-token" '[0-9]{8,10}:AA[0-9A-Za-z_-]{33}'
scan "jwt"            'eyJ[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}'
scan "private-key"    'BEGIN[ A-Z]* PRIVATE KEY'
scan "url-credentials" '[a-z][a-z0-9+.-]*://[^/@[:space:]]+:[^/@[:space:]]+@'
scan "named-secret"   '(api[_-]?key|secret|token|password|passwd)["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"'[:space:]]{10,}'

exit "$FOUND"
