import datetime
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- PATHS (absolute, platform-safe) ---
CORE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CORE_DIR.parent
ENV_PATH = CORE_DIR / ".env"
GOALS_PATH = CORE_DIR / "GOALS.md"
BACKLOG_PATH = PROJECT_DIR / "BACKLOG.md"
LOG_PATH = CORE_DIR / "result.log"
IST = ZoneInfo("Asia/Kolkata")

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# --- GIT (platform-aware) ---
GIT_EXE = "git"
if sys.platform == "win32":
    for candidate in [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
    ]:
        if os.path.exists(candidate):
            GIT_EXE = candidate
            break

PRIMARY_MODEL = "gemini-2.0-flash"
FALLBACK_MODEL = "gemini-1.5-flash"
REQUIRED_PROJECT_FILES = ("main.py", "README.md", "requirements.txt")


class StrikeError(RuntimeError):
    pass


def now_ist():
    return datetime.datetime.now(IST)


def current_date_str(now=None):
    current = now or now_ist()
    if current.tzinfo is None:
        current = current.replace(tzinfo=IST)
    else:
        current = current.astimezone(IST)
    return current.strftime("%Y-%m-%d")


def slugify(text):
    return re.sub(r"[\s\W_]+", "-", text.lower()).strip("-")


def require_api_key():
    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise StrikeError("GEMINI_API_KEY not found. Add it to GitHub Secrets or core_system/.env")
    return api_key


def get_client():
    return genai.Client(api_key=require_api_key())


def get_daily_goal(now=None):
    current = now or now_ist()
    if current.tzinfo is None:
        current = current.replace(tzinfo=IST)
    else:
        current = current.astimezone(IST)

    day_of_year = current.timetuple().tm_yday
    goal_index = day_of_year % 3
    goals = {
        0: {
            "title": "AI Mastery",
            "focus": (
                "Build deep technical infrastructure: MCP servers, LLM evaluation tools, "
                "RAG pipelines, agentic frameworks, or Claude Code automation scripts. "
                "Think like a Principal Engineer building the weapons of 2026."
            ),
        },
        1: {
            "title": "Strategic Sharpness",
            "focus": (
                "Build logic-based decision systems: game theory engines, second-order effect "
                "simulators, competitor intelligence scrapers, or psychological pattern trackers. "
                "Think like a Systems Architect who maps invisible leverage."
            ),
        },
        2: {
            "title": "Financial Independence",
            "focus": (
                "Build direct revenue tools: lead generation automation for Suryoday Bank loans, "
                "Teddy3 clothing brand inventory or content bots, TallyBridge improvements, "
                "or SaaS micro-tools that can be sold for $5-20/month. "
                "Think like a founder who replaces salary with systems."
            ),
        },
    }
    return goals[goal_index]


def call_model(client, model_name, prompt, schema):
    return client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )


def parse_response(response):
    data = getattr(response, "parsed", None)
    if data:
        return data

    raw = response.text.strip() if hasattr(response, "text") else ""
    if not raw:
        return None
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    return json.loads(raw)


def load_goals_content():
    if GOALS_PATH.exists():
        return GOALS_PATH.read_text(encoding="utf-8")
    if BACKLOG_PATH.exists():
        log.info("GOALS.md missing; using BACKLOG.md as project guidance.")
        return BACKLOG_PATH.read_text(encoding="utf-8")
    return (
        "Build one small, useful Python CLI project aligned with AI, strategy, finance, "
        "productivity, or knowledge systems."
    )


def build_prompt(goals_content, goal, date_str):
    return f"""
STRICT MANDATE FOR TODAY - {date_str}
Category: {goal['title']}
Specific Focus: {goal['focus']}

CONSTRAINT: Only build within today's category. No cross-pillar drift.

CONTEXT - Who you are building for:
- Sivanesh (Buddy), 22, final-year B.Com, Chennai
- Founder of Teddy3 brand (streetwear + automation)
- Running lead-gen for Suryoday Small Finance Bank (unsecured biz loans, Chennai)
- Building Resume Builder AaaS (B2B, React + Firebase + Razorpay)
- Building Karen (AI voice agent, LiveKit + Deepgram + Gemini)
- Stack: Python, n8n, Railway, Vercel, Google APIs, Gemini, Claude
- Machine: Windows, Intel i5, no GPU - CPU-only, lightweight tools only

GOALS FILE:
{goals_content}

TASK: Design a unique, high-leverage Python CLI tool that:
1. Solves a real problem in the category above
2. Is SaaS-ready (could be sold as a $5-20/month micro-service)
3. Is modular (core logic reusable in larger systems)
4. Uses only free/open APIs or local computation
5. Runs on CPU-only Windows machine

Return ONLY a JSON object with these exact keys:
- "name": slug-friendly project name (no spaces, lowercase, hyphens)
- "code": complete, runnable main.py source code
- "readme": professional README.md with #AIMastery / #Strategy / #Finance tag
- "requirements": list of pip package names only
"""


