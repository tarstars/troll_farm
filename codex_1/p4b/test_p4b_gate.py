import sys
import gzip
import json
import tempfile
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

    def archive(self, commands):
        tmp = tempfile.NamedTemporaryFile(suffix=".jsonl.gz", delete=False)
        tmp.close()
        row = {"map_id": "m000", "seat": 0,
               "artifacts": {"candidate_commands": commands}}
        with gzip.open(tmp.name, "wt", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        return Path(tmp.name)

    def test_none_is_not_applicable_with_banner_msg(self):
        path = self.archive("MSG readable_banner;WAIT\nWAIT\n")
        try:
            result = p.evaluate_not_applicable(path)
            self.assertEqual(result["status"], "NOT_APPLICABLE")
            self.assertEqual(result["errors"], [])
        finally:
            path.unlink()

    def test_none_fails_closed_on_narrate_payload(self):
        path = self.archive("MSG NARRATE v4 t=1;WAIT\n")
        try:
            result = p.evaluate_not_applicable(path)
            self.assertEqual(result["status"], "GATE_UNREADY")
            self.assertEqual(len(result["errors"]), 1)
        finally:
            path.unlink()

    def test_not_applicable_comparison_is_explicit(self):
        na = {"status": "NOT_APPLICABLE", "unit_rows": [], "failed_units": []}
        ready = {"status": "READY", "unit_rows": [], "failed_units": []}
        self.assertEqual(p.compare(ready, na)["status"], "NOT_APPLICABLE")

    def test_v6_fixture_decoder_contract(self):
        class V6Fixture:
            @staticmethod
            def decode(payload):
                self.assertIn("NARRATE v6", payload)
                self.assertIn("/k=2", payload)
                return 7, {0: ("TREE(3,4)", "TREE(3,4)", "P", 0, 2)}, [0], False, {"kp": 1}

        turn, units = p.decode_units(
            V6Fixture(),
            "MSG NARRATE v6 t=7 u0=TREE(3,4)/TREE(3,4)/r=P/b=0/k=2 kp=1")
        self.assertEqual(turn, 7)
        self.assertEqual(units[0][1], "TREE(3,4)")
        self.assertEqual(units[0][2], "P")

    def test_v6_five_field_tuple_runs_through_evaluate(self):
        class Unit:
            id = 0

        class State:
            @staticmethod
            def own_units():
                return [Unit()]

        class Trace:
            T = 1

            @staticmethod
            def state(_turn):
                return State()

        class TraceDetectors:
            @staticmethod
            def build_trace(_transcript, _commands):
                return Trace()

        class V6Fixture:
            @staticmethod
            def msg_fragments(_line):
                return ["MSG NARRATE v6 t=1 u0=TREE(3,4)/TREE(3,4)/r=P/b=0/k=2 kp=1"]

            @staticmethod
            def decode(_payload):
                return 1, {0: ("TREE(3,4)", "TREE(3,4)", "P", 0, 2)}, [0], False, {"kp": 1}

        tmp = tempfile.NamedTemporaryFile(suffix=".jsonl.gz", delete=False)
        tmp.close()
        row = {"map_id": "m000", "seat": 0,
               "artifacts": {"candidate_commands": "WAIT\n", "candidate_transcript": ""}}
        path = Path(tmp.name)
        try:
            with gzip.open(path, "wt", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")
            result = p.evaluate(path, TraceDetectors(), V6Fixture(), "v6")
            self.assertEqual(result["status"], "READY")
            self.assertEqual(result["errors"], [])
            self.assertEqual(result["unit_rows"][0]["unit_id"], 0)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
