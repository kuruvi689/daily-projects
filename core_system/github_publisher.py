"""Commit files to GitHub through the REST API (stdlib only).

Used by the Vercel endpoint, which has no persistent git checkout.
"""
import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

from core_system.strike_core import StrikeError

API = "https://api.github.com"
USER_AGENT = "daily-strike/2.0"

Transport = Callable[[str, str, dict, dict | None], tuple[int, str]]


def urllib_transport(method: str, url: str, headers: dict, body: dict | None) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


class GitHubPublisher:
    def __init__(self, token: str, repo: str, branch: str = "main", transport: Transport = urllib_transport):
        if not token:
            raise StrikeError("GITHUB_TOKEN is not set.")
        if not repo or "/" not in repo:
            raise StrikeError("GITHUB_REPO must look like 'owner/name'.")
        self._token = token
        self.repo = repo
        self.branch = branch
        self._transport = transport

    def _request(self, method: str, path: str, body: dict | None = None, ok: tuple[int, ...] = (200, 201)) -> dict | list:
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        status, text = self._transport(method, f"{API}/repos/{self.repo}{path}", headers, body)
        if status not in ok:
            raise StrikeError(f"GitHub {method} {path} failed: HTTP {status} {text[:200]}")
        return json.loads(text) if text else {}

    def read_text(self, path: str) -> str | None:
        quoted = urllib.parse.quote(path)
        try:
            data = self._request("GET", f"/contents/{quoted}?ref={self.branch}")
        except StrikeError:
            return None
        if not isinstance(data, dict) or "content" not in data:
            return None
        return base64.b64decode(data["content"]).decode("utf-8", "replace")

    def find_folder_with_prefix(self, prefix: str) -> str | None:
        entries = self._request("GET", f"/contents/?ref={self.branch}")
        for entry in entries if isinstance(entries, list) else []:
            if entry.get("type") == "dir" and entry.get("name", "").startswith(prefix):
                return entry["name"]
        return None

    def commit_files(self, files: dict[str, str], message: str) -> str:
        """Create one commit on the branch containing all files. Returns the commit SHA."""
        ref = self._request("GET", f"/git/ref/heads/{self.branch}")
        parent_sha = ref["object"]["sha"]
        parent = self._request("GET", f"/git/commits/{parent_sha}")
        tree = self._request(
            "POST",
            "/git/trees",
            {
                "base_tree": parent["tree"]["sha"],
                "tree": [{"path": p, "mode": "100644", "type": "blob", "content": c} for p, c in files.items()],
            },
        )
        commit = self._request(
            "POST",
            "/git/commits",
            {"message": message, "tree": tree["sha"], "parents": [parent_sha]},
        )
        # force=False: fails instead of overwriting if someone pushed in between.
        self._request("PATCH", f"/git/refs/heads/{self.branch}", {"sha": commit["sha"], "force": False})
        return commit["sha"]
