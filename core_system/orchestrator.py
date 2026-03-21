import os, json, subprocess, re
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# --- CONFIG ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
PROJECT_DIR = r"C:\Users\sindh\OneDrive\Desktop\daily-projects"
GOALS_PATH = os.path.join(os.path.dirname(__file__), "GOALS.md")
DATE_STR = datetime.now().strftime("%Y-%m-%d")

client = genai.Client(api_key=API_KEY)

def slugify(text):
    """Convert text to a filename-safe format."""
    return re.sub(r'[\s\W_]+', '-', text.lower()).strip('-')

def execute_strike():
    if not os.path.exists(GOALS_PATH): return print("[!] GOALS.md missing.")
    with open(GOALS_PATH, 'r') as f: goals = f.read()

    prompt = (
        f"Goals: {goals}. Task: Create a unique Python project for {DATE_STR}. "
        "Return ONLY a JSON object with four keys: "
        "'name' (a short descriptive name), 'code' (the Python source), "
        "'readme' (Markdown documentation), and 'requirements' (pip dependencies list). "
        "No markdown backticks."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # Handle potential markdown artifacts in JSON response
        clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        # Create Folder with Name and Date
        project_slug = slugify(data.get('name', 'daily-strike'))
        folder_name = f"{DATE_STR}-{project_slug}"
        path = os.path.join(PROJECT_DIR, folder_name)
        os.makedirs(path, exist_ok=True)
        
        # Save project files
        with open(os.path.join(path, "main.py"), "w", encoding="utf-8") as f: 
            f.write(data['code'])
        with open(os.path.join(path, "README.md"), "w", encoding="utf-8") as f: 
            f.write(data['readme'])
        
        # Handle requirements string or list
        reqs = data.get('requirements', "")
        if isinstance(reqs, list):
            reqs = "\n".join(reqs)
        with open(os.path.join(path, "requirements.txt"), "w", encoding="utf-8") as f: 
            f.write(reqs)

        print(f"[+] Project Packaged: {folder_name}")
        
        # Deploy to GitHub
        print("[*] Synchronizing with GitHub...")
        subprocess.run(['git', 'add', '.'], cwd=PROJECT_DIR, shell=True, check=True)
        subprocess.run(['git', 'commit', '-m', f"Strike: {data.get('name', DATE_STR)}"], cwd=PROJECT_DIR, shell=True, check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=PROJECT_DIR, shell=True, check=True)
        
        print(f"[++++] SYSTEM STRIKE SUCCESSFUL: {folder_name} Deployed.")
        
    except Exception as e:
        print(f"[!] Failure: {e}")

if __name__ == "__main__":
    execute_strike()