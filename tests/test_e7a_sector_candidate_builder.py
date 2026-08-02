from __future__ import annotations

import shutil
import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chatgpt_1 import e7a_sector_candidate_builder as builder
from chatgpt_1 import e7a_sector_candidate_pricing as pricing
from cgauto.e7_type_to_cut_audit import focus_geometry
from sim.mapgen import generate_bronze


class E7aSectorCandidateBuilderTests(unittest.TestCase):
    def test_parent_hash_anchor_and_inverse_are_exact(self) -> None:
        parent = builder.PARENT.read_bytes()
        self.assertEqual(builder.sha256_bytes(parent), builder.PARENT_SHA256)
        self.assertEqual(parent.count(builder.OLD_FOCUS.encode()), 1)
        candidate = builder.transform(parent)
        self.assertEqual(candidate.count(builder.NEW_FOCUS.encode()), 1)
        self.assertNotEqual(candidate, parent)
        self.assertEqual(
            candidate.replace(builder.NEW_FOCUS.encode(), builder.OLD_FOCUS.encode(), 1),
            parent,
        )

    def test_frozen_csv_sector_census_reproduces(self) -> None:
        census = builder.sector_census(builder.load_sector_rows())
        self.assertEqual(census["root_count"], 60)
        self.assertEqual(census["selected_count"], 13)
        self.assertEqual(census["selected_positive_count"], 10)
        self.assertEqual(census["selected_nonpositive_count"], 3)
        self.assertAlmostEqual(census["descriptive_precision"], 10 / 13)

    def test_rule_matches_exact_e7_geometry_for_all_roots(self) -> None:
        rows = {int(row["seed"]): row for row in builder.load_sector_rows()}
        selected = []
        for seed in range(60):
            game = generate_bronze(seed)
            seat0 = focus_geometry(game, 0)
            seat1 = focus_geometry(game, 1)
            self.assertEqual(seat0["chosen_species"], seat1["chosen_species"])
            lemon = seat0["distance_sums"]["LEMON"]
            plum = seat0["distance_sums"]["PLUM"]
            alternate_minus_default = abs(plum - lemon)
            row = rows[seed]
            self.assertEqual(row["default_species"], seat0["chosen_species"])
            self.assertEqual(
                int(float(row["delta_dist_sum"])), alternate_minus_default
            )
            in_sector = (
                seat0["chosen_species"] == "LEMON"
                and alternate_minus_default <= 8
            )
            self.assertEqual(builder.row_is_sector(row), in_sector)
            expected_candidate = "PLUM" if in_sector else seat0["chosen_species"]
            if in_sector:
                selected.append(seed)
            self.assertIn(expected_candidate, {"LEMON", "PLUM"})
        self.assertEqual(len(selected), 13)

    @unittest.skipUnless(shutil.which("rustc"), "rustc is unavailable")
    def test_generated_candidate_compiles_standalone(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e7a-sector-test-") as directory:
            temp = Path(directory)
            candidate = temp / "candidate.min.rs"
            manifest = temp / "manifest.json"
            result = builder.build(candidate, manifest, compile_source=True)
            self.assertTrue(candidate.exists())
            self.assertTrue(manifest.exists())
            self.assertEqual(result["verdict"], "MATERIALIZED_EXACT_SOURCE_TRANSFORM")
            self.assertEqual(result["sector"]["selected_count"], 13)
            self.assertIsNotNone(result["compilation"])

    def test_frozen_pricing_inputs_reproduce_the_locked_e7_anchors(self) -> None:
        sign_rows = pricing.load_sign_rows()
        rows = pricing.load_delta_rows(sign_rows)
        roots = pricing.root_rows(rows)
        self.assertEqual(len(rows), 360)
        self.assertEqual(len(roots), 60)
        self.assertAlmostEqual(
            pricing.mean(row["flip_delta_margin"] for row in rows),
            -12.17361111111111,
        )
        self.assertEqual(
            sum(root["flip_delta_margin"] > 0 for root in roots), 24
        )
        self.assertAlmostEqual(
            pricing.mean(max(0.0, root["flip_delta_margin"]) for root in roots),
            10.509722222222223,
        )
        selected = [root for root in roots if root["selected"]]
        self.assertEqual(len(selected), 13)
        self.assertEqual(sum(root["flip_delta_margin"] > 0 for root in selected), 10)
        self.assertAlmostEqual(
            pricing.mean(root["candidate_delta_margin"] for root in roots),
            4.008333333333333,
        )


if __name__ == "__main__":
    unittest.main()
