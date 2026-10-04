import importlib.util
import json
import unittest
from pathlib import Path

from core_system import strike_core
from core_system.strike_core import StrikeError

SPEC = importlib.util.spec_from_file_location("strike_api", Path(__file__).resolve().parent.parent / "api" / "strike.py")
strike_api = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(strike_api)

GOOD_PROJECT = {"name": "Lead Scorer Pro", "code": "print(1)", "readme": "# x", "requirements": ["requests", " "]}


class FakeGroq:
    def __init__(self, data=GOOD_PROJECT):
        self.data = data
        self.prompts = []

    def chat_json(self, prompt, schema=None):
        self.prompts.append(prompt)
        self.schema = schema
        return self.data, "openai/gpt-oss-120b"


class FakePublisher:
    def __init__(self, folders=("2026-03-16-wealth-projection-tool", "core_system", "api")):
        self.folders = list(folders)
        self.commits = []

    def list_folders(self):
        return self.folders

    def read_text(self, path):
        return "BACKLOG CONTENT" if path == "BACKLOG.md" else None

    def commit_files(self, files, message):
        self.commits.append((files, message))
        return "abc123"


class AuthTests(unittest.TestCase):
    def test_requires_matching_bearer_secret(self):
        self.assertTrue(strike_api.is_authorized("Bearer s3cret", "s3cret"))
        self.assertFalse(strike_api.is_authorized("Bearer wrong", "s3cret"))
        self.assertFalse(strike_api.is_authorized(None, "s3cret"))
        self.assertFalse(strike_api.is_authorized("Bearer ", ""))  # unset secret never authorizes


class RunStrikeTests(unittest.TestCase):
    def test_creates_and_commits_project(self):
        groq, publisher = FakeGroq(), FakePublisher()
        status, body = strike_api.run_strike(env={}, groq=groq, publisher=publisher)

        self.assertEqual(status, 201)
        self.assertEqual(body["status"], "created")
        self.assertTrue(body["folder"].endswith("-lead-scorer-pro"))
        files, message = publisher.commits[0]
        self.assertEqual(sorted(p.split("/")[1] for p in files), ["README.md", "main.py", "requirements.txt"])
        self.assertEqual(files[f"{body['folder']}/requirements.txt"], "requests\n")
        self.assertIn("Auto-Strike:", message)
        self.assertIn("BACKLOG CONTENT", groq.prompts[0])
        self.assertIn("wealth-projection-tool", groq.prompts[0])  # told not to repeat it
        self.assertNotIn("core_system", groq.prompts[0].split("ALREADY BUILT")[1])

    def test_skips_when_today_already_built(self):
        today = f"{strike_core.current_date_str()}-done"
        groq, publisher = FakeGroq(), FakePublisher(folders=[today])
        status, body = strike_api.run_strike(env={}, groq=groq, publisher=publisher)
        self.assertEqual((status, body["status"], body["folder"]), (200, "skipped", today))
        self.assertEqual(groq.prompts, [])
        self.assertEqual(publisher.commits, [])

    def test_dry_run_generates_without_committing(self):
        today = f"{strike_core.current_date_str()}-done"
        groq, publisher = FakeGroq(), FakePublisher(folders=[today])
        status, body = strike_api.run_strike(env={}, groq=groq, publisher=publisher, dry_run=True)
        self.assertEqual((status, body["status"]), (200, "dry_run"))
        self.assertEqual(body["lines"]["main.py"], 1)
        self.assertEqual(publisher.commits, [])

    def test_invalid_model_payload_is_not_committed(self):
        publisher = FakePublisher()
        with self.assertRaises(StrikeError):
            strike_api.run_strike(env={}, groq=FakeGroq({"name": "x"}), publisher=publisher)
        self.assertEqual(publisher.commits, [])


class StrikeCoreTests(unittest.TestCase):
    def test_folder_name_is_slugged_and_bounded(self):
        self.assertEqual(strike_core.folder_name_for("2026-10-04", "My Tool!"), "2026-10-04-my-tool")
        self.assertEqual(strike_core.folder_name_for("2026-10-04", "!!!"), "2026-10-04-daily-strike")
        self.assertLessEqual(len(strike_core.folder_name_for("2026-10-04", "a" * 200)), 71)

    def test_parse_json_text_handles_fences(self):
        self.assertEqual(strike_core.parse_json_text('```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(strike_core.parse_json_text('{"a": 1}'), {"a": 1})

    def test_parse_json_text_ignores_fences_inside_strings(self):
        raw = json.dumps({"name": "x", "readme": "Example:\n```json\n{\"a\": 1}\n```\n"})
        self.assertEqual(strike_core.parse_json_text(raw)["readme"], "Example:\n```json\n{\"a\": 1}\n```\n")

    def test_parse_json_text_repairs_bad_escapes_and_control_chars(self):
        raw = '{"code": "re.match(r\'\\d+\', s)\n\tx = 1"}'  # bare \d plus raw newline/tab
        self.assertEqual(strike_core.parse_json_text(raw), {"code": "re.match(r'\\d+', s)\n\tx = 1"})
        self.assertEqual(strike_core.parse_json_text('{"a": "x\\\\d \\n"}'), {"a": "x\\d \n"})

    def test_validate_rejects_bad_requirements(self):
        with self.assertRaises(StrikeError):
            strike_core.validate_project_payload({**GOOD_PROJECT, "requirements": "requests"})


if __name__ == "__main__":
    unittest.main()
