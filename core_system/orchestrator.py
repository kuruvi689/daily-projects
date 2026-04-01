import os, json, subprocess, re, datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- CONFIG ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
PROJECT_DIR = r"C:\Users\sindh\OneDrive\Desktop\daily-projects"
GOALS_PATH = os.path.join(os.path.dirname(__file__), "GOALS.md")
DATE_STR = datetime.datetime.now().strftime("%Y-%m-%d")

client = genai.Client(api_key=API_KEY)

def slugify(text):
    """Convert text to a filename-safe format."""
    return re.sub(r'[\s\W_]+', '-', text.lower()).strip('-')

# --- GOAL ARCHITECTURE ---
# 0: AI Mastery (MCP, Agentic Frameworks, Core Coding)
# 1: Strategic Sharpness (Psychology Systems, Decision Engines)
# 2: Financial Independence (TallyBridge, Teddy³, Revenue Bots)
def get_daily_goal():
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    goal_index = day_of_year % 3
    
    goals = {
        0: {"title": "AI Mastery", "focus": "Build deep technical infrastructure, MCP servers, or LLM evaluation tools."},
        1: {"title": "Strategic Sharpness", "focus": "Build logic-based systems for psychology, game theory, or second-order effect modeling."},
        2: {"title": "Financial Independence", "focus": "Automate TallyBridge, improve Teddy³ assets, or build lead-gen scrapers."}
    }
    return goals[goal_index]

def execute_strike():
    if not os.path.exists(GOALS_PATH): return print("[!] GOALS.md missing.")
    with open(GOALS_PATH, 'r', encoding='utf-8') as f: goals_file_content = f.read()

    goal = get_daily_goal()
    
    prompt = f"""
    STRICT MANDATE FOR TODAY:
    Category: {goal['title']}
    Specific Focus: {goal['focus']}
    
    CONSTRAINT: You are strictly forbidden from suggesting a project in the 'Finance' or 'Tally' category 
    unless the Category is 'Financial Independence'. 
    
    If it is 'AI Mastery' day, think like a Principal Engineer. 
    If it is 'Strategic Sharpness' day, think like a Systems Architect.

    TASK: Create a unique, high-leverage Python project for {DATE_STR}.
    The project must be modular, SaaS-ready, and align with the pillars in GOALS.md.
    
    GOALS FILE CONTEXT:
    {goals_file_content}
    
    Return a JSON object with these keys:
    - 'name': Slug-friendly project name.
    - 'code': Complete source code for 'main.py'.
    - 'readme': Markdown content for 'README.md' with tagging (#AIMastery, #Strategy, or #Finance).
    - 'requirements': List of pip dependencies.
    """
    
    try:
        print(f"[*] Theme for Today: {goal['title']}")
        # Use full model name with prefix if needed
        model_name = 'gemini-2.5-flash'
        print(f"[*] Generating Strike for {DATE_STR} using {model_name}...")
        
        schema = {
            'type': 'OBJECT',
            'properties': {
                'name': {'type': 'STRING'},
                'code': {'type': 'STRING'},
                'readme': {'type': 'STRING'},
                'requirements': {'type': 'ARRAY', 'items': {'type': 'STRING'}}
            },
            'required': ['name', 'code', 'readme', 'requirements']
        }

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=schema
                )
            )
        except Exception as api_err:
            print(f"[!] API Error during generation: {api_err}")
            # Fallback
            import time
            print(f"[*] Waiting 5s for quota reset and retrying with fallback model...")
            time.sleep(5)
            model_name = 'gemini-3.1-flash-live'
            print(f"[*] Retrying with {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=schema
                )
            )
        
        # In google-genai 1.x, response.parsed contains the data when response_schema is used
        data = getattr(response, 'parsed', None)
        if not data:
            # Final fallback to manual parse if parsed is missing
            try:
                import json
                clean_text = response.text.strip()
                if "```json" in clean_text:
                    clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_text:
                    clean_text = clean_text.split("```")[1].split("```")[0].strip()
                data = json.loads(clean_text)
            except:
                print(f"[!] Critical Parsing Error.")
                print(f"Raw Output: {response.text[:1000]}...")
                return

        project_name = data.get('name', 'daily-strike')
        print(f"[+] Successfully parsed data for project: {project_name}")

        # Create Folder with Name and Date
        project_name = data.get('name', 'daily-strike')
        project_slug = slugify(project_name)
        folder_name = f"{DATE_STR}-{project_slug}"
        path = os.path.join(PROJECT_DIR, folder_name)
        print(f"[*] Creating folder: {path}")
        os.makedirs(path, exist_ok=True)
        
        # Save project files
        files_to_save = {
            "main.py": data.get('code', ''),
            "README.md": data.get('readme', ''),
            "requirements.txt": "\n".join(data.get('requirements', [])) if isinstance(data.get('requirements'), list) else str(data.get('requirements', ''))
        }
        
        for filename, content in files_to_save.items():
            fpath = os.path.join(path, filename)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[+] Saved {filename} to {fpath}")

        print(f"[+] Project Packaged locally: {folder_name}")
        
        # Deploy to GitHub
        print("[*] Synchronizing with GitHub...")
        subprocess.run(['git', 'add', '.'], cwd=PROJECT_DIR, shell=True, check=True)
        status = subprocess.run(['git', 'status', '--porcelain'], cwd=PROJECT_DIR, shell=True, capture_output=True, text=True)
        
        if status.stdout.strip():
            print(f"[*] Changes detected. Committing and pushing...")
            subprocess.run(['git', 'commit', '-m', f"Strike [{goal['title']}]: {project_name}"], cwd=PROJECT_DIR, shell=True, check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=PROJECT_DIR, shell=True, check=True)
            print(f"[++++] SYSTEM STRIKE SUCCESSFUL: {folder_name} deployed to GitHub.")
        else:
            print("[!] No changes recorded to commit. (Maybe project already exists or git is up to date)")
        
    except Exception as e:
        print(f"[!] System Failure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    execute_strike()