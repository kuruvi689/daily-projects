import os, json, subprocess, re, datetime, sys, logging
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- PATHS (absolute, platform-safe) ---
CORE_DIR    = Path(__file__).resolve().parent
PROJECT_DIR = CORE_DIR.parent
ENV_PATH    = CORE_DIR / ".env"
GOALS_PATH  = CORE_DIR / "GOALS.md"
BACKLOG_PATH = PROJECT_DIR / "BACKLOG.md"
LOG_PATH    = CORE_DIR / "result.log"

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# --- ENV (GitHub Actions injects GEMINI_API_KEY directly; .env used locally) ---
load_dotenv(dotenv_path=ENV_PATH)
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    log.error("GEMINI_API_KEY not found. Add it to GitHub Secrets or core_system/.env")
    sys.exit(1)

# --- GIT (platform-aware) ---
GIT_EXE = "git"  # GitHub Actions runner has git in PATH natively
if sys.platform == "win32":
    for candidate in [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe"
    ]:
        if os.path.exists(candidate):
            GIT_EXE = candidate
            break

DATE_STR = datetime.datetime.now().strftime("%Y-%m-%d")
client   = genai.Client(api_key=API_KEY)

PRIMARY_MODEL  = "gemini-2.0-flash"
FALLBACK_MODEL = "gemini-1.5-flash"

def slugify(text):
    return re.sub(r'[\s\W_]+', '-', text.lower()).strip('-')

def get_daily_goal():
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    goal_index  = day_of_year % 3
    goals = {
        0: {
            "title": "AI Mastery",
            "focus": (
                "Build deep technical infrastructure: MCP servers, LLM evaluation tools, "
                "RAG pipelines, agentic frameworks, or Claude Code automation scripts. "
                "Think like a Principal Engineer building the weapons of 2026."
            )
        },
        1: {
            "title": "Strategic Sharpness",
            "focus": (
                "Build logic-based decision systems: game theory engines, second-order effect "
                "simulators, competitor intelligence scrapers, or psychological pattern trackers. "
                "Think like a Systems Architect who maps invisible leverage."
            )
        },
        2: {
            "title": "Financial Independence",
            "focus": (
                "Build direct revenue tools: lead generation automation for Suryoday Bank loans, "
                "Teddy3 clothing brand inventory or content bots, TallyBridge improvements, "
                "or SaaS micro-tools that can be sold for $5-20/month. "
                "Think like a founder who replaces salary with systems."
            )
        }
    }
    return goals[goal_index]

def call_model(model_name, prompt, schema):
    return client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=schema
        )
    )

def parse_response(response):
    data = getattr(response, 'parsed', None)
    if data:
        return data
    raw = response.text.strip() if hasattr(response, 'text') else ""
    if not raw:
        return None
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    return json.loads(raw)

def execute_strike():
    if GOALS_PATH.exists():
        goals_content = GOALS_PATH.read_text(encoding='utf-8')
    elif BACKLOG_PATH.exists():
        log.info("GOALS.md missing; using BACKLOG.md as project guidance.")
        goals_content = BACKLOG_PATH.read_text(encoding='utf-8')
    else:
        goals_content = "Build one small, useful Python CLI project aligned with AI, strategy, finance, productivity, or knowledge systems."
    goal = get_daily_goal()

    prompt = f"""
STRICT MANDATE FOR TODAY — {DATE_STR}
Category: {goal['title']}
Specific Focus: {goal['focus']}

CONSTRAINT: Only build within today's category. No cross-pillar drift.

CONTEXT — Who you are building for:
- Sivanesh (Buddy), 22, final-year B.Com, Chennai
- Founder of Teddy3 brand (streetwear + automation)
- Running lead-gen for Suryoday Small Finance Bank (unsecured biz loans, Chennai)
- Building Resume Builder AaaS (B2B, React + Firebase + Razorpay)
- Building Karen (AI voice agent, LiveKit + Deepgram + Gemini)
- Stack: Python, n8n, Railway, Vercel, Google APIs, Gemini, Claude
- Machine: Windows, Intel i5, no GPU — CPU-only, lightweight tools only

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

    schema = {
        'type': 'OBJECT',
        'properties': {
            'name':         {'type': 'STRING'},
            'code':         {'type': 'STRING'},
            'readme':       {'type': 'STRING'},
            'requirements': {'type': 'ARRAY', 'items': {'type': 'STRING'}}
        },
        'required': ['name', 'code', 'readme', 'requirements']
    }

    log.info("Theme: %s | Date: %s", goal['title'], DATE_STR)

    response = None
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            log.info("Calling model: %s", model)
            response = call_model(model, prompt, schema)
            break
        except Exception as e:
            log.warning("Model %s failed: %s", model, e)

    if not response:
        log.error("All models failed. Aborting.")
        return

    try:
        data = parse_response(response)
    except Exception as e:
        log.error("JSON parse failed: %s", e)
        raw_snippet = getattr(response, 'text', '')[:500]
        log.error("Raw snippet: %s", raw_snippet)
        return

    if not data:
        log.error("Empty data returned from model.")
        return

    project_name = data.get('name', 'daily-strike')
    project_slug = slugify(project_name)
    folder_name  = f"{DATE_STR}-{project_slug}"
    path         = PROJECT_DIR / folder_name

    if path.exists():
        log.warning("Folder already exists: %s. Skipping.", folder_name)
    else:
        path.mkdir(parents=True, exist_ok=True)
        files = {
            "main.py":          data.get('code', '# empty'),
            "README.md":        data.get('readme', ''),
            "requirements.txt": "\n".join(data.get('requirements', []))
        }
        for fname, content in files.items():
            (path / fname).write_text(content, encoding='utf-8')
            log.info("Saved: %s", fname)
        log.info("Project packaged: %s", folder_name)

    # Git push (skipped on GitHub Actions — the workflow step handles it)
    if sys.platform == "win32":
        log.info("Pushing to GitHub...")
        try:
            subprocess.run([GIT_EXE, 'add', '.'],
                           cwd=PROJECT_DIR, check=True, capture_output=True)
            status = subprocess.run([GIT_EXE, 'status', '--porcelain'],
                                    cwd=PROJECT_DIR, check=True,
                                    capture_output=True, text=True)
            if status.stdout.strip():
                commit_msg = f"Strike [{goal['title']}]: {project_name}"
                subprocess.run([GIT_EXE, 'commit', '-m', commit_msg],
                               cwd=PROJECT_DIR, check=True, capture_output=True)
                subprocess.run([GIT_EXE, 'push', 'origin', 'main'],
                               cwd=PROJECT_DIR, check=True, capture_output=True)
                log.info("STRIKE DEPLOYED: %s", folder_name)
            else:
                log.info("Nothing to commit.")
        except FileNotFoundError:
            log.error("git.exe not found at %s", GIT_EXE)
        except subprocess.CalledProcessError as e:
            log.error("Git failed: %s", e.stderr.decode(errors='replace') if e.stderr else str(e))
    else:
        log.info("Running on CI — git handled by workflow step.")

if __name__ == "__main__":
    execute_strike()
