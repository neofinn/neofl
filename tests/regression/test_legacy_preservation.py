"""Legacy source is read-only reference material (master spec section 6, 34).

These tests fail loudly if preserved source is deleted, or if the files the spec
warns about go missing before their rules have been extracted.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY = REPO_ROOT / "legacy"

EXPECTED_FAMILIES = [
    "gold-dual-engine-5.x-6.x",
    "ark-7.1-standalone",
    "candle-revisit-master-brain",
    "ark-jobbing-backtest-v3.00",
    "observer-network",
]

# Named directly in master spec section 6 and 34.
SPEC_NAMED_FILES = [
    "ark-jobbing-backtest-v3.00/ARK/NeoFL_ARK_Backtest_v3_00.mq5",
    "gold-dual-engine-5.x-6.x/NeoFL_GOLD_6.6_ARK_PREEXECUTION_LOCK.mq5",
]


class LegacyPreservationTest(unittest.TestCase):
    def test_all_families_present(self):
        for family in EXPECTED_FAMILIES:
            with self.subTest(family=family):
                self.assertTrue((LEGACY / family).is_dir())

    def test_spec_named_files_preserved(self):
        for relative in SPEC_NAMED_FILES:
            with self.subTest(file=relative):
                path = LEGACY / relative
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 0)

    def test_inventory_documents_every_family(self):
        inventory = (REPO_ROOT / "docs" / "architecture" / "SOURCE_INVENTORY.md").read_text(
            encoding="utf-8"
        )
        for family in EXPECTED_FAMILIES:
            with self.subTest(family=family):
                self.assertIn(family, inventory)

    def test_legacy_source_count_has_not_shrunk(self):
        sources = list(LEGACY.rglob("*.mq5")) + list(LEGACY.rglob("*.mqh"))
        self.assertGreaterEqual(len(sources), 36)


if __name__ == "__main__":
    unittest.main()