def project_path_for(date_str, project_name):
    project_slug = slugify(project_name or "daily-strike")
    if not project_slug:
        project_slug = "daily-strike"
    return PROJECT_DIR / f"{date_str}-{project_slug}"


def project_path_is_complete(path):
    return path.is_dir() and all((path / name).is_file() for name in REQUIRED_PROJECT_FILES)


def find_projects_for_date(project_dir, date_str):
    return sorted(
        path
        for path in project_dir.iterdir()
        if path.is_dir() and path.name.startswith(f"{date_str}-")
    )


def validate_project_payload(data):
    if not isinstance(data, dict):
        raise StrikeError("Model response was not a JSON object.")

    for key in ("name", "code", "readme", "requirements"):
        if key not in data:
            raise StrikeError(f"Model response missing required key: {key}")

    if not str(data["name"]).strip():
        raise StrikeError("Model returned an empty project name.")
    if not str(data["code"]).strip():
        raise StrikeError("Model returned empty main.py content.")
    if not str(data["readme"]).strip():
        raise StrikeError("Model returned empty README content.")
    if not isinstance(data["requirements"], list):
        raise StrikeError("Model returned invalid requirements payload.")


def persist_project(path, data):
    path.mkdir(parents=True, exist_ok=True)
    files = {
        "main.py": data["code"],
        "README.md": data["readme"],
        "requirements.txt": "\n".join(data["requirements"]).strip(),
    }
    for fname, content in files.items():
        (path / fname).write_text(f"{content}\n" if content and not content.endswith("\n") else content, encoding="utf-8")
        log.info("Saved: %s", fname)
    log.info("Project packaged: %s", path.name)


def ensure_today_project_exists(project_dir, date_str):
    todays_projects = find_projects_for_date(project_dir, date_str)
    if not todays_projects:
        raise StrikeError(f"No daily project folder found for {date_str}.")

    incomplete = [path.name for path in todays_projects if not project_path_is_complete(path)]
    if incomplete:
        raise StrikeError(f"Incomplete daily project folders for {date_str}: {', '.join(incomplete)}")

    return todays_projects


def maybe_push_locally(goal_title, project_name, folder_name):
    if sys.platform != "win32":
        log.info("Running on CI - git handled by workflow step.")
        return

    log.info("Pushing to GitHub...")
    try:
        subprocess.run([GIT_EXE, "add", "."], cwd=PROJECT_DIR, check=True, capture_output=True)
        status = subprocess.run(
            [GIT_EXE, "status", "--porcelain"],
            cwd=PROJECT_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        if status.stdout.strip():
            commit_msg = f"Strike [{goal_title}]: {project_name}"
            subprocess.run(
                [GIT_EXE, "commit", "-m", commit_msg],
                cwd=PROJECT_DIR,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [GIT_EXE, "push", "origin", "main"],
                cwd=PROJECT_DIR,
                check=True,
                capture_output=True,
            )
            log.info("STRIKE DEPLOYED: %s", folder_name)
        else:
            log.info("Nothing to commit.")
    except FileNotFoundError as exc:
        raise StrikeError(f"git executable not found at {GIT_EXE}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode(errors="replace") if exc.stderr else str(exc)
        raise StrikeError(f"Git failed: {stderr}") from exc


def execute_strike(now=None):
    date_str = current_date_str(now)
    goal = get_daily_goal(now)
    goals_content = load_goals_content()
    prompt = build_prompt(goals_content, goal, date_str)
    schema = {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING"},
            "code": {"type": "STRING"},
            "readme": {"type": "STRING"},
            "requirements": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["name", "code", "readme", "requirements"],
    }

    log.info("Theme: %s | Date: %s", goal["title"], date_str)

    client = get_client()
    response = None
    last_error = None
    for model in (PRIMARY_MODEL, FALLBACK_MODEL):
        try:
            log.info("Calling model: %s", model)
            response = call_model(client, model, prompt, schema)
            break
        except Exception as exc:
            last_error = exc
            log.warning("Model %s failed: %s", model, exc)

    if response is None:
        raise StrikeError(f"All model calls failed: {last_error}")

    try:
        data = parse_response(response)
    except Exception as exc:
        raw_snippet = getattr(response, "text", "")[:500]
        raise StrikeError(f"JSON parse failed: {exc}. Raw snippet: {raw_snippet}") from exc

    if not data:
        raise StrikeError("Empty data returned from model.")

    validate_project_payload(data)

    project_name = str(data["name"]).strip()
    path = project_path_for(date_str, project_name)

    if path.exists():
        if not project_path_is_complete(path):
            raise StrikeError(f"Folder already exists but is incomplete: {path.name}")
        log.info("Daily project already exists for today: %s", path.name)
    else:
        persist_project(path, data)

    todays_projects = ensure_today_project_exists(PROJECT_DIR, date_str)
    log.info("Verified %s daily project folder(s) for %s.", len(todays_projects), date_str)

    maybe_push_locally(goal["title"], project_name, path.name)
    return path


def main():
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
