"""Print what a review of a pull/merge request starts from (Azure DevOps, GitHub or GitLab).

Usage (from inside the repository checkout):

    python scripts/fetch_pr.py <pr-id> [--diff] [--remote origin]

The host, organisation/owner, project and repository are derived from the git remote URL; the
token comes from ``git credential fill`` (Git Credential Manager), so nothing is hard-coded.
Prints the PR metadata and description, every iteration's (ADO) / version's (GitLab) base and
source commit, the human comment threads, and finally one line ``BASE <sha> SRC <sha>``. With
``--diff`` it also fetches both commits and prints ``git diff --stat BASE SRC``.

BASE is the commit the changeset is diffed against, two-dot: ADO's iteration commonRefCommit,
GitLab's version base_commit_sha, and for GitHub (which has no iterations) the merge base of the
head and the target branch, which is what the GitHub UI shows.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hosts import Client, Host, detect, utf8_stdout  # noqa: E402


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def build_validation(c: Client, h: Host, pr_id: int, src: str) -> None:
    """What the host's own checks say about this PR, and whether they evaluated the current SRC.
    Fast mode cites this instead of running parse/render locally; full mode gets it as extra
    context. Degrades to 'unavailable' on any API error."""
    section("build validation")
    try:
        if h.kind == "ado":
            proj = c.get(f"https://dev.azure.com/{h.org}/_apis/projects/{h.project}")["id"]
            art = f"vstfs:///CodeReview/CodeReviewId/{proj}/{pr_id}"
            ev = c.get(f"https://dev.azure.com/{h.org}/{h.project}/_apis/policy/evaluations"
                       f"?artifactId={art}&api-version=7.1-preview.1")
            rows = ev.get("value", [])
            if not rows:
                print("no branch policies evaluated for this PR")
            for e in rows:
                cfg = e.get("configuration", {})
                typ = cfg.get("type", {}).get("displayName", "?")
                ctx = e.get("context") or {}
                line = f"{typ:28s} {str(e.get('status')):9s} blocking={cfg.get('isBlocking')}"
                if typ == "Build":
                    evaluated = ctx.get("lastMergeSourceCommitId", "")
                    match = "yes" if evaluated == src else f"NO (evaluated {evaluated[:10] or '-'}, SRC is {src[:10]})"
                    line += (f" | definition {cfg.get('settings', {}).get('buildDefinitionId')} "
                             f"| evaluated SRC: {match}")
                print(line)
        elif h.kind == "github":
            runs = c.get(f"{h.api}/commits/{src}/check-runs").get("check_runs", [])
            for r in runs:
                print(f"check-run {r.get('name'):28s} {str(r.get('status')):11s} {str(r.get('conclusion')):10s} | on SRC: yes")
            st = c.get(f"{h.api}/commits/{src}/status")
            for s in st.get("statuses", []):
                print(f"status    {s.get('context'):28s} {str(s.get('state')):11s} | on SRC: yes")
            if not runs and not st.get("statuses"):
                print("no check-runs or statuses on SRC")
        else:
            pipes = c.get_all(f"{h.pr_api(pr_id)}/pipelines")
            if not pipes:
                print("no pipelines for this MR")
            for p in pipes[:5]:
                match = "yes" if p.get("sha") == src else f"NO (ran on {str(p.get('sha'))[:10]})"
                print(f"pipeline {p.get('id')} {str(p.get('status')):10s} | on SRC: {match} | {p.get('web_url', '')}")
    except SystemExit as err:
        print(f"unavailable ({err})")


def related_prs(c: Client, h: Host, pr_id: int, base: str, src: str, remote: str) -> None:
    """Every other open PR/MR with its relation to this one: stacked (git ancestry between the
    heads) or sibling (overlapping changed files). Heads are fetched locally; failures degrade to
    'unknown' rather than aborting the review."""
    others: list[tuple[int, str, str, str, str]] = []  # id, title, source, target, head sha
    if h.kind == "ado":
        data = c.get(f"{h.api}/pullrequests?searchCriteria.status=active&$top=100")
        for p in data.get("value", []):
            if p["pullRequestId"] == pr_id:
                continue
            others.append((p["pullRequestId"], p.get("title", ""), p["sourceRefName"].replace("refs/heads/", ""),
                           p["targetRefName"].replace("refs/heads/", ""), p["lastMergeSourceCommit"]["commitId"]))
    elif h.kind == "github":
        for p in c.get_all(f"{h.api}/pulls?state=open"):
            if p["number"] == pr_id:
                continue
            others.append((p["number"], p.get("title", ""), p["head"]["ref"], p["base"]["ref"], p["head"]["sha"]))
    else:
        for p in c.get_all(f"{h.api}/merge_requests?state=opened"):
            if p["iid"] == pr_id:
                continue
            others.append((p["iid"], p.get("title", ""), p["source_branch"], p["target_branch"], p["sha"]))
    section(f"related {h.noun}s ({len(others)} other open)")
    if not others:
        print("none: standalone")
        return
    mine = set(_git("diff", "--name-only", base, src).splitlines())
    for oid, title, source, target, head in others:
        subprocess.run(["git", "fetch", "-q", remote, head], capture_output=True)
        if _git("cat-file", "-t", head) != "commit":
            print(f"{h.noun} {oid} | {source} -> {target} | relation unknown (head not fetchable) | {title}")
            continue
        if subprocess.run(["git", "merge-base", "--is-ancestor", src, head]).returncode == 0:
            rel = f"STACKED ON THIS ONE (its head contains {src[:7]}); merge this first"
        elif subprocess.run(["git", "merge-base", "--is-ancestor", head, src]).returncode == 0:
            rel = f"THIS ONE STACKS ON IT (contains its head {head[:7]}); merge {oid} first, then rebase"
        else:
            mb = _git("merge-base", head, f"{remote}/{target}") or base
            theirs = set(_git("diff", "--name-only", mb, head).splitlines())
            overlap = len(mine & theirs)
            rel = f"sibling, {overlap} overlapping file(s)" if overlap else "unrelated (no overlapping files)"
        print(f"{h.noun} {oid} | {source} -> {target} | {rel} | {title}")


def fetch_ado(c: Client, h: Host, pr_id: int) -> tuple[str, str]:
    api = h.pr_api(pr_id)
    pr = c.get(api)
    print(f"title   : {pr.get('title')}")
    print(f"status  : {pr.get('status')} | mergeStatus: {pr.get('mergeStatus')} | draft: {pr.get('isDraft')}")
    print(f"branches: {pr.get('sourceRefName')} -> {pr.get('targetRefName')}")
    print(f"author  : {pr.get('createdBy', {}).get('displayName')}")
    print(f"votes   : {[(r['displayName'], r['vote']) for r in pr.get('reviewers', [])]}")
    merge_target = (pr.get("lastMergeTargetCommit") or {}).get("commitId", "-")[:10]
    print(f"merge target commit (stale if older than target head): {merge_target}")
    print("--- description ---")
    print(pr.get("description") or "(none)")
    print("--- end description ---\n")

    iterations = c.get(f"{api}/iterations")["value"]
    for it in iterations:
        print(f"iteration {it['id']}: src={it['sourceRefCommit']['commitId'][:10]} "
              f"base={it['commonRefCommit']['commitId'][:10]}")
    last = iterations[-1]
    base, src = last["commonRefCommit"]["commitId"], last["sourceRefCommit"]["commitId"]
    if len({it["commonRefCommit"]["commitId"] for it in iterations}) > 1:
        print("NOTE: base moved between iterations -> rebased; diff only against the last base")

    human = 0
    for thread in c.get(f"{api}/threads")["value"]:
        if thread.get("isDeleted"):
            continue
        comments = [x for x in thread.get("comments", [])
                    if x.get("commentType") != "system" and not x.get("isDeleted")]
        if not comments:
            continue
        human += 1
        ctx = thread.get("threadContext") or {}
        line = (ctx.get("rightFileStart") or {}).get("line")
        section(f"thread {thread['id']} | {thread.get('status')} | {ctx.get('filePath', '(general)')}:{line}")
        for x in comments:
            print(f"--- [{x.get('author', {}).get('displayName', '?')}] ---\n{(x.get('content') or '').strip()}\n")
    print(f"({human} human threads)")
    return base, src


def fetch_github(c: Client, h: Host, pr_id: int) -> tuple[str, str]:
    api = h.pr_api(pr_id)
    pr = c.get(api)
    print(f"title   : {pr.get('title')}")
    print(f"status  : {pr.get('state')} | mergeable: {pr.get('mergeable')} ({pr.get('mergeable_state')}) "
          f"| draft: {pr.get('draft')}")
    print(f"branches: {pr['head']['label']} -> {pr['base']['label']}")
    print(f"author  : {pr.get('user', {}).get('login')}")
    reviews = c.get_all(f"{api}/reviews")
    latest: dict[str, str] = {}
    for r in reviews:
        if r.get("state") not in ("COMMENTED", "PENDING"):
            latest[r["user"]["login"]] = r["state"]
    print(f"reviews : {sorted(latest.items())}")
    print("--- description ---")
    print(pr.get("body") or "(none)")
    print("--- end description ---\n")

    src = pr["head"]["sha"]
    compare = c.get(f"{h.api}/compare/{pr['base']['sha']}...{src}")
    base = compare["merge_base_commit"]["sha"]
    print(f"head {src[:10]} | target tip {pr['base']['sha'][:10]} | merge base {base[:10]} "
          f"| {pr.get('commits')} commits, {pr.get('changed_files')} files")
    events = c.get_all(f"{h.api}/issues/{pr_id}/timeline")
    pushes = [e for e in events if e.get("event") == "head_ref_force_pushed"]
    if pushes:
        print(f"NOTE: {len(pushes)} force-push(es) -> earlier review anchors may be stale; re-anchor on the head")

    human = 0
    roots: dict[int, dict] = {}
    replies: dict[int, list] = defaultdict(list)
    for x in c.get_all(f"{api}/comments"):
        parent = x.get("in_reply_to_id")
        if parent:
            replies[parent].append(x)
        else:
            roots[x["id"]] = x
    for cid, x in roots.items():
        human += 1
        line = x.get("line") or x.get("original_line")
        section(f"review comment {cid} | {x.get('path')}:{line}")
        for y in [x] + replies.get(cid, []):
            print(f"--- [{y.get('user', {}).get('login', '?')}] ---\n{(y.get('body') or '').strip()}\n")
    for x in c.get_all(f"{h.api}/issues/{pr_id}/comments"):
        human += 1
        section(f"issue comment {x['id']} | (general)")
        print(f"--- [{x.get('user', {}).get('login', '?')}] ---\n{(x.get('body') or '').strip()}\n")
    for r in reviews:
        if r.get("body"):
            human += 1
            section(f"review {r['id']} | {r.get('state')} | (general)")
            print(f"--- [{r.get('user', {}).get('login', '?')}] ---\n{r['body'].strip()}\n")
    print(f"({human} human threads)")
    return base, src


def fetch_gitlab(c: Client, h: Host, pr_id: int) -> tuple[str, str]:
    api = h.pr_api(pr_id)
    mr = c.get(api)
    print(f"title   : {mr.get('title')}")
    print(f"status  : {mr.get('state')} | merge status: {mr.get('detailed_merge_status')} | draft: {mr.get('draft')}")
    print(f"branches: {mr.get('source_branch')} -> {mr.get('target_branch')}")
    print(f"author  : {mr.get('author', {}).get('name')}")
    approvals = c.get(f"{api}/approvals")
    print(f"approved: {[a['user']['name'] for a in approvals.get('approved_by', [])]} "
          f"| reviewers: {[r.get('name') for r in mr.get('reviewers', [])]}")
    print("--- description ---")
    print(mr.get("description") or "(none)")
    print("--- end description ---\n")

    versions = c.get_all(f"{api}/versions")  # newest first
    for i, v in enumerate(reversed(versions), 1):
        print(f"version {i} (id {v['id']}): src={v['head_commit_sha'][:10]} base={v['base_commit_sha'][:10]} "
              f"start={v['start_commit_sha'][:10]}")
    last = versions[0]
    base, src = last["base_commit_sha"], last["head_commit_sha"]
    if len({v["base_commit_sha"] for v in versions}) > 1:
        print("NOTE: base moved between versions -> rebased; diff only against the last base")
    print(f"diff_refs for posting: base={base[:10]} head={src[:10]} start={last['start_commit_sha'][:10]}")

    human = 0
    for d in c.get_all(f"{api}/discussions"):
        notes = [n for n in d.get("notes", []) if not n.get("system")]
        if not notes:
            continue
        human += 1
        pos = notes[0].get("position") or {}
        resolved = "resolved" if notes[0].get("resolved") else ("open" if notes[0].get("resolvable") else "note")
        section(f"discussion {d['id']} | {resolved} | {pos.get('new_path', '(general)')}:{pos.get('new_line')}")
        for n in notes:
            print(f"--- [{n.get('author', {}).get('name', '?')}] ---\n{(n.get('body') or '').strip()}\n")
    print(f"({human} human threads)")
    return base, src


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pr_id", type=int)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--diff", action="store_true", help="git fetch both commits and print diff --stat")
    args = parser.parse_args()

    host = detect(args.remote)
    print(f"host    : {host.label} | {host.slug} | {host.noun} {args.pr_id} | {host.pr_url(args.pr_id)}")
    client = Client(host)
    base, src = {"ado": fetch_ado, "github": fetch_github, "gitlab": fetch_gitlab}[host.kind](client, host, args.pr_id)

    subprocess.run(["git", "fetch", "-q", args.remote, base, src], check=True)
    build_validation(client, host, args.pr_id, src)
    try:
        related_prs(client, host, args.pr_id, base, src, args.remote)
    except SystemExit as err:  # an API error in the related-PR lookup must not abort the review
        print(f"\n=== related {host.noun}s === unavailable ({err})")

    if args.diff:
        subprocess.run(["git", "diff", "--stat", base, src], check=True)

    print(f"\nBASE {base} SRC {src}")


if __name__ == "__main__":
    main()
