"""Host detection, credentials and HTTP for the reviewing-prs scripts.

Supports Azure DevOps (dev.azure.com), GitHub (github.com) and GitLab (gitlab.com or self-hosted
with "gitlab" in the host name, or any host named in the GITLAB_HOST environment variable).
The host is derived from the git remote URL; the token comes from ``git credential fill`` (Git
Credential Manager), so nothing is hard-coded and no CLI (gh / glab / az) is needed.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

ADO_API = "7.1"
USER_AGENT = "reviewing-prs-skill"

_PATTERNS = [
    ("ado", re.compile(r"https://(?:[^@/]+@)?(dev\.azure\.com)/([^/]+)/([^/]+)/_git/([^/]+?)(?:\.git)?/?$")),
    ("ado", re.compile(r"git@(ssh\.dev\.azure\.com):v3/([^/]+)/([^/]+)/([^/]+?)(?:\.git)?$")),
    ("github", re.compile(r"https://(?:[^@/]+@)?(github\.com)/([^/]+)/()([^/]+?)(?:\.git)?/?$")),
    ("github", re.compile(r"git@(github\.com):([^/]+)/()([^/]+?)(?:\.git)?$")),
    # GitLab last: any other https/ssh remote whose host looks like GitLab. Namespace may be nested.
    ("gitlab", re.compile(r"https://(?:[^@/]+@)?([^/]+)/(.+?)/()([^/]+?)(?:\.git)?/?$")),
    ("gitlab", re.compile(r"git@([^:]+):(.+?)/()([^/]+?)(?:\.git)?$")),
]


@dataclass
class Host:
    kind: str      # "ado" | "github" | "gitlab"
    host: str      # dev.azure.com | github.com | <gitlab host>
    org: str       # ADO organisation | GitHub owner | GitLab namespace path (may contain '/')
    project: str   # ADO project; "" for the others
    repo: str
    remote_url: str

    @property
    def label(self) -> str:
        return {"ado": "Azure DevOps", "github": "GitHub", "gitlab": "GitLab"}[self.kind]

    @property
    def noun(self) -> str:
        return "MR" if self.kind == "gitlab" else "PR"

    @property
    def slug(self) -> str:
        return "/".join(p for p in (self.org, self.project, self.repo) if p)

    @property
    def api(self) -> str:
        if self.kind == "ado":
            return f"https://dev.azure.com/{self.org}/{self.project}/_apis/git/repositories/{self.repo}"
        if self.kind == "github":
            return f"https://api.github.com/repos/{self.org}/{self.repo}"
        project = urllib.parse.quote(f"{self.org}/{self.repo}", safe="")
        return f"https://{self.host}/api/v4/projects/{project}"

    def pr_api(self, pr_id: int) -> str:
        if self.kind == "ado":
            return f"{self.api}/pullRequests/{pr_id}"
        if self.kind == "github":
            return f"{self.api}/pulls/{pr_id}"
        return f"{self.api}/merge_requests/{pr_id}"

    def pr_url(self, pr_id: int) -> str:
        if self.kind == "ado":
            return f"https://dev.azure.com/{self.org}/{self.project}/_git/{self.repo}/pullrequest/{pr_id}"
        if self.kind == "github":
            return f"https://github.com/{self.org}/{self.repo}/pull/{pr_id}"
        return f"https://{self.host}/{self.org}/{self.repo}/-/merge_requests/{pr_id}"

    @property
    def credential_path(self) -> str:
        if self.kind == "ado":
            return f"{self.org}/{self.project}/_git/{self.repo}"
        return f"{self.org}/{self.repo}"

    def file_url(self, sha: str, path: str, line: int | None = None, line_end: int | None = None) -> str:
        """Web link to `path` at commit `sha`, positioned on `line` (the host's own 'copy link to line' form)."""
        path = path.lstrip("/")
        if self.kind == "ado":
            url = (f"https://dev.azure.com/{self.org}/{self.project}/_git/{self.repo}"
                   f"?path={urllib.parse.quote('/' + path, safe='')}&version=GC{sha}&_a=contents")
            if line:
                url += (f"&line={line}&lineEnd={line_end or line}&lineStartColumn=1"
                        f"&lineEndColumn=1000&lineStyle=plain")
            return url
        if self.kind == "github":
            url = f"https://github.com/{self.org}/{self.repo}/blob/{sha}/{path}"
            return url + (f"#L{line}" + (f"-L{line_end}" if line_end and line_end != line else "") if line else "")
        url = f"https://{self.host}/{self.org}/{self.repo}/-/blob/{sha}/{path}"
        return url + (f"#L{line}" + (f"-{line_end}" if line_end and line_end != line else "") if line else "")

    def pr_file_url(self, pr_id: int, path: str, line: int | None = None) -> str:
        """Web link into the PR's own Files view for `path` (GitHub/GitLab can anchor the line)."""
        path = path.lstrip("/")
        if self.kind == "ado":
            return f"{self.pr_url(pr_id)}?_a=files&path={urllib.parse.quote('/' + path, safe='')}"
        if self.kind == "github":
            anchor = "diff-" + hashlib.sha256(path.encode()).hexdigest()
            return f"{self.pr_url(pr_id)}/files#{anchor}" + (f"R{line}" if line else "")
        anchor = hashlib.sha1(path.encode()).hexdigest()
        return f"{self.pr_url(pr_id)}/diffs#{anchor}" + (f"_0_{line}" if line else "")


def detect(remote: str = "origin") -> Host:
    """Return the Host for the given git remote, or exit with a clear message."""
    result = subprocess.run(["git", "remote", "get-url", remote], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"cannot read remote '{remote}': {result.stderr.strip()} (run from inside the repository)")
    url = result.stdout.strip()
    for kind, pattern in _PATTERNS:
        m = pattern.match(url)
        if not m:
            continue
        host, org, project, repo = m.groups()
        if kind == "gitlab":
            gitlab_host = os.environ.get("GITLAB_HOST", "")
            if "gitlab" not in host.lower() and host.lower() != gitlab_host.lower():
                continue
        if kind == "ado":
            host = "dev.azure.com"
        return Host(kind, host, org, project or "", repo, url)
    sys.exit(f"remote '{remote}' is not an Azure DevOps, GitHub or GitLab URL: {url}\n"
             "(self-hosted GitLab without 'gitlab' in the host name: set GITLAB_HOST=<host>)")


def token(host: Host) -> str:
    """Ask the git credential helper; the path lets GCM pick the right account for the org."""
    request = f"protocol=https\nhost={host.host}\npath={host.credential_path}\n\n"
    out = subprocess.run(["git", "credential", "fill"], input=request, capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("password="):
            return line[len("password="):]
    sys.exit(f"git credential fill returned no token for {host.host}; sign in once with `git fetch`, then retry")


def headers(host: Host) -> dict[str, str]:
    tok = token(host)
    if host.kind == "ado":
        return {"Authorization": "Basic " + base64.b64encode(f":{tok}".encode()).decode(),
                "User-Agent": USER_AGENT}
    if host.kind == "github":
        return {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28", "User-Agent": USER_AGENT}
    return {"Authorization": f"Bearer {tok}", "User-Agent": USER_AGENT}


class Client:
    """Minimal JSON client. ADO URLs get api-version appended automatically."""

    def __init__(self, host: Host):
        self.host = host
        self._headers = headers(host)

    def _url(self, url: str) -> str:
        if self.host.kind == "ado" and "api-version=" not in url:
            url += ("&" if "?" in url else "?") + f"api-version={ADO_API}"
        return url

    def call(self, method: str, url: str, body: dict | list | None = None):
        data = None
        hdrs = dict(self._headers)
        if body is not None:
            data = json.dumps(body).encode()
            hdrs["Content-Type"] = "application/json"
        req = urllib.request.Request(self._url(url), data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", "replace")[:600]
            hint = " (302/401 usually means an expired or wrong-scope token)" if err.code in (302, 401, 403) else ""
            sys.exit(f"HTTP {err.code} {method} {url}{hint}\n{detail}")

    def get(self, url: str):
        return self.call("GET", url)

    def post(self, url: str, body: dict | list):
        return self.call("POST", url, body)

    def get_all(self, url: str) -> list:
        """Follow GitHub/GitLab pagination (page/per_page); ADO returns everything in one call."""
        if self.host.kind == "ado":
            data = self.get(url)
            return data.get("value", data) if isinstance(data, dict) else data
        items: list = []
        page = 1
        while True:
            sep = "&" if "?" in url else "?"
            chunk = self.get(f"{url}{sep}per_page=100&page={page}")
            if not chunk:
                break
            items.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1
        return items


def utf8_stdout() -> None:
    """Descriptions and comments carry em dashes and emoji; a Windows console defaults to cp1252."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
