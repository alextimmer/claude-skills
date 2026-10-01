"""Render a review from a compact findings file: ONE source -> review.md (the template, every
anchor as three clickable links) AND review.json (what post_review.py posts).

Usage (from inside the repository checkout):

    python scripts/render_review.py review.yaml                 # writes review.md + review.json next to it
    python scripts/render_review.py review.yaml --check         # also verify every anchor exists on SRC and is in the diff
    python scripts/render_review.py review.yaml --out DIR

The reviewer writes WHAT (findings, texts, verdict); this script writes HOW (links, tables,
section order, review.json). Schema: see review.example.yaml next to this file. Severity words:
MAJOR | MEDIUM | MINOR. Anchors: "path:line" or "path:line-end", full repo path.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hosts import Host, detect, utf8_stdout  # noqa: E402

SEV = {"MAJOR": "🔴 MAJOR", "MEDIUM": "🟠 MEDIUM", "MINOR": "🟡 MINOR"}
VOTE = {  # (any MAJOR, any MEDIUM) -> per host
    "ado": {"major": "Wait for author", "medium": "Approve with suggestions", "none": "Approve"},
    "github": {"major": "Request changes", "medium": "Comment (approve once resolved)", "none": "Approve"},
    "gitlab": {"major": "Request changes", "medium": "Comment, no approval yet", "none": "Approve"},
}
ANCHOR = re.compile(r"^(?P<path>.+?):(?P<line>\d+)(?:-(?P<end>\d+))?$")
VERDICT_VOTE = {  # a verdict word maps straight to a vote; otherwise derive from severities
    "wait for author": "major", "request changes": "major",
    "approve with suggestions": "medium", "approve": "none",
}


def derive_vote(r: dict, host: Host) -> str:
    """Explicit `vote` wins; then the verdict word (a re-review may carry no new MAJOR while a
    prior one is still open); then the new findings' severities."""
    if r.get("vote"):
        return r["vote"]
    key = VERDICT_VOTE.get(str(r.get("verdict", "")).strip().lower().rstrip("."))
    if key is None:
        sevs = {f["severity"] for f in r.get("findings", [])}
        key = "major" if "MAJOR" in sevs else "medium" if "MEDIUM" in sevs else "none"
    return VOTE[host.kind][key]


def parse_anchor(spec: str) -> tuple[str, int, int | None]:
    m = ANCHOR.match(spec.strip())
    if not m:
        sys.exit(f"bad anchor {spec!r}: expected path:line or path:line-end")
    return m.group("path").replace("\\", "/").lstrip("/"), int(m.group("line")), int(m.group("end")) if m.group("end") else None


def links(host: Host, sha: str, pr: int, spec: str) -> str:
    path, line, end = parse_anchor(spec)
    label = f"{path}:{line}" + (f"-{end}" if end else "")
    local = f"{path}#L{line}" + (f"-L{end}" if end else "")
    return (f"**[`{label}`]({host.file_url(sha, path, line, end)})** · "
            f"[in PR]({host.pr_file_url(pr, path, line)}) · [local]({local})")


def short(spec: str) -> str:
    return f"`{spec}`"


def q(text: str) -> str:
    """Blockquote a markdown block, preserving fenced code."""
    return "\n".join("> " + l if l.strip() else ">" for l in text.rstrip().splitlines())


