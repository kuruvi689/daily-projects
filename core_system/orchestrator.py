import os, json, subprocess
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

def execute_strike():
    if not os.path.exists(GOALS_PATH): return print("[!] GOALS.md missing.")
    with open(GOALS_PATH, 'r') as f: goals = f.read()

    prompt = f"Goals: {goals}. Task: Create a Python project for {DATE_STR}. Return ONLY a JSON object with keys 'code' and 'readme'. No markdown backticks."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        # Handle potential markdown artifacts in JSON response
        clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        path = os.path.join(PROJECT_DIR, f"project_{DATE_STR}")
        os.makedirs(path, exist_ok=True)
        
        with open(os.path.join(path, "main.py"), "w", encoding="utf-8") as f: f.write(data['code'])
        with open(os.path.join(path, "README.md"), "w", encoding="utf-8") as f: f.write(data['readme'])
        
        subprocess.run(['git', 'add', '.'], cwd=PROJECT_DIR, shell=True, check=True)
        subprocess.run(['git', 'commit', '-m', f"Strike: {DATE_STR}"], cwd=PROJECT_DIR, shell=True, check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=PROJECT_DIR, shell=True, check=True)
        print(f"[++++] SYSTEM STRIKE SUCCESSFUL: {DATE_STR}")
    except Exception as e:
        print(f"[!] Failure: {e}")

if __name__ == "__main__":
    execute_strike()