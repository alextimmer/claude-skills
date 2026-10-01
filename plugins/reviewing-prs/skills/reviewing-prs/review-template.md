# Review output template

Use these sections, in this order. Fill every one; write "none" rather than omit. Optional blocks
are marked OPTIONAL and appear only when their content exists. Start the message with one line
naming the audience, e.g. `Written for: you, to paste into the Azure DevOps PR.` (that line is for
the requester, not part of the review). Use the host's words: PR (Azure DevOps, GitHub) or MR
(GitLab); thread / review comment / discussion.

Anchors: ALWAYS the full repo path and the three links from
`python scripts/anchor.py --pr <id> --sha <SRC> path:line` (host file view at SRC on that line,
the PR's Files view, the IDE-relative link). Never a bare file name.

```markdown
# Review — <host> <repo> PR <id>
**"<title>"** · `<source>` → `<target>` · iteration <n> (ADO) | version <n> (GitLab) |
head after <k> force-pushes (GitHub) · base `<sha7>`(stable | moved: rebased),
src `<sha7>` · <N> files · <M> threads

## The goal (as I read it)

**This PR.** One paragraph restating the intent in your own words, including the design
decision that shapes the change.

**Where it sits.** The surrounding work, from `fetch_pr.py`'s *Related PRs* block and the
description/threads: the overarching problem the series of PRs is solving, which part of it
*this* PR takes on, and the chain. Then the table (rendered from the `related:` list in
`review.yaml`; one row per open PR in the series including this one, in merge order):

| Merge order | PR | Branch → target | Relation to this PR | Overlap | State |
|---|---|---|---|---|---|
| 1 | PR <id> <title> | `src → tgt` | this one stacks on it (contains its head `<sha7>`) | inherited | iteration n, vote |
| 2 | **PR <this> (this)** | `src → tgt` | — | | iteration n |
| 3 | PR <id> <title> | `src → tgt` | stacked on this one | inherited | iteration n |
|   | PR <id> <title> | `src → tgt` | sibling | k files | … |

Relation words: "this one stacks on it", "stacked on this one", "sibling, k overlapping files",
"unrelated". When nothing is related, write "standalone" in the prose and omit the table.

## Verdict: **Approve | Approve with suggestions | Request changes.** One sentence why.
Recommended vote in the host's vocabulary (see SKILL.md table), e.g. *ADO: Wait for author*.

## What I verified rather than took on faith ✅
- Claim → where it is proven: **[`full/path:line`](<web at SRC>)** · [in PR](…) · [local](path#Lnn).
  One bullet per checked claim.
- Product claim → documentation, footnote [S<n>] into the review-level Sources index.
- Keep anything taken from the description *out* of this list.

---

## 🔴 MAJOR — <one-line claim>
**[`full/path:line`](<web at SRC>)** · [in PR](<PR files url>) · [local](full/path#Lnn)
(every anchor: a code line on the PR head, present in the diff)

MANDATORY — the in-depth explanation for the requester, before anything pasteable: the
mechanism (what happens, step by step, with the concrete names from the diff), why it matters
(what breaks, for whom, when), and the evidence (commands run, outputs seen, lines read on SRC).
One or more paragraphs; this is where the reasoning lives. The paste-ready comment below is the
condensed version for the author, never a substitute for this.

OPTIONAL — claims table, in addition to the explanation, only when the finding rests on product
facts that were checked against documentation:

| Claim in the code / description | Verdict | Source |
|---|---|---|
| "<quoted claim>" | ✅ confirmed · ❌ contradicted · ⚠️ undocumented | [S<n>] |

Then the paste-ready comment. It carries at most the ONE url the author needs, never the
quote block:

> **[`full/path:line`](<web at SRC>)** — Text the reader pastes as-is. When the fix is concrete,
> a suggestion block the author can apply with one click (it replaces the anchored line(s)):
> ```suggestion
> the complete replacement line(s), correctly indented
> ```
> Otherwise a plain code snippet if it helps.

OPTIONAL — **Sources** (fetched <date>), only when something was fetched for this finding:
1. <Docs title>, section "<heading>": "<verbatim sentence>" <url>
   Official documentation first. A vendor blog or community post only when the docs are silent,
   labelled "(community)". Docs that disagree with each other: cite both pages, say which one
   is the reference, and which value the code assumes.

OPTIONAL — `Found by: <generator>[, <generator>]` one line, only when a generator skill
(code-review, security-review, a routed domain skill) proposed this finding and it survived
verification. Absent means the method found it.

## 🟠 MEDIUM — …
## 🟡 MINOR — …
(repeat; order by severity; unchanged files → anchor on the changed test/file that must
grow, or "(general)")

---

## Summary

| File:line | Severity | Finding | Follow-up |
|---|---|---|---|
| `full/path:line` | 🔴 MAJOR | one line | fix in PR |
| `full/path:line` | 🟠 MEDIUM 🔒 | one line | ticket? |
| … | ✅ | verified items, one row | |

🔒 after the severity marks a finding that came from `security-review`. `ticket?` in
Follow-up marks a finding the review judges to belong in the backlog rather than this PR:
deferred by the author, cross-cutting, or out of the PR's scope. Use it sparingly; most rows
say "fix in PR" or stay empty.

**Verdict** repeated and expanded: what must happen before completing. Name the vote to cast.

## Housekeeping
Open threads to resolve (ids), missing reviewers, description lines to update, merge order
for stacked PRs.

**Generators consulted:** which routing rows applied (skills, `code-review` effort,
`security-review`), which were skipped as `heavy` and why, and the routing file's `confirmed`
line. "none (no routing file)" when the review ran on method and general knowledge alone.

**Retracted from generators:** each generator finding that did not survive verification, one
line each: `<generator>: <claim> -> <why dropped>` (line not in diff, claim false on SRC,
duplicate of finding X, false positive). "none" when everything survived.

**Sources:** S1 <Docs title> <url> · S2 … — the review-level index of every source cited
above. "none" when nothing was fetched.

**Could not verify:** what needed a cluster/CI/feed you had no access to, author-measured
figures you did not reproduce, and that you ran nothing locally unless you did.

OPTIONAL — **Follow-up tickets?** <k> finding(s) marked `ticket?` in the Summary. Say
"create tickets" to see drafts (one per finding: title, body with anchor and paste-ready text,
the PR link); nothing is created before the drafts are shown and approved. This block appears
only when at least one finding is marked.
```

## Re-review variant

Replace the findings block with a table, then any new findings:

```markdown
| Prior finding | Iteration-<n> anchor | Status |
|---|---|---|
| 🟠 <claim> | **[`full/path:line`](<web>)** · [local](…) | ✅ Fixed | ⏸ Declined, accepted because … | ❌ Still open | 🎫 Ticket <id> |
```

State retractions plainly ("I called X a typo; the author's reason is correct because …").

## "Where does this go?" answer

A numbered paste list, nothing else. Every entry carries the full repo path and the three links
from `anchor.py`, so the reader clicks to the line, pastes, done:

```markdown
1. **[`full/path/in/repo.sql:line`](<web at SRC>)** · [in PR](<PR files url>) · [local](full/path/in/repo.sql#Lnn) — <severity> — <the comment text>
2. General (Overview tab) — <the comment text>
```

Confirm each line is in the diff and is code. Suggest a reply into an existing thread when
one already covers the topic — never open a second thread on the same point.

## Posting variant (`review.json`)

When asked to post, the review above is the source; `review.json` is derived from it:

- one `comments[]` entry per 🔴/🟠/🟡 finding: `path`, `line` (and `start_line` for a
  range), `severity`, `body` = the paste-ready comment verbatim (suggestion block included,
  at most one url, never the Sources block);
- a finding that continues an existing thread → `reply_to` = that thread/comment/discussion id
  from `fetch_pr.py`, no `path`/`line`;
- `summary` = Verdict + Summary table + Could not verify (the general thread). The goal
  paragraph, the evidence, Sources and Generators stay in the paste-ready review, not on the PR;
- `recommended_vote` = the vote named in the Verdict; it is shown in the preview and cast by
  the reader, never by the script;
- `head` = SRC from `fetch_pr.py`; GitLab also `base` and `start` from its `diff_refs` line.

The dry-run output is the approval preview. Show it unchanged; post only after "Yes, post it".
