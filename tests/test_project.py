import sys
import tomllib
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


class ProjectSmokeTests(unittest.TestCase):
    def test_package_imports(self):
        import mikoshi

        self.assertTrue(mikoshi.__doc__)

    def test_project_metadata_is_readable(self):
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as project_file:
            project = tomllib.load(project_file)["project"]

        self.assertEqual(project["name"], "mikoshi")
        self.assertEqual(project["version"], "0.1.0")
        self.assertEqual(project["requires-python"], ">=3.14")


if __name__ == "__main__":
    unittest.main()
