"""The mutation runner must not report an incomplete experiment as a success.

`chatgpt_1`'s bite-test audit r2 (`20260812T003000Z`, blocker 4) found that
`run_mutations.py` returned `0` whenever the unmutated control was green,
regardless of how much of the experiment actually ran.  The evidence was already
in the results file — `patch_failed`, `compile_failed`, `mutants_run` versus
`manifest_entries` — and nothing consulted it.  A run in which sixty of
sixty-four mutants never patched was, to anything gating on exit status,
indistinguishable from a clean sweep.

These tests are the guard for the repair, and they are written to *fail on the
pre-repair runner*: each one drives `main()` end to end over a synthetic
manifest and asserts on the exit status, not on prose.

Run:  python3 -m unittest test_run_mutations_completeness
"""
from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

import run_mutations as rm

HERE = os.path.dirname(os.path.abspath(__file__))
REAL_MANIFEST = os.path.join(HERE, "mutation_manifest.json")


def _real() -> dict:
    with open(REAL_MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def _one_mutant_manifest(corrupt: bool = False) -> dict:
    """A whole manifest containing exactly one real mutant.

    Because it is the *whole* manifest, running it is a complete experiment —
    which is what lets these tests separate "incomplete" from "small".
    """
    src = _real()
    mutant = copy.deepcopy(next(m for m in src["mutants"]
                                if not m.get("excluded_from_totals")))
    if corrupt:
        # A preimage that does not occur: apply_patch returns None and the row
        # becomes PATCH_FAILED.  Nothing else about the run changes, so the
        # exit status is the only variable.
        mutant["preimage"] = "this string does not occur in the source at all"
    return {"pinned_sources": src["pinned_sources"], "mutants": [mutant]}


class RunnerCompleteness(unittest.TestCase):
    maxDiff = None

    def _run(self, manifest: dict, *extra: str):
        tmp = tempfile.mkdtemp(prefix="bitetest-completeness-")
        self.addCleanup(__import__("shutil").rmtree, tmp, ignore_errors=True)
        man_path = os.path.join(tmp, "manifest.json")
        out_path = os.path.join(tmp, "results.json")
        with open(man_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh)
        code = rm.main(["--manifest", man_path, "--out", out_path,
                        "--workroot", os.path.join(tmp, "work"), *extra])
        with open(out_path, encoding="utf-8") as fh:
            doc = json.load(fh)
        return code, doc

    def test_a_whole_manifest_that_runs_clean_exits_zero(self):
        """Control: without this the tests below could pass vacuously, by the
        runner simply refusing everything."""
        code, doc = self._run(_one_mutant_manifest())
        self.assertEqual(code, 0, "a complete, green experiment must exit 0")
        self.assertTrue(doc["completeness"]["complete"])
        self.assertEqual(doc["completeness"]["reasons"], [])

    def test_a_patch_that_never_applied_is_not_a_success(self):
        """The headline case: control green, experiment broken."""
        code, doc = self._run(_one_mutant_manifest(corrupt=True))
        self.assertTrue(doc["control"]["green"],
                        "precondition: the control must still be green, so "
                        "exit status is the only thing under test")
        self.assertEqual(doc["completeness"]["patch_failed"], 1)
        self.assertFalse(doc["completeness"]["complete"])
        self.assertEqual(code, 2,
                         "a green control over a mutant that never patched "
                         "must not exit 0 — that is the defect being closed")

    def test_a_subset_run_is_not_a_whole_manifest_result(self):
        src = _real()
        code, doc = self._run(src, "--only", src["mutants"][0]["id"])
        self.assertEqual(code, 2)
        self.assertTrue(doc["completeness"]["subset_run"])
        self.assertIn("selected", " ".join(doc["completeness"]["reasons"]))

    def test_a_subset_may_be_acknowledged_but_is_recorded_as_partial(self):
        """`--only` stays usable.  What it may not do is look whole."""
        src = _real()
        code, doc = self._run(src, "--only", src["mutants"][0]["id"], "--partial")
        self.assertEqual(code, 0, "an acknowledged subset is a legitimate run")
        self.assertFalse(doc["completeness"]["complete"],
                         "acknowledging a subset does not make it complete")
        self.assertTrue(doc["completeness"]["acknowledged_partial"])

    def test_the_results_file_always_states_completeness(self):
        """A reader of the JSON must not have to infer this from totals."""
        for corrupt in (False, True):
            with self.subTest(corrupt=corrupt):
                _, doc = self._run(_one_mutant_manifest(corrupt=corrupt))
                self.assertIn("completeness", doc)
                self.assertEqual(doc["schema"], "detector-mutation-results/3")
                for key in ("complete", "manifest_entries", "attempted",
                            "patch_failed", "compile_failed", "probe_error",
                            "drift_overridden", "reasons"):
                    self.assertIn(key, doc["completeness"])


if __name__ == "__main__":
    unittest.main()
