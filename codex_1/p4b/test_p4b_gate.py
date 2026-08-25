import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p4b_gate as p


class P4bUnitTests(unittest.TestCase):
    def rows(self, n, available=True, progress_at=()):
        return [{"turn": i + 1, "available_concrete": available,
                 "progress": i + 1 in progress_at} for i in range(n)]

    def test_exact_60_is_episode(self):
        self.assertEqual(p.maximal_runs(self.rows(60))[0]["length"], 60)

    def test_59_is_not_episode(self):
        self.assertEqual(p.maximal_runs(self.rows(59)), [])

    def test_progress_breaks_window(self):
        self.assertEqual(p.maximal_runs(self.rows(119, progress_at={60})), [])

    def test_availability_required(self):
        rows = self.rows(60)
        rows[30]["available_concrete"] = False
        self.assertEqual(p.maximal_runs(rows), [])

    def test_teammate_progress_not_credited(self):
        self.assertEqual(p.maximal_runs(self.rows(194))[0]["length"], 194)

    def test_concrete_grammar(self):
        for target in ("SHACK", "BANK(1,2)", "CELL(1,2)", "TREE(1,2)"):
            self.assertTrue(p.concrete(target))
        for target in ("NONE", "ABSENT", "IRON(1,2)"):
            self.assertFalse(p.concrete(target))


if __name__ == "__main__":
    unittest.main()
