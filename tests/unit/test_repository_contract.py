"""The repository must keep the shape and safety properties the master spec requires.

Cheap structural guards so drift is caught by the suite rather than by review.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRECTORIES = [
    "docs/product",
    "docs/architecture",
    "docs/ai",
    "strategies/trend",
    "strategies/ark",
    "mt5/TrendEA",
    "mt5/ARKEA",
    "mt5/DataBridge",
    "external-data/CME",
    "external-data/TradingView",
    "external-data/Calendar",
    "external-data/News",
    "agentic-brain",
    "backtesting/replay",
    "backtesting/historical-data",
    "tests",
    "infrastructure",
    "scripts",
    "monitoring",
    "legacy",
]

REQUIRED_FILES = [
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    ".gitignore",
    "docs/product/MASTER_SPEC_v1.0.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/architecture/SOURCE_INVENTORY.md",
    "docs/ai/DEVELOPMENT_WORKFLOW.md",
]

# Spec section 26: these must never be committable.
SECRET_PATTERNS = [".env", "*.key", "*.pem", "secrets/"]

# Spec section 14: gold only.
FORBIDDEN_INSTRUMENTS = ["BTCXAU", "ETHXAU"]


class RepositoryContractTest(unittest.TestCase):
    def test_required_directories_exist(self):
        for relative in REQUIRED_DIRECTORIES:
            with self.subTest(directory=relative):
                self.assertTrue((REPO_ROOT / relative).is_dir())

    def test_required_files_exist(self):
        for relative in REQUIRED_FILES:
            with self.subTest(file=relative):
                path = REPO_ROOT / relative
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 0)

    def test_gitignore_blocks_secrets(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, gitignore)

    def test_no_forbidden_instruments_outside_legacy(self):
        """Gold only. Legacy is exempt: it is preserved as-is and never executed."""
        searchable = [
            path
            for extension in ("*.py", "*.mq5", "*.mqh", "*.json", "*.yaml", "*.yml")
            for path in REPO_ROOT.rglob(extension)
            if "legacy" not in path.parts
            and ".venv" not in path.parts
            and "tests" not in path.parts
        ]
        for path in searchable:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for instrument in FORBIDDEN_INSTRUMENTS:
                with self.subTest(file=path.name, instrument=instrument):
                    self.assertNotIn(instrument, content)


if __name__ == "__main__":
    unittest.main()
