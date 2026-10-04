"""Vercel function: generate today's project with Groq and commit it to GitHub.

GET or POST /api/strike with header `Authorization: Bearer <CRON_SECRET>`.
Idempotent: if today's folder already exists in the repo, it returns "skipped".

Env vars: GROQ_API_KEY, GITHUB_TOKEN, CRON_SECRET, GITHUB_REPO (owner/name), GITHUB_BRANCH.
"""
import hmac
import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core_system.github_publisher import GitHubPublisher  # noqa: E402
from core_system.groq_client import GroqClient  # noqa: E402
from core_system.strike_core import StrikeError, current_date_str, generate_project, project_folders  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("strike")

DEFAULT_REPO = "kuruvi689/daily-projects"
# Leave headroom under the function's 300s maxDuration for the GitHub commit.
GROQ_DEADLINE_SECONDS = 220.0


def is_authorized(header: str | None, secret: str | None) -> bool:
    if not secret:
        return False
    return hmac.compare_digest((header or "").encode(), f"Bearer {secret}".encode())


def run_strike(
    env: dict = os.environ,
    groq: GroqClient | None = None,
    publisher: GitHubPublisher | None = None,
    dry_run: bool = False,
) -> tuple[int, dict]:
    """Build today's project. dry_run generates but never commits (for testing the live function)."""
    publisher = publisher or GitHubPublisher(
        env.get("GITHUB_TOKEN", ""), env.get("GITHUB_REPO", DEFAULT_REPO), env.get("GITHUB_BRANCH", "main")
    )
    date_str = current_date_str()
    existing = project_folders(publisher.list_folders())
    today = [name for name in existing if name.startswith(f"{date_str}-")]
    if today and not dry_run:
        return 200, {"status": "skipped", "reason": "already built today", "folder": today[0]}

    groq = groq or GroqClient(env.get("GROQ_API_KEY", ""), deadline_seconds=GROQ_DEADLINE_SECONDS)
    goals = publisher.read_text("core_system/GOALS.md") or publisher.read_text("BACKLOG.md") or ""
    project = generate_project(groq, goals, existing=existing)
    if dry_run:
        lines = {name: len(content.splitlines()) for name, content in project["files"].items()}
        return 200, {"status": "dry_run", "folder": project["folder"], "model": project["model"], "lines": lines}

    files = {f"{project['folder']}/{name}": content for name, content in project["files"].items()}
    message = f"Auto-Strike: {project['date']} [{project['goal']}] {project['name']}\n\nModel: {project['model']}"
    sha = publisher.commit_files(files, message)
    log.info("Committed %s as %s", project["folder"], sha)
    return 201, {"status": "created", "folder": project["folder"], "model": project["model"], "commit": sha}


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle(self) -> None:
        if not is_authorized(self.headers.get("Authorization"), os.environ.get("CRON_SECRET")):
            self._send(401, {"status": "error", "error": "unauthorized"})
            return
        query = parse_qs(urlparse(self.path).query)
        try:
            status, body = run_strike(dry_run=query.get("dry_run", ["0"])[0] == "1")
        except StrikeError as exc:
            log.error("Strike failed: %s", exc)
            status, body = 502, {"status": "error", "error": str(exc)}
        except Exception:
            log.exception("Unexpected strike failure")
            status, body = 500, {"status": "error", "error": "internal error"}
        self._send(status, body)

    def do_GET(self) -> None:  # noqa: N802 (Vercel/BaseHTTPRequestHandler naming)
        self._handle()

    def do_POST(self) -> None:  # noqa: N802
        self._handle()
