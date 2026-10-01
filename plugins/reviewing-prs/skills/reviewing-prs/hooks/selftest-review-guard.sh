#!/usr/bin/env bash
# Machine-checks review-guard.sh against simulated PreToolUse payloads. Exit 0 = all pass.
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$HERE/review-guard.sh"
PASS=0; FAIL=0
S="rg-selftest-$$"
rm -f "${TMPDIR:-/tmp}/claude-review-dryrun-${S}-"*

bash_payload() { printf '{"session_id":"%s","tool_name":"Bash","tool_input":{"command":"%s"}}' "$S" "$1"; }
skill_payload() { printf '{"session_id":"%s","tool_name":"Skill","tool_input":{"skill":"%s","args":"%s"}}' "$S" "$1" "$2"; }

expect_deny()  { out=$(printf '%s' "$2" | bash "$HOOK"); if printf '%s' "$out" | grep -q '"deny"'; then echo "PASS: $1"; PASS=$((PASS+1)); else echo "FAIL: $1 (expected deny, got: $out)"; FAIL=$((FAIL+1)); fi; }
expect_allow() { out=$(printf '%s' "$2" | bash "$HOOK"); if [ -z "$out" ]; then echo "PASS: $1"; PASS=$((PASS+1)); else echo "FAIL: $1 (expected allow, got: $out)"; FAIL=$((FAIL+1)); fi; }

expect_deny  "skill code-review --comment"            "$(skill_payload code-review '--comment 44517')"
expect_deny  "skill security-review --fix"            "$(skill_payload security-review '--fix')"
expect_allow "skill code-review plain"                "$(skill_payload code-review 'high 44517')"
expect_allow "bash unrelated"                         "$(bash_payload 'git status')"
expect_deny  "post without dry run"                   "$(bash_payload 'python scripts/post_review.py review.json')"
expect_allow "post dry run passes + sets marker"      "$(bash_payload 'python scripts/post_review.py --dry-run review.json')"
expect_allow "post after dry run of same file"        "$(bash_payload 'python scripts/post_review.py review.json')"
expect_deny  "post after dry run of a DIFFERENT file" "$(bash_payload 'python scripts/post_review.py other.json')"
expect_deny  "gh pr review"                           "$(bash_payload 'gh pr review 7 --approve')"
expect_deny  "powershell gh pr review"                "$(printf '{"session_id":"%s","tool_name":"PowerShell","tool_input":{"command":"gh pr review 7 --approve"}}' "$S")"
expect_deny  "ado reviewers api"                      "$(bash_payload 'curl -X PUT https://dev.azure.com/o/p/_apis/git/repositories/r/pullRequests/7/reviewers/me')"
expect_allow "other tool name"                        "$(printf '{"session_id":"%s","tool_name":"Read","tool_input":{"file_path":"x"}}' "$S")"

rm -f "${TMPDIR:-/tmp}/claude-review-dryrun-${S}-"*
echo "---"; echo "$PASS passed, $FAIL failed"; [ "$FAIL" -eq 0 ]
