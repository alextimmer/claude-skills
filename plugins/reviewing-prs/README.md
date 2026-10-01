# reviewing-prs

Pull-request and merge-request reviews for **Azure DevOps, GitHub and GitLab** with one method
and a hard approval gate. The host is detected from the git remote; the scripts talk REST with
the token from `git credential fill`, so no `gh`, `glab` or `az` is needed.

## What a review looks like

Every review has the same shape, every time: header (iteration, base, source), *the goal as I
read it*, verdict with the vote to cast, what was verified rather than taken on faith, then one
block per finding ordered by severity (🔴 MAJOR · 🟠 MEDIUM · 🟡 MINOR · ✅ verified), a summary
table, housekeeping. Each finding block carries:

- an anchor with the **full repo path and three links**: the file at the PR head positioned on
  the line, the PR's own Files view, and the IDE-relative link;
- the **in-depth explanation** for the reviewer: mechanism, impact, evidence (commands run,
  outputs seen);
- when the finding rests on a product fact, a **claims table** (confirmed / contradicted /
  undocumented) and **Sources** with page, section, verbatim quote and fetch date;
- the **paste-ready comment** for the author, with a one-click `suggestion` block when the fix
  is concrete.

## Three principles

1. **Review the authoritative changeset.** Iteration base → source, two-dot. A diff against the
   target tip attributes the target branch's own commits to the PR.
2. **Nothing reaches the PR unseen.** Posting is opt-in: Draft → Show (dry run) → Approve (one
   yes/no) → Post, one batch, one notification. The vote is never cast by a tool.
3. **One method, many finding generators.** The skill owns method, severity, anchors, vote and
   posting. Domain skills, the built-in `code-review` and `security-review`, and documentation
   lookups are generators. Which ones apply per path is **project data** in
   `.claude/review-routing.md`, proposed by Discovery on the first review, written only after
   the requester confirms, never hard-coded in the skill.

## Install

```bash
/plugin marketplace add alextimmer/claude-skills
/plugin install reviewing-prs@claude-skills
/reload-plugins
```

The approval gate is a PreToolUse hook declared in the skill's own frontmatter
(`skills/reviewing-prs/hooks/review-guard.sh`, located through `${CLAUDE_PLUGIN_ROOT}`, which is the plugin root for a plugin install and the skill's own directory for a bare `.claude/skills/` copy; the hook command handles both). Claude Code
registers it the first time the skill is invoked in a session and keeps it for the rest of the
session; nothing to wire, no `hooks.json`, works identically when the folder is copied into a
project's `.claude/skills/`. It denies `code-review`/`security-review` with `--comment` or
`--fix`, `post_review.py` without a prior `--dry-run` of the same review file, and terminal
votes. Check with `/hooks` after the first review. Self-test:
`bash skills/reviewing-prs/hooks/selftest-review-guard.sh` (12 cases).

Requirements: Python 3.12+ with PyYAML (`pip install pyyaml`; only `render_review.py` needs it, the other scripts are standard library), git with a credential helper that holds a
token for the host (sign in once with `git fetch`), Git Bash on Windows for the hook.

## First review in a repository

```
review PR 1234
```

The skill fetches the PR, then, finding no `.claude/review-routing.md`, runs Discovery: it
matches the available skill descriptions against the repository layout, proposes a routing
table (repo-local skills first, then plugin skills, `code-review` always, `security-review`
for credential-bearing paths), and asks. On yes it writes the file, creating `.claude/` if
needed; whether that file is committed or excluded is the requester's choice. In a repository
with no matching skills the table is just `code-review`, and the review runs on method plus
general knowledge.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/fetch_pr.py <id> [--diff]` | metadata, description, iterations/versions, human threads, `BASE <sha> SRC <sha>` |
| `scripts/anchor.py --pr <id> --sha <SRC> path:line …` | the three clickable links per anchor |
| `scripts/render_review.py review.yaml --check` | ONE source -> `review.md` (template, all links) + `review.json` (posting payload); `--check` verifies every anchor on SRC and in the diff. Schema: `review.example.yaml` |
| `scripts/post_review.py [--dry-run] review.json` | preview, then post: ADO threads / GitHub pending review submitted as COMMENT / GitLab draft notes published in bulk; `reply_to` for existing threads |
| `scripts/hosts.py` | host detection, credentials, HTTP, URL forms |

## Files

```
skills/reviewing-prs/
  SKILL.md                      the method
  review-template.md            the output contract (review, re-review, paste list, review.json)
  review-routing.example.md     format of the per-project routing file
  scripts/                      fetch_pr.py, anchor.py, render_review.py, post_review.py, hosts.py,
                                review.example.yaml, review.example.json
  hooks/                        review-guard.sh + selftest, registered by SKILL.md frontmatter
```

## Origin

Started as an Azure-DevOps-only review skill; merged with the approval-gate workflow of
[aidankinzett/claude-git-pr-skill](https://github.com/aidankinzett/claude-git-pr-skill)
(github-pr-review) and generalized to three hosts. Routing, discovery, documentation checks
and the hook were added in October 2026.
