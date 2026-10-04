"""Local / CI runner: generate today's project with Groq into this checkout.

The production path is the Vercel endpoint (api/strike.py); this script is for
running a strike from your own machine (it commits and pushes on Windows).
"""
import logging
import os
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core_system.groq_client import GroqClient  # noqa: E402
from core_system.strike_core import (  # noqa: E402
    DEFAULT_GOALS,
    REQUIRED_PROJECT_FILES,
    StrikeError,
    current_date_str,
    generate_project,
)

# --- PATHS (absolute, platform-safe) ---
CORE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CORE_DIR.parent
ENV_PATHS = (PROJECT_DIR / ".env", CORE_DIR / ".env")
GOALS_PATH = CORE_DIR / "GOALS.md"
BACKLOG_PATH = PROJECT_DIR / "BACKLOG.md"
LOG_PATH = CORE_DIR / "result.log"

log = logging.getLogger("orchestrator")

__all__ = ["REQUIRED_PROJECT_FILES", "StrikeError", "current_date_str"]

# --- GIT (platform-aware) ---
GIT_EXE = "git"
if sys.platform == "win32":
    for candidate in (r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files (x86)\Git\cmd\git.exe"):
        if os.path.exists(candidate):
            GIT_EXE = candidate
            break


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )


def load_env_files() -> None:
    """Minimal .env loader so the runner has no third-party dependencies."""
    for path in ENV_PATHS:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_goals_content() -> str:
    if GOALS_PATH.exists():
        return GOALS_PATH.read_text(encoding="utf-8")
    if BACKLOG_PATH.exists():
        log.info("GOALS.md missing; using BACKLOG.md as project guidance.")
        return BACKLOG_PATH.read_text(encoding="utf-8")
    return DEFAULT_GOALS


def project_path_is_complete(path: Path) -> bool:
    return path.is_dir() and all((path / name).is_file() for name in REQUIRED_PROJECT_FILES)


def find_projects_for_date(project_dir: Path, date_str: str) -> list[Path]:
    return sorted(p for p in project_dir.iterdir() if p.is_dir() and p.name.startswith(f"{date_str}-"))


def ensure_today_project_exists(project_dir: Path, date_str: str) -> list[Path]:
    todays_projects = find_projects_for_date(project_dir, date_str)
    if not todays_projects:
        raise StrikeError(f"No daily project folder found for {date_str}.")
    incomplete = [p.name for p in todays_projects if not project_path_is_complete(p)]
    if incomplete:
        raise StrikeError(f"Incomplete daily project folders for {date_str}: {', '.join(incomplete)}")
    return todays_projects


def persist_project(path: Path, files: dict[str, str]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (path / name).write_text(content, encoding="utf-8")
        log.info("Saved: %s", name)
    log.info("Project packaged: %s", path.name)


def maybe_push_locally(message: str, folder_name: str) -> None:
    if sys.platform != "win32":
        log.info("Running on CI - git handled by workflow step.")
        return
    log.info("Pushing to GitHub...")
    try:
        subprocess.run([GIT_EXE, "add", folder_name], cwd=PROJECT_DIR, check=True, capture_output=True)
        subprocess.run([GIT_EXE, "commit", "-m", message], cwd=PROJECT_DIR, check=True, capture_output=True)
        subprocess.run([GIT_EXE, "push", "origin", "main"], cwd=PROJECT_DIR, check=True, capture_output=True)
        log.info("STRIKE DEPLOYED: %s", folder_name)
    except FileNotFoundError as exc:
        raise StrikeError(f"git executable not found at {GIT_EXE}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode(errors="replace") if exc.stderr else str(exc)
        raise StrikeError(f"Git failed: {stderr}") from exc


def execute_strike() -> Path:
    date_str = current_date_str()
    existing = find_projects_for_date(PROJECT_DIR, date_str)
    if existing:
        log.info("Daily project already exists for today: %s", existing[0].name)
        ensure_today_project_exists(PROJECT_DIR, date_str)
        return existing[0]

    load_env_files()
    client = GroqClient(os.environ.get("GROQ_API_KEY", ""))
    project = generate_project(client, load_goals_content())
    log.info("Theme: %s | Date: %s | Model: %s", project["goal"], project["date"], project["model"])

    path = PROJECT_DIR / project["folder"]
    persist_project(path, project["files"])
    ensure_today_project_exists(PROJECT_DIR, date_str)
    maybe_push_locally(f"Strike [{project['goal']}]: {project['name']}", project["folder"])
    return path


def main() -> None:
    setup_logging()
    try:
        execute_strike()
    except StrikeError as exc:
        log.error("%s", exc)
        sys.exit(1)
    except Exception:
        log.exception("Unexpected Daily Strike failure")
        sys.exit(1)


if __name__ == "__main__":
    main()
