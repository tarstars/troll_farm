#!/usr/bin/env python3
"""Unit tests for pre_review.py - synthetic mini-cases per mechanized check.

Run: python3 -m unittest test_pre_review -v   (from claude_1/pipeline/)

Each failure class is exercised in both directions on fabricated inputs:
  - trace-provenance: a scripted (hand-edited) trace caught by regeneration;
    an honest candidate-driven trace passing; a scripted control allowed;
    a scripted CRITICAL trace blocked.
  - single-model: a planted divergent max(eta_opp, ...) line caught outside
    the oracle; the same line explained inside a verified importer; an
    allowed_importer that does not import caught; comment-only mention not
    blocking.
  - red-reason: a red pair that passes on the old bytes caught; a red pair
    failing with the wrong signature caught; a right-reason red pair clear.
  - claims-coverage: a scripted-control entry on a critical invariant
    caught; a missing evidence path caught; a critical invariant with no
    entry caught (SPEC_TEST_GAP); a missing required deliverable caught
    (MISSING_DELIVERABLE); an unfed mechanized ledger class caught unless
    waived.
  - CLI exit-code semantics: 0 CLEAR / 1 BLOCK / 2 tool or config error.

Stdlib only; rustc required (same requirement as the tool itself).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRE_REVIEW = HERE / "pre_review.py"

sys.path.insert(0, str(HERE))
import pre_review  # noqa: E402

# A deterministic toy bot: for each input line, prints "GO <n>".
TOY_BOT = r"""
use std::io::{self, BufRead};
fn main() {
    let stdin = io::stdin();
    let mut n = 0u32;
    for line in stdin.lock().lines() {
        let _ = line.unwrap();
        n += 1;
        println!("GO {}", n);
    }
}
"""

MINI_LEDGER = {
    "classes": [
        {"id": "SCRIPTED_TRACE", "detection": "mechanized",
         "pre_review_check": "trace-provenance"},
        {"id": "MODEL_DIVERGENCE", "detection": "mechanized",
         "pre_review_check": "single-model"},
        {"id": "RED_WRONG_REASON", "detection": "mechanized",
         "pre_review_check": "red-reason"},
        {"id": "VACUOUS_EVIDENCE", "detection": "mechanized",
         "pre_review_check": "claims-coverage"},
        {"id": "INSTRUMENT_GAP", "detection": "checklist",
         "pre_review_check": None},
    ]
}


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="pre-review-test-")
        self.dir = Path(self._tmp.name)
        (self.dir / "ledger.json").write_text(json.dumps(MINI_LEDGER))

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name: str, text: str) -> Path:
        p = self.dir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def config(self, **sections) -> Path:
        cfg = {"task": "unit-test", "ledger": "ledger.json"}
        cfg.update(sections)
        return self.write("config.json", json.dumps(cfg))

    def run_check(self, runner, **sections):
        ctx = pre_review.Context(self.config(**sections))
        return runner(ctx)

    def classes(self, result):
        return sorted({f["class"] for f in result["findings"]})


class TestTraceProvenance(Base):
    def setUp(self):
        super().setUp()
        self.write("bot.rs", TOY_BOT)
        self.write("transcript.txt", "s1\ns2\ns3\n")
        self.write("good-commands.txt", "GO 1\nGO 2\nGO 3\n")
        # a hand-edited ("scripted") command stream the bot never emits
        self.write("bad-commands.txt", "GO 1\nATTACK NOW\nGO 3\n")

    def trace(self, commands, **kw):
        base = {"name": "toy", "transcript": "transcript.txt",
                "commands": commands, "binary_source": "bot.rs",
                "crate_name": "toy_bot"}
        base.update(kw)
        return base

    def test_candidate_driven_trace_passes(self):
        res = self.run_check(pre_review.run_trace_provenance,
                             traces=[self.trace("good-commands.txt")])
        self.assertEqual(res["verdict"], "CLEAR")

    def test_fabricated_scripted_trace_caught_by_regeneration(self):
        res = self.run_check(pre_review.run_trace_provenance,
                             traces=[self.trace("bad-commands.txt")])
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertEqual(self.classes(res), ["SCRIPTED_TRACE"])
        self.assertIn("line 2", res["findings"][0]["detail"])
        self.assertIn("ATTACK NOW", res["findings"][0]["detail"])

    def test_declared_scripted_control_allowed_but_listed(self):
        res = self.run_check(
            pre_review.run_trace_provenance,
            traces=[self.trace("bad-commands.txt", scripted=True,
                               critical=False)])
        self.assertEqual(res["verdict"], "CLEAR")
        self.assertTrue(any("scripted control" in n for n in res["info"]))

    def test_scripted_critical_trace_blocks(self):
        res = self.run_check(
            pre_review.run_trace_provenance,
            traces=[self.trace("bad-commands.txt", scripted=True,
                               critical=True)])
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertEqual(self.classes(res), ["SCRIPTED_TRACE"])


class TestSingleModel(Base):
    PATTERNS = ["max\\(\\s*eta_opp", "exact_chops\\s*<\\s*eta_opp"]

    def setUp(self):
        super().setUp()
        self.write("the_oracle.py", "def deadline():\n    return 1\n")

    def oracle(self, scan, importers=(), mirrors=()):
        return {"name": "THE_ORACLE", "module_path": "the_oracle.py",
                "quantity_patterns": list(self.PATTERNS),
                "scan_files": list(scan),
                "allowed_importers": list(importers),
                "allowed_mirrors": list(mirrors)}

    def test_planted_divergent_arithmetic_caught(self):
        self.write("rogue.py", "deadline = max(eta_opp, cooldown)\n")
        res = self.run_check(pre_review.run_single_model,
                             oracles=[self.oracle(["rogue.py"])])
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertEqual(self.classes(res), ["MODEL_DIVERGENCE"])
        self.assertIn("rogue.py:1", res["findings"][0]["subject"])

    def test_hit_inside_verified_importer_is_explained(self):
        self.write("user.py",
                   "import the_oracle\n"
                   "check = max(eta_opp, x)  # diagnostic of voided value\n")
        res = self.run_check(
            pre_review.run_single_model,
            oracles=[self.oracle(["user.py"], importers=[{"path": "user.py"}])])
        self.assertEqual(res["verdict"], "CLEAR")
        self.assertTrue(any("explained hit" in n for n in res["info"]))

    def test_listed_importer_that_does_not_import_blocks(self):
        self.write("fake.py", "exact_chops < eta_opp_now\n")
        res = self.run_check(
            pre_review.run_single_model,
            oracles=[self.oracle(["fake.py"], importers=[{"path": "fake.py"}])])
        self.assertEqual(res["verdict"], "BLOCK")
        details = " | ".join(f["detail"] for f in res["findings"])
        self.assertIn("no import statement", details)

    def test_comment_only_mention_not_blocking(self):
        self.write("prose.py", "# legacy: max(eta_opp, cd) was voided\n")
        res = self.run_check(pre_review.run_single_model,
                             oracles=[self.oracle(["prose.py"])])
        self.assertEqual(res["verdict"], "CLEAR")
        self.assertTrue(any("comment-only" in n for n in res["info"]))

    def test_missing_oracle_module_blocks(self):
        oracle = self.oracle([])
        oracle["module_path"] = "nonexistent_oracle.py"
        res = self.run_check(pre_review.run_single_model, oracles=[oracle])
        self.assertEqual(res["verdict"], "BLOCK")

    def test_mirror_without_required_marker_blocks(self):
        self.write("mirror.rs", "let d = eta_opp.max(ripe);\n")
        oracle = self.oracle(["mirror.rs"],
                             mirrors=[{"path": "mirror.rs",
                                       "marker_regex": "THE_ORACLE"}])
        oracle["quantity_patterns"] = ["eta_opp\\w*\\s*\\.\\s*max\\s*\\("]
        res = self.run_check(pre_review.run_single_model, oracles=[oracle])
        self.assertEqual(res["verdict"], "BLOCK")


class TestRedReason(Base):
    CHECKER = (
        "import sys\n"
        "text = open(sys.argv[1]).read()\n"
        "if 'BUG' in text:\n"
        "    print('detected off-by-one in deadline')\n"
        "    sys.exit(1)\n"
        "print('all green')\n"
        "sys.exit(0)\n")

    def setUp(self):
        super().setUp()
        self.write("checker.py", self.CHECKER)
        self.write("old-buggy.rs", "// BUG: off by one\n")
        self.write("old-clean.rs", "// nothing wrong here\n")

    def pair(self, old, regexes):
        return {"name": "pair", "cwd": ".",
                "check_cmd": [sys.executable, "checker.py", "{source}"],
                "old_source": old,
                "expected_failure_signature": {"must_match_regexes": regexes}}

    def test_red_for_right_reason_clear(self):
        res = self.run_check(
            pre_review.run_red_reason,
            red_green_pairs=[self.pair("old-buggy.rs", ["off-by-one"])])
        self.assertEqual(res["verdict"], "CLEAR")

    def test_pass_on_old_bytes_caught(self):
        res = self.run_check(
            pre_review.run_red_reason,
            red_green_pairs=[self.pair("old-clean.rs", ["off-by-one"])])
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertEqual(self.classes(res), ["RED_WRONG_REASON"])
        self.assertIn("exits 0 on the old bytes", res["findings"][0]["detail"])

    def test_wrong_failure_signature_caught(self):
        res = self.run_check(
            pre_review.run_red_reason,
            red_green_pairs=[self.pair("old-buggy.rs",
                                       ["stale-ripen arrival case"])])
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertEqual(self.classes(res), ["RED_WRONG_REASON"])
        self.assertIn("signature", res["findings"][0]["detail"])


class TestClaimsCoverage(Base):
    def base_sections(self, entries, critical=("I-1",), **extra):
        self.write("claims.json", json.dumps(entries))
        sections = {
            "traces": [{"name": "t", "transcript": "x", "commands": "x",
                        "binary_source": "x", "crate_name": "x",
                        "scripted": False}],
            "oracles": [{"name": "O"}],
            "red_green_pairs": [{"name": "p"}],
            "claims": {"path": "claims.json",
                       "critical_invariants": list(critical)},
        }
        sections.update(extra)
        return sections

    def entry(self, inv="I-1", etype="candidate-driven",
              path="evidence.txt"):
        return {"invariant": inv, "evidence_type": etype,
                "evidence_path": path}

    def test_good_claims_clear(self):
        self.write("evidence.txt", "trace bytes\n")
        res = self.run_check(pre_review.run_claims_coverage,
                             **self.base_sections([self.entry()]))
        self.assertEqual(res["verdict"], "CLEAR")

    def test_scripted_critical_entry_caught(self):
        self.write("evidence.txt", "x\n")
        entries = [self.entry(etype="scripted-control"),
                   self.entry()]  # second entry keeps I-1 guarded
        res = self.run_check(pre_review.run_claims_coverage,
                             **self.base_sections(entries))
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertIn("VACUOUS_EVIDENCE", self.classes(res))

    def test_missing_evidence_path_caught(self):
        res = self.run_check(pre_review.run_claims_coverage,
                             **self.base_sections(
                                 [self.entry(path="ghost.txt")]))
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertIn("VACUOUS_EVIDENCE", self.classes(res))

    def test_unguarded_critical_invariant_caught(self):
        self.write("evidence.txt", "x\n")
        res = self.run_check(pre_review.run_claims_coverage,
                             **self.base_sections([self.entry()],
                                                  critical=("I-1", "I-99")))
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertIn("SPEC_TEST_GAP", self.classes(res))

    def test_missing_required_deliverable_caught(self):
        self.write("evidence.txt", "x\n")
        res = self.run_check(
            pre_review.run_claims_coverage,
            **self.base_sections([self.entry()],
                                 required_deliverables=["not-there.md"]))
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertIn("MISSING_DELIVERABLE", self.classes(res))

    def test_unfed_mechanized_ledger_class_caught_and_waivable(self):
        self.write("evidence.txt", "x\n")
        sections = self.base_sections([self.entry()])
        del sections["red_green_pairs"]   # RED_WRONG_REASON now unfed
        res = self.run_check(pre_review.run_claims_coverage, **sections)
        self.assertEqual(res["verdict"], "BLOCK")
        self.assertTrue(any(f["subject"] == "RED_WRONG_REASON"
                            for f in res["findings"]))
        sections["waivers"] = [{"class_id": "RED_WRONG_REASON",
                                "reason": "no old bytes exist for round 1"}]
        res = self.run_check(pre_review.run_claims_coverage, **sections)
        self.assertEqual(res["verdict"], "CLEAR")

    def test_invalid_evidence_type_is_tool_error(self):
        self.write("evidence.txt", "x\n")
        sections = self.base_sections([self.entry(etype="vibes")])
        with self.assertRaises(pre_review.ToolError):
            self.run_check(pre_review.run_claims_coverage, **sections)


class TestCliExitCodes(Base):
    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(PRE_REVIEW), *args],
            capture_output=True, text=True, cwd=str(self.dir))

    def test_exit_2_on_missing_config(self):
        proc = self.cli("--config", "no-such-config.json",
                        "--report", "r.md")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("tool/config error", proc.stderr)

    def test_exit_0_clear_and_report_written(self):
        self.write("prose.py", "x = 1\n")
        self.write("the_oracle.py", "def f():\n    return 0\n")
        cfg = self.config(oracles=[{
            "name": "THE_ORACLE", "module_path": "the_oracle.py",
            "quantity_patterns": ["max\\(\\s*eta_opp"],
            "scan_files": ["prose.py"]}])
        proc = self.cli("--config", str(cfg), "--report", "r.md",
                        "--json", "r.json", "--only", "single-model")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = (self.dir / "r.md").read_text()
        self.assertIn("VERDICT: CLEAR", report)
        payload = json.loads((self.dir / "r.json").read_text())
        self.assertEqual(payload["verdict"], "CLEAR")

    def test_exit_1_block_and_banner(self):
        self.write("rogue.py", "d = max(eta_opp, cd)\n")
        self.write("the_oracle.py", "def f():\n    return 0\n")
        cfg = self.config(oracles=[{
            "name": "THE_ORACLE", "module_path": "the_oracle.py",
            "quantity_patterns": ["max\\(\\s*eta_opp"],
            "scan_files": ["rogue.py"]}])
        proc = self.cli("--config", str(cfg), "--report", "r.md",
                        "--only", "single-model")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("VERDICT: BLOCK", (self.dir / "r.md").read_text())

    def test_exit_2_on_missing_scan_file(self):
        self.write("the_oracle.py", "def f():\n    return 0\n")
        cfg = self.config(oracles=[{
            "name": "THE_ORACLE", "module_path": "the_oracle.py",
            "quantity_patterns": ["max\\(\\s*eta_opp"],
            "scan_files": ["missing.py"]}])
        proc = self.cli("--config", str(cfg), "--report", "r.md",
                        "--only", "single-model")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
