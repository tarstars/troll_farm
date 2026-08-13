#!/usr/bin/env python3
"""Golden tests for the M3a D-1 extraction and its trusted toolchain."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXTRACTOR_PATH = REPO / "chatgpt_1/m3a_extract_from_panel.py"
VERIFIER_PATH = REPO / "chatgpt_1/m3a_verify_golden_set.py"
MANIFEST_PATH = REPO / "chatgpt_1/m3a-golden-set-manifest-v2-2026-08-09.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extractor = load_module(EXTRACTOR_PATH, "m3a_extractor_test")
verifier = load_module(VERIFIER_PATH, "m3a_verifier_test")


class TestM3aGoldenSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.panel_path = REPO / extractor.PANEL_PATH
        cls.panel = json.loads(cls.panel_path.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.artifacts = {row["role"]: row for row in cls.manifest["artifacts"]}

    def test_complete_bundle_verifies(self) -> None:
        result = verifier.verify_bundle(MANIFEST_PATH, REPO)
        self.assertEqual(result["bundle_status"], "VERIFIED")
        self.assertEqual(result["summary"]["episodes"], 34)
        self.assertEqual(result["summary"]["situations"], 32)

    def test_regeneration_is_byte_exact(self) -> None:
        library = extractor.build_library(self.panel)
        extractor.validate(library, self.panel)
        regenerated = verifier.canonical_json(library)
        golden = (REPO / self.artifacts["golden_output"]["path"]).read_text(
            encoding="utf-8"
        )
        self.assertEqual(regenerated, golden)

    def test_counting_rule_preserves_episode_multiplicity(self) -> None:
        library = extractor.build_library(self.panel)
        multi = {
            row["situation_id"]: len(row["episodes"])
            for row in library["situations"]
            if len(row["episodes"]) > 1
        }
        self.assertEqual(multi, {"m071-s1-a0": 2, "m090-s0-a2": 2})
        self.assertEqual(sum(len(row["episodes"]) for row in library["situations"]), 34)

    def test_delete_episode_fails_even_when_declared_count_is_repaired(self) -> None:
        panel = copy.deepcopy(self.panel)
        found = False
        for game in panel["games"]:
            for violation in game.get("violations", []):
                if violation.get("detector") == "D-1":
                    violation["episodes"].pop()
                    violation["count"] = len(violation["episodes"])
                    found = True
                    break
            if found:
                break
        self.assertTrue(found)
        library = extractor.build_library(panel)
        with self.assertRaises(extractor.ExtractionError):
            extractor.validate(library, panel)

    def test_duplicate_episode_fails_even_when_declared_count_is_repaired(self) -> None:
        panel = copy.deepcopy(self.panel)
        found = False
        for game in panel["games"]:
            for violation in game.get("violations", []):
                if violation.get("detector") == "D-1":
                    violation["episodes"].append(copy.deepcopy(violation["episodes"][0]))
                    violation["count"] = len(violation["episodes"])
                    found = True
                    break
            if found:
                break
        self.assertTrue(found)
        library = extractor.build_library(panel)
        with self.assertRaises(extractor.ExtractionError):
            extractor.validate(library, panel)

    def test_window_edit_fails_ledger_digest(self) -> None:
        panel = copy.deepcopy(self.panel)
        found = False
        for game in panel["games"]:
            for violation in game.get("violations", []):
                if violation.get("detector") == "D-1":
                    violation["episodes"][0]["turn_start"] += 1
                    found = True
                    break
            if found:
                break
        self.assertTrue(found)
        library = extractor.build_library(panel)
        with self.assertRaises(extractor.ExtractionError):
            extractor.validate(library, panel)

    def test_nond1_source_change_is_caught_by_exact_blob_guard(self) -> None:
        panel = copy.deepcopy(self.panel)
        panel["stats"]["wall_time_seconds"] = 123456.0
        # The semantic extraction is deliberately unchanged; provenance must still fail.
        library = extractor.build_library(panel)
        extractor.validate(library, panel)

        artifact = self.artifacts["source_panel"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / artifact["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(panel, indent=1) + "\n", encoding="utf-8")
            with self.assertRaises(verifier.GoldenSetError):
                verifier.verify_artifact(root, artifact)

    def test_golden_output_byte_change_is_rejected(self) -> None:
        artifact = self.artifacts["golden_output"]
        original = (REPO / artifact["path"]).read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / artifact["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(original + b" ")
            with self.assertRaises(verifier.GoldenSetError):
                verifier.verify_artifact(root, artifact)

    def test_manifest_distinguishes_data_from_toolchain(self) -> None:
        self.assertEqual(
            self.manifest["data_members"],
            ["chatgpt_1/m3a-d1-situation-library-2026-08-10.json"],
        )
        self.assertIn("chatgpt_1/m3a_extract_from_panel.py", self.manifest["toolchain_members"])
        self.assertIn("chatgpt_1/m3a_verify_golden_set.py", self.manifest["toolchain_members"])
        self.assertIn("chatgpt_1/test_m3a_golden_set.py", self.manifest["toolchain_members"])

    def test_review_gate_is_not_self_approval(self) -> None:
        reviewers = {
            row["reviewer"] for row in self.manifest["review_gate"]["required_reviewers"]
        }
        self.assertNotIn("chatgpt_1", reviewers)
        self.assertIn("local_claude_1", reviewers)
        self.assertTrue(self.manifest["review_gate"]["second_machine_execution_required"])


if __name__ == "__main__":
    unittest.main()
