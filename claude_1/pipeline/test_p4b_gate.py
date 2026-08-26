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

    def test_v6_five_field_unit_tuple(self):
        class V6:
            @staticmethod
            def decode(payload):
                self.assertIn("NARRATE v6", payload)
                return 7, {0: ("TREE(3,4)", "SHACK", "P", 0, 2)}, [0], False, {"kp": 1}

        turn, units = p.decode_units(V6(), "MSG NARRATE v6 t=7")
        self.assertEqual(turn, 7)
        self.assertEqual(units[0][1:3], ("SHACK", "P"))


class P4bPanelWiringTests(unittest.TestCase):
    """The --p4b integration surface (claude_1, 2026-08-25)."""

    def arm(self, episodes=0, tripwire=(), status="READY"):
        return {"archive": "a", "archive_sha256": "0" * 64, "status": status,
                "errors": [], "games": 240, "map_ids": 120,
                "both_seats_per_map": True,
                "totals": {"episodes": episodes, "unit_lives": 384,
                           "observable_transitions": 10, "available_turns": 5,
                           "progress_turns": 1},
                "failed_units": [], "failed_games": [], "unit_rows": [],
                "blind_population": {},
                "longest_run_distribution": {"min": 0, "q1": 1, "median": 2,
                                             "q3": 3, "max": 4},
                "idle_share_above_1_5_pct": [], "tripwire_45": list(tripwire)}

    def test_render_has_no_verdict_authority(self):
        text = "\n".join(p.render_markdown(
            {"definition": {"W": 60, "k": 60, "tripwire": 45},
             "arms": {"panel": self.arm()}, "comparisons": {},
             "controls": {"K3_tripwire_clear": True}}))
        self.assertIn("does not change the panel verdict", text)
        self.assertIn("## P4b per-troll stall gate (report tier)", text)

    def test_render_names_a_gate_unready_arm(self):
        arm = self.arm(status="GATE_UNREADY")
        arm["errors"] = ["m000 turn 1: telemetry decode"]
        text = "\n".join(p.render_markdown(
            {"definition": {"W": 60, "k": 60, "tripwire": 45},
             "arms": {"panel": arm}, "comparisons": {}, "controls": {}}))
        self.assertIn("GATE_UNREADY", text)
        self.assertIn("telemetry decode", text)

    def test_tripwire_reported_as_undercount_warning(self):
        text = "\n".join(p.render_markdown(
            {"definition": {"W": 60, "k": 60, "tripwire": 45},
             "arms": {"panel": self.arm()}, "comparisons": {},
             "controls": {}}))
        self.assertIn("under-count warning, not a pass", text)


if __name__ == "__main__":
    unittest.main()
