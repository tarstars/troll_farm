#!/usr/bin/env python3
"""Executable tests for the sealed-holdout lifecycle."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("seal.py").resolve()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SealLifecycleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="sealed-holdout-test-")
        self.base = Path(self.temporary.name)
        self.repo = self.base / "repo"
        self.root = self.repo / "instrument"
        self.keys = self.base / "coordinator-private"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "seal-test@example.invalid"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Seal Test"], cwd=self.repo, check=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_seal(self, *arguments: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=self.repo,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, expect, completed.stderr)
        return completed

    def init(self, maps: int = 8) -> None:
        self.run_seal(
            "init",
            "--root",
            str(self.root),
            "--key-dir",
            str(self.keys),
            "--seed-start",
            "4000000000",
            "--seed-stop-exclusive",
            "4000100000",
            "--maps",
            str(maps),
            "--generator-path",
            "rust/src/game/official_mapgen.rs",
            "--generator-ref",
            "test",
            "--generator-commit",
            "0" * 40,
            "--generator-sha256",
            "1" * 64,
        )

    def write_gate(self, seal_id: str) -> tuple[Path, str]:
        baseline = self.repo / "baseline.rs"
        candidate = self.repo / "candidate.rs"
        opponents = self.repo / "opponents.json"
        baseline.write_text("fn main() { println!(\"baseline\"); }\n")
        candidate.write_text("fn main() { println!(\"candidate\"); }\n")
        opponents.write_text(
            json.dumps(
                {
                    "opponents": [
                        {"name": name, "agent_id": agent_id}
                        for name, agent_id in (
                            ("delineate", 6479768),
                            ("wala", 6481141),
                            ("escdemon", 6483545),
                            ("norxondor", 6480540),
                            ("laconic", 6482055),
                        )
                    ]
                },
                sort_keys=True,
            )
            + "\n"
        )
        gate = self.repo / "gate.json"
        self.run_seal(
            "prepare-gate",
            "--root",
            str(self.root),
            "--baseline",
            str(baseline),
            "--candidate",
            str(candidate),
            "--external-opponents",
            str(opponents),
            "--decision-rule",
            "paired mean score delta lower 95% bound > 0",
            "--output",
            str(gate),
        )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", f"freeze gate for {seal_id}"], cwd=self.repo, check=True)
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        return gate, commit

    def test_one_read_rotation_rollback_and_tamper_guards(self) -> None:
        self.init()
        initial_state_bytes = (self.root / "seal-state.json").read_bytes()
        self.run_seal("verify", "--root", str(self.root), "--key-dir", str(self.keys))
        for seal_id in ("holdout-001", "holdout-002"):
            manifest_text = (self.root / "sealed" / f"{seal_id}.manifest.json").read_text()
            self.assertNotIn('"seeds"', manifest_text)
            key = self.keys / f"{seal_id}.key"
            self.assertEqual(stat.S_IMODE(key.stat().st_mode), 0o600)
        self.assertFalse(any("payload" in path.name for path in self.keys.iterdir()))

        gate, commit = self.write_gate("holdout-001")
        reveal = self.repo / "retired" / "holdout-001-seed-bank.json"
        self.run_seal(
            "open",
            "--root",
            str(self.root),
            "--key-dir",
            str(self.keys),
            "--gate-manifest",
            str(gate),
            "--gate-commit",
            commit,
            "--reveal-path",
            str(reveal),
        )
        bank = json.loads(reveal.read_text())
        self.assertEqual(bank["map_count"], 8)
        self.assertEqual(len(bank["blocks"]), 8)
        self.assertEqual(
            [row["opponent_agent"] for row in bank["blocks"][:6]],
            [6479768, 6481141, 6483545, 6480540, 6482055, 6479768],
        )
        self.assertEqual(len({row["seed"] for row in bank["blocks"]}), 8)
        state_path = self.root / "seal-state.json"
        post_open_state_bytes = state_path.read_bytes()
        state = json.loads(post_open_state_bytes)
        self.assertEqual(state["active_seal_id"], "holdout-002")
        self.assertIsNone(state["standby_seal_id"])
        self.assertEqual(state["retired_seal_ids"], ["holdout-001"])
        self.assertTrue((self.keys / ".opened-holdout-001.lock").exists())

        # A Git/worktree rollback cannot make the private audit state agree again.
        state_path.write_bytes(initial_state_bytes)
        self.run_seal(
            "verify", "--root", str(self.root), "--key-dir", str(self.keys), expect=2
        )
        state_path.write_bytes(post_open_state_bytes)

        # The newly active holdout cannot be opened until another sealed successor exists.
        self.run_seal(
            "open",
            "--root",
            str(self.root),
            "--key-dir",
            str(self.keys),
            "--gate-manifest",
            str(gate),
            "--gate-commit",
            commit,
            "--reveal-path",
            str(self.repo / "forbidden.json"),
            expect=2,
        )
        self.run_seal("add-standby", "--root", str(self.root), "--key-dir", str(self.keys))
        state = json.loads(state_path.read_text())
        self.assertEqual(state["standby_seal_id"], "holdout-003")

        cipher = self.root / "sealed" / "holdout-003.enc"
        content = bytearray(cipher.read_bytes())
        content[-1] ^= 1
        cipher.write_bytes(content)
        self.run_seal(
            "verify", "--root", str(self.root), "--key-dir", str(self.keys), expect=2
        )


if __name__ == "__main__":
    unittest.main()
