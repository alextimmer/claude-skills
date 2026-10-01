"""Print clickable anchors for review findings: host web link at the PR head, PR Files-view link,
and the local file link, for any number of path:line[-end] arguments.

Usage (from inside the repository checkout):

    python scripts/anchor.py --pr 44517 --sha <SRC> src/x.sql:42 tools/y.py:10-12 ...

Output per anchor (markdown, ready to drop into the review):
    **[`src/x.sql:42`](<web url at SRC>)** · [in PR](<PR files url>) · [local](src/x.sql#L42)
The local link is repo-relative and opens the file in the IDE from the chat; the web link opens
the exact line on Azure DevOps / GitHub / GitLab; the PR link opens the PR's Files view (GitHub
and GitLab anchor the line too; Azure DevOps opens the file).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hosts import detect, utf8_stdout  # noqa: E402

ANCHOR = re.compile(r"^(?P<path>.+?):(?P<line>\d+)(?:-(?P<end>\d+))?$")


def render(host, sha: str, pr_id: int | None, spec: str) -> str:
    m = ANCHOR.match(spec)
    if not m:
        return f"(not an anchor: {spec!r}; expected path:line or path:line-end)"
    path, line = m.group("path").replace("\\", "/").lstrip("/"), int(m.group("line"))
    end = int(m.group("end")) if m.group("end") else None
    label = f"{path}:{line}" + (f"-{end}" if end else "")
    parts = [f"**[`{label}`]({host.file_url(sha, path, line, end)})**"]
    if pr_id:
        parts.append(f"[in PR]({host.pr_file_url(pr_id, path, line)})")
    parts.append(f"[local]({path}#L{line}" + (f"-L{end}" if end else "") + ")")
    return " · ".join(parts)


def main() -> None:
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("anchors", nargs="+", help="path:line or path:line-end")
    ap.add_argument("--sha", required=True, help="commit the anchors refer to (SRC from fetch_pr.py)")
    ap.add_argument("--pr", type=int, help="PR/MR id, adds the 'in PR' link")
    ap.add_argument("--remote", default="origin")
    args = ap.parse_args()
    host = detect(args.remote)
    for spec in args.anchors:
        print(render(host, args.sha, args.pr, spec))


if __name__ == "__main__":
    main()
