import datetime
import tempfile
import unittest
from pathlib import Path

from core_system import orchestrator


class OrchestratorTests(unittest.TestCase):
    def test_current_date_str_converts_to_ist(self):
        utc_time = datetime.datetime(2026, 6, 15, 20, 45, tzinfo=datetime.timezone.utc)
        self.assertEqual(orchestrator.current_date_str(utc_time), "2026-06-16")

    def test_project_path_is_complete_requires_expected_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "2026-06-16-sample-project"
            project.mkdir()
            self.assertFalse(orchestrator.project_path_is_complete(project))

            for name in orchestrator.REQUIRED_PROJECT_FILES:
                (project / name).write_text("x", encoding="utf-8")

            self.assertTrue(orchestrator.project_path_is_complete(project))

    def test_ensure_today_project_exists_rejects_missing_or_incomplete_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            with self.assertRaises(orchestrator.StrikeError):
                orchestrator.ensure_today_project_exists(project_dir, "2026-06-16")

            incomplete = project_dir / "2026-06-16-broken-project"
            incomplete.mkdir()
            (incomplete / "README.md").write_text("x", encoding="utf-8")
            with self.assertRaises(orchestrator.StrikeError):
                orchestrator.ensure_today_project_exists(project_dir, "2026-06-16")

            for name in orchestrator.REQUIRED_PROJECT_FILES:
                (incomplete / name).write_text("x", encoding="utf-8")

            projects = orchestrator.ensure_today_project_exists(project_dir, "2026-06-16")
            self.assertEqual([p.name for p in projects], ["2026-06-16-broken-project"])


if __name__ == "__main__":
    unittest.main()
