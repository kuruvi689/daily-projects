import os
from dotenv import load_dotenv
from google import genai
import subprocess
from datetime import datetime

# --- CONFIGURATION (The System Soul) ---
# Load the environment variables from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") 
PROJECT_DIR = r"C:\Users\sindh\OneDrive\Desktop\daily-projects"
GOALS_PATH = os.path.join(PROJECT_DIR, "GOALS.md")
DATE_STR = datetime.now().strftime("%Y-%m-%d")

# Initialize the Intelligence Layer
client = genai.Client(api_key=API_KEY)

def get_strategic_prompt():
    if os.path.exists(GOALS_PATH):
        with open(GOALS_PATH, 'r') as f:
            goals = f.read()
    else:
        goals = "AI Mastery, Financial Independence, Automation Systems"

    return f"""
    Act as the Teddy³ Strategic Architect. 
    Context Goals: {goals}
    Task: Create a single-file Python project for {DATE_STR}.
    Requirements: 150-300 lines, functional, documented. 
    Output: Provide ONLY the raw Python code. No markdown backticks.
    """

def run_git_command(command, cwd):
    """Executes git commands and catches actual failures."""
    try:
        subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Git Error: {e.stderr.strip()}")
        return False

def execute_strike():
    # 1. GENERATE CODE (The Strike)
    print(f"[*] Triggering Intelligence Strike for {DATE_STR}...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=get_strategic_prompt()
        )
        code_content = response.text.strip()
        # Remove any accidental markdown artifacts
        code_content = code_content.replace("```python", "").replace("```", "").strip()
    except Exception as e:
        print(f"[!] API Failure: {e}")
        return

    # 2. FILE SYSTEM MECHANICS
    folder_name = f"project_{DATE_STR}"
    path = os.path.join(PROJECT_DIR, folder_name)
    os.makedirs(path, exist_ok=True)
    
    file_path = os.path.join(path, "main.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_content)
    print(f"[+] Code synthesized: {file_path}")

    # 3. GIT DEPLOYMENT (The Proof)
    print("[*] Deploying to GitHub...")
    # Initialize repo if it doesn't exist
    if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
        run_git_command(['git', 'init'], PROJECT_DIR)
    
    run_git_command(['git', 'add', '.'], PROJECT_DIR)
    if run_git_command(['git', 'commit', '-m', f"Teddy Strike: {DATE_STR}"], PROJECT_DIR):
        if run_git_command(['git', 'push', 'origin', 'main'], PROJECT_DIR):
            print("[++++] SYSTEM STRIKE SUCCESSFUL: Deployment Verified.")
        else:
            print("[!] Push failed. Check your remote 'origin' settings.")

if __name__ == "__main__":
    execute_strike()