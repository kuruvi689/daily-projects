"""Pure Daily Strike logic shared by the local runner and the Vercel endpoint.

Stdlib only, so it can run inside a Vercel Python function without dependencies.
"""
import datetime
import json
import re
from typing import Any, Protocol

# IST has no DST, so a fixed offset avoids depending on tzdata being installed.
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30), name="IST")
REQUIRED_PROJECT_FILES = ("main.py", "README.md", "requirements.txt")
REQUIRED_KEYS = ("name", "code", "readme", "requirements")
DEFAULT_GOALS = (
    "Build one small, useful Python CLI project aligned with AI, strategy, finance, "
    "productivity, or knowledge systems."
)

GOALS = {
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


class StrikeError(RuntimeError):
    pass


class JsonChatClient(Protocol):
    def chat_json(self, prompt: str) -> tuple[dict, str]: ...


def to_ist(now: datetime.datetime | None = None) -> datetime.datetime:
    current = now or datetime.datetime.now(IST)
    if current.tzinfo is None:
        return current.replace(tzinfo=IST)
    return current.astimezone(IST)


def current_date_str(now: datetime.datetime | None = None) -> str:
    return to_ist(now).strftime("%Y-%m-%d")


def get_daily_goal(now: datetime.datetime | None = None) -> dict:
    return GOALS[to_ist(now).timetuple().tm_yday % 3]


def slugify(text: str) -> str:
    return re.sub(r"[\s\W_]+", "-", text.lower()).strip("-")


def folder_name_for(date_str: str, project_name: str) -> str:
    slug = slugify(project_name or "")[:60].strip("-") or "daily-strike"
    return f"{date_str}-{slug}"


def build_prompt(goals_content: str, goal: dict, date_str: str) -> str:
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
- Stack: Python, n8n, Railway, Vercel, Google APIs, Groq, Claude
- Machine: Windows, Intel i5, no GPU - CPU-only, lightweight tools only

GOALS FILE:
{goals_content}

TASK: Design a unique, high-leverage Python CLI tool that:
1. Solves a real problem in the category above
2. Is SaaS-ready (could be sold as a $5-20/month micro-service)
3. Is modular (core logic reusable in larger systems)
4. Uses only free/open APIs or local computation, preferring the standard library
5. Runs on CPU-only Windows machine

SIZE LIMITS (hard): main.py under 250 lines, README under 80 lines.

Return ONLY a JSON object with these exact keys:
- "name": slug-friendly project name (no spaces, lowercase, hyphens)
- "code": complete, runnable main.py source code
- "readme": professional README.md with #AIMastery / #Strategy / #Finance tag
- "requirements": list of pip package names only (empty list if stdlib only)
"""


def parse_json_text(raw: str) -> Any:
    text = (raw or "").strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0]
    elif text.startswith("```"):
        text = text.split("```", 2)[1]
    return json.loads(text.strip())


def validate_project_payload(data: Any) -> None:
    if not isinstance(data, dict):
        raise StrikeError("Model response was not a JSON object.")
    for key in REQUIRED_KEYS:
        if key not in data:
            raise StrikeError(f"Model response missing required key: {key}")
    if not str(data["name"]).strip():
        raise StrikeError("Model returned an empty project name.")
    if not str(data["code"]).strip():
        raise StrikeError("Model returned empty main.py content.")
    if not str(data["readme"]).strip():
        raise StrikeError("Model returned empty README content.")
    reqs = data["requirements"]
    if not isinstance(reqs, list) or not all(isinstance(r, str) for r in reqs):
        raise StrikeError("Model returned invalid requirements payload.")


def _with_newline(content: str) -> str:
    return content if not content or content.endswith("\n") else f"{content}\n"


def render_project_files(data: dict) -> dict[str, str]:
    return {
        "main.py": _with_newline(str(data["code"])),
        "README.md": _with_newline(str(data["readme"])),
        "requirements.txt": _with_newline("\n".join(r.strip() for r in data["requirements"] if r.strip())),
    }


def generate_project(client: JsonChatClient, goals_content: str, now: datetime.datetime | None = None) -> dict:
    """Ask the model for today's project. Returns folder name, files, model and goal."""
    date_str = current_date_str(now)
    goal = get_daily_goal(now)
    data, model = client.chat_json(build_prompt(goals_content or DEFAULT_GOALS, goal, date_str))
    validate_project_payload(data)
    name = str(data["name"]).strip()
    return {
        "date": date_str,
        "goal": goal["title"],
        "name": name,
        "folder": folder_name_for(date_str, name),
        "files": render_project_files(data),
        "model": model,
    }