def check_anchors(r: dict, specs: list[str]) -> list[str]:
    base, src = r["base"], r["head"]
    changed = set(subprocess.run(["git", "diff", "--name-only", base, src], capture_output=True, text=True).stdout.split())
    problems = []
    for spec in specs:
        path, line, end = parse_anchor(spec)
        show = subprocess.run(["git", "show", f"{src}:{path}"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if show.returncode != 0:
            problems.append(f"{spec}: file not at SRC")
            continue
        n = show.stdout.count("\n") + 1
        if (end or line) > n:
            problems.append(f"{spec}: line beyond EOF ({n} lines)")
        if path not in changed:
            problems.append(f"{spec}: file not in the BASE..SRC diff (anchor on a changed file or '(general)')")
        text = show.stdout.splitlines()[line - 1].strip() if line <= n else ""
        if not text:
            problems.append(f"{spec}: blank line")
    return problems


def render_md(r: dict, host: Host) -> str:
    pr, sha = r["pr"], r["head"]
    L = lambda spec: links(host, sha, pr, spec)  # noqa: E731
    findings = r.get("findings", [])
    vote = derive_vote(r, host)
    out: list[str] = []
    a = out.append

    a(f"# Review — {host.label} {host.repo} {host.noun} {pr}" + (" (re-review)" if r.get("prior") else ""))
    a(f"**\"{r['title']}\"** · `{r['source']}` → `{r['target']}` · {r.get('iteration_note', '')} · "
      f"base `{r['base'][:7]}` ({r.get('base_note', 'stable')}), src `{sha[:7]}` · {r.get('files_note', '')} · {r.get('threads_note', '')}")
    a("")
    a("## The goal (as I read it)")
    a("")
    a(f"**This PR.** {r['goal']['this_pr'].strip()}")
    a("")
    a(f"**Where it sits.** {r['goal']['where_it_sits'].strip()}")
    a("")
    if r.get("related"):
        a("| Merge order | PR | Branch → target | Relation to this PR | Overlap | State |")
        a("|---|---|---|---|---|---|")
        for x in sorted(r["related"], key=lambda x: x.get("order", 99)):
            is_this = x.get("pr") == pr
            link = f"[{host.noun} {x['pr']}]({host.pr_url(x['pr'])})"
            if is_this:
                link = f"**{link} (this)**"
            title = f" {x['title']}" if x.get("title") else ""
            a(f"| {x.get('order', '')} | {link}{title} | `{x.get('branch', '')}` | "
              f"{'—' if is_this else x.get('relation', '')} | {x.get('overlap', '')} | {x.get('state', '')} |")
        a("")
    a(f"## Verdict: **{r['verdict']}.** {r['verdict_reason'].strip()} {host.label} vote: *{vote}*.")
    a("")
    a("## What I verified rather than took on faith ✅")
    for v in r.get("verified", []):
        line = f"- {v['text'].strip()}"
        if v.get("anchor"):
            line += f" → {L(v['anchor'])}"
        if v.get("source"):
            line += f" [{v['source']}]"
        a(line)
    a("")
    a("---")

    if r.get("prior"):
        a("")
        a("## Prior findings")
        a("")
        a("| Prior finding | Anchor | Status |")
        a("|---|---|---|")
        for p in r["prior"]:
            anchor = L(p["anchor"]) if p.get("anchor") and ":" in p["anchor"] else p.get("anchor", "(general)")
            a(f"| {p['severity']} {p['claim']} | {anchor} | {p['status']} |")
        a("")
        a("## New findings" if findings else "## New findings\n\nnone")

    order = {"MAJOR": 0, "MEDIUM": 1, "MINOR": 2}
    for f in sorted(findings, key=lambda f: order[f["severity"]]):
        a("")
        lock = " 🔒" if f.get("security") else ""
        reply = f" (reply into thread {f['reply_to']})" if f.get("reply_to") else ""
        a(f"### {SEV[f['severity']]}{lock} — {f['title'].strip()}{reply}")
        a(L(f["anchor"]) + ("".join(f" · also {short(x)}" for x in f.get("extra_anchors", []))))
        a("")
        a(f["body"].strip())
        if f.get("claims"):
            a("")
            a("| Claim in the code / description | Verdict | Source |")
            a("|---|---|---|")
            for c in f["claims"]:
                a(f"| \"{c['claim']}\" | {c['verdict']} | [{c['source']}] |")
        a("")
        path, line, end = parse_anchor(f["anchor"])
        head = "" if f.get("reply_to") else f"**[`{path}:{line}`]({host.file_url(sha, path, line, end)})** — "
        a(q(head + f["comment"].strip()))
        if f.get("sources"):
            a("")
            a(f"**Sources** (fetched {r.get('fetched', '')})")
            for i, sid in enumerate(f["sources"], 1):
                s = r["sources"][sid]
                a(f"{i}. [{sid}] {s['title']}" + (f", \"{s['quote']}\"" if s.get("quote") else "") + f" {s['url']}")
        if f.get("found_by"):
            a("")
            a(f"Found by: {f['found_by']}")

    a("")
    a("---")
    a("")
    a("## Summary")
    a("")
    a("| File:line | Severity | Finding | Follow-up |")
    a("|---|---|---|---|")
    for f in sorted(findings, key=lambda f: order[f["severity"]]):
        a(f"| {short(f['anchor'])} | {SEV[f['severity']]}{' 🔒' if f.get('security') else ''} | {f['title'].strip()} | {f.get('followup', '')} |")
    for row in r.get("summary_extra", []):
        a(f"| {row['anchor']} | {row['severity']} | {row['text']} | {row.get('followup', '')} |")
    a("")
    a(f"**Verdict:** {r['verdict']}. {r.get('verdict_expanded', '').strip()} Vote to cast: *{vote}*.")
    a("")
    a("## Housekeeping")
    a(r.get("housekeeping", "none").strip())
    a("")
    a(f"**Generators consulted:** {r.get('generators_consulted', 'none (no routing file)').strip()}")
    a("")
    a(f"**Retracted from generators:** {r.get('retracted', 'none').strip()}")
    a("")
    srcs = " · ".join(f"{k} {v['title']} {v['url']}" for k, v in r.get("sources", {}).items()) or "none"
    a(f"**Sources:** {srcs}" + (f" (fetched {r['fetched']})" if r.get("fetched") else ""))
    a("")
    a(f"**Could not verify:** {r.get('could_not_verify', 'none').strip()}")
    tickets = [f for f in findings if "ticket?" in str(f.get("followup", ""))]
    if tickets:
        a("")
        a(f"**Follow-up tickets?** {len(tickets)} finding(s) marked `ticket?` in the Summary. Say \"create tickets\" "
          "to see drafts; nothing is created before the drafts are shown and approved.")
    return "\n".join(out) + "\n"


def render_json(r: dict, host: Host, vote: str) -> dict:
    comments = []
    for f in r.get("findings", []):
        c: dict = {"severity": f["severity"], "body": f["comment"].strip()}
        if f.get("reply_to"):
            c.update({"path": None, "line": None, "reply_to": f["reply_to"]})
        else:
            path, line, end = parse_anchor(f["anchor"])
            c.update({"path": path, "line": end or line, "start_line": line if end else None, "reply_to": None})
        comments.append(c)
    order = {"MAJOR": 0, "MEDIUM": 1, "MINOR": 2}
    rows = ["| File:line | Severity | Finding |", "|---|---|---|"] + [
        f"| `{f['anchor']}` | {SEV[f['severity']]} | {f['title'].strip()} |"
        for f in sorted(r.get("findings", []), key=lambda f: order[f["severity"]])]
    summary = (f"**Verdict: {r['verdict']}.** {r['verdict_reason'].strip()}\n\n" + "\n".join(rows)
               + f"\n\n**Could not verify:** {r.get('could_not_verify', 'none').strip()}")
    return {"pr": r["pr"], "head": r["head"], "base": r["base"], "recommended_vote": vote,
            "summary": summary, "comments": comments}


def main() -> int:
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("review", help="review.yaml")
    ap.add_argument("--out", type=Path, help="output directory (default: next to the yaml)")
    ap.add_argument("--check", action="store_true", help="verify anchors against SRC and the diff")
    ap.add_argument("--remote", default="origin")
    args = ap.parse_args()
    src_path = Path(args.review)
    r = yaml.safe_load(src_path.read_text(encoding="utf-8"))
    host = detect(args.remote)
    for key in ("pr", "head", "base", "title", "source", "target", "goal", "verdict", "verdict_reason"):
        if key not in r:
            sys.exit(f"review.yaml: missing '{key}'")
    specs = [f["anchor"] for f in r.get("findings", [])] + [v["anchor"] for v in r.get("verified", []) if v.get("anchor")]
    if args.check:
        problems = check_anchors(r, specs)
        for p in problems:
            print("ANCHOR:", p, file=sys.stderr)
        if problems:
            print(f"{len(problems)} anchor problem(s); fix them before posting", file=sys.stderr)
    md = render_md(r, host)
    vote = derive_vote(r, host)
    out_dir = args.out or src_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "review.md").write_text(md, encoding="utf-8", newline="\n")
    (out_dir / "review.json").write_text(json.dumps(render_json(r, host, vote), indent=2, ensure_ascii=False) + "\n",
                                         encoding="utf-8", newline="\n")
    print(f"wrote {out_dir / 'review.md'} ({len(md.splitlines())} lines) and {out_dir / 'review.json'} "
          f"({len(r.get('findings', []))} comment(s)); vote: {vote}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
