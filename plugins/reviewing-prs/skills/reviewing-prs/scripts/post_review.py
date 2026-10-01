"""Post an approved review as comment threads on Azure DevOps, GitHub or GitLab.

Usage (from inside the repository checkout):

    python scripts/post_review.py --dry-run review.json     # print EXACTLY what would be posted
    python scripts/post_review.py review.json               # post it (only after the user said yes)

The script never votes / approves / requests changes: the vote is a human act in the UI. It
batches everything into one posting step: Azure DevOps threads, one GitHub pending review that
is submitted as COMMENT, or GitLab draft notes published in bulk.

review.json:
{
  "pr": 123,
  "head": "<sha the anchors refer to>",          // required for GitHub and GitLab
  "base": "<sha>", "start": "<sha>",              // GitLab only (diff_refs; start defaults to base)
  "recommended_vote": "Wait for author",          // shown in the preview, never applied
  "summary": "markdown for the general thread (verdict + summary table + could-not-verify)",
  "comments": [
    {"path": "src/x.py", "line": 42, "start_line": null, "severity": "MAJOR",
     "body": "markdown; may contain a ```suggestion block", "reply_to": null}
  ]
}
`reply_to` is an existing thread id (ADO), review-comment id (GitHub) or discussion id (GitLab):
the comment becomes a reply instead of a new thread, so one topic never gets two threads.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hosts import Client, Host, detect, utf8_stdout  # noqa: E402

SEVERITIES = ("MAJOR", "MEDIUM", "MINOR", "NOTE")


def load(path: str) -> dict:
    review = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = []
    if not isinstance(review.get("pr"), int):
        problems.append("'pr' must be an integer")
    comments = review.get("comments") or []
    for i, c in enumerate(comments, 1):
        if not (c.get("body") or "").strip():
            problems.append(f"comment {i}: empty body")
        if c.get("reply_to") is None:
            if not c.get("path") or not isinstance(c.get("line"), int):
                problems.append(f"comment {i}: needs 'path' and integer 'line' (or 'reply_to')")
        if c.get("start_line") is not None and c.get("line") is not None and c["start_line"] > c["line"]:
            problems.append(f"comment {i}: start_line must be <= line")
        if c.get("severity") and c["severity"] not in SEVERITIES:
            problems.append(f"comment {i}: severity must be one of {SEVERITIES}")
    if not comments and not (review.get("summary") or "").strip():
        problems.append("nothing to post: no comments and no summary")
    if problems:
        sys.exit("review.json is not valid:\n  " + "\n  ".join(problems))
    return review


def preview(host: Host, review: dict) -> None:
    head = (review.get("head") or "")[:10] or "-"
    print(f"== Posting preview: {host.label} {host.slug} {host.noun} {review['pr']} (head {head}) ==")
    print(f"   {host.pr_url(review['pr'])}")
    for i, c in enumerate(review.get("comments") or [], 1):
        where = f"reply to {c['reply_to']}" if c.get("reply_to") is not None else "new thread"
        span = f"{c['start_line']}-{c['line']}" if c.get("start_line") else str(c.get("line"))
        anchor = f"{c.get('path')}:{span}" if c.get("path") else "(general)"
        print(f"\n[{i}] {c.get('severity', 'NOTE'):6s} {anchor}   ({where})")
        print(c["body"].rstrip())
    if (review.get("summary") or "").strip():
        print("\n== General thread ==")
        print(review["summary"].rstrip())
    print("\n== Not posted by this script: the vote. Recommended: "
          f"{review.get('recommended_vote') or '(none given)'} -> cast it in the UI. ==")


# --- Azure DevOps --------------------------------------------------------------------------

def post_ado(c: Client, host: Host, review: dict) -> None:
    api = host.pr_api(review["pr"])
    for i, cm in enumerate(review.get("comments") or [], 1):
        if cm.get("reply_to") is not None:
            thread = c.get(f"{api}/threads/{cm['reply_to']}")
            parent = min(x["id"] for x in thread.get("comments", []) if not x.get("isDeleted"))
            c.post(f"{api}/threads/{cm['reply_to']}/comments",
                   {"content": cm["body"], "parentCommentId": parent, "commentType": 1})
            print(f"[{i}] replied in thread {cm['reply_to']}")
            continue
        start = cm.get("start_line") or cm["line"]
        body = {
            "comments": [{"parentCommentId": 0, "content": cm["body"], "commentType": 1}],
            "status": 1,  # active
            "threadContext": {
                "filePath": "/" + cm["path"].lstrip("/"),
                "rightFileStart": {"line": start, "offset": 1},
                "rightFileEnd": {"line": cm["line"], "offset": 1},
            },
        }
        t = c.post(f"{api}/threads", body)
        print(f"[{i}] thread {t['id']} on {cm['path']}:{cm['line']}")
    if (review.get("summary") or "").strip():
        t = c.post(f"{api}/threads",
                   {"comments": [{"parentCommentId": 0, "content": review["summary"], "commentType": 1}],
                    "status": 1})
        print(f"general thread {t['id']}")


# --- GitHub --------------------------------------------------------------------------------

def post_github(c: Client, host: Host, review: dict) -> None:
    api = host.pr_api(review["pr"])
    if not review.get("head"):
        sys.exit("GitHub needs 'head' (the PR head sha from fetch_pr.py's SRC line)")
    inline, replies = [], []
    for cm in review.get("comments") or []:
        (replies if cm.get("reply_to") is not None else inline).append(cm)
    comments = []
    for cm in inline:
        entry = {"path": cm["path"], "line": cm["line"], "side": "RIGHT", "body": cm["body"]}
        if cm.get("start_line"):
            entry.update({"start_line": cm["start_line"], "start_side": "RIGHT"})
        comments.append(entry)
    summary = (review.get("summary") or "").strip() or "Review comments posted inline."
    if comments or summary:
        pending = c.post(f"{api}/reviews", {"commit_id": review["head"], "comments": comments})
        print(f"pending review {pending['id']} ({pending.get('state')}) with {len(comments)} comment(s)")
        submitted = c.post(f"{api}/reviews/{pending['id']}/events", {"event": "COMMENT", "body": summary})
        print(f"submitted as COMMENT: {submitted.get('html_url')}")
    for cm in replies:
        r = c.post(f"{api}/comments/{cm['reply_to']}/replies", {"body": cm["body"]})
        print(f"replied to review comment {cm['reply_to']}: {r.get('html_url')}")


# --- GitLab --------------------------------------------------------------------------------

def post_gitlab(c: Client, host: Host, review: dict) -> None:
    api = host.pr_api(review["pr"])
    if not review.get("head") or not review.get("base"):
        sys.exit("GitLab needs 'head' and 'base' (and optionally 'start') from fetch_pr.py's diff_refs line")
    start = review.get("start") or review["base"]
    n = 0
    for i, cm in enumerate(review.get("comments") or [], 1):
        body: dict = {"note": cm["body"]}
        if cm.get("reply_to") is not None:
            body["in_reply_to_discussion_id"] = cm["reply_to"]
        else:
            body["position"] = {
                "position_type": "text", "base_sha": review["base"], "head_sha": review["head"],
                "start_sha": start, "new_path": cm["path"], "old_path": cm["path"], "new_line": cm["line"],
            }
        d = c.post(f"{api}/draft_notes", body)
        n += 1
        print(f"[{i}] draft note {d['id']}")
    if (review.get("summary") or "").strip():
        d = c.post(f"{api}/draft_notes", {"note": review["summary"]})
        n += 1
        print(f"general draft note {d['id']}")
    if n:
        c.post(f"{api}/draft_notes/bulk_publish", {})
        print(f"published {n} draft note(s) in one batch")


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("review", help="path to review.json")
    parser.add_argument("--dry-run", action="store_true", help="print what would be posted; touch nothing")
    parser.add_argument("--remote", default="origin")
    args = parser.parse_args()

    host = detect(args.remote)
    review = load(args.review)
    preview(host, review)
    if args.dry_run:
        print("\n(dry run: nothing was posted)")
        return
    print("\n== Posting ==")
    client = Client(host)
    {"ado": post_ado, "github": post_github, "gitlab": post_gitlab}[host.kind](client, host, review)
    print(f"done: {host.pr_url(review['pr'])}")


if __name__ == "__main__":
    main()
