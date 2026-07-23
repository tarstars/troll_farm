import json
import subprocess
from pathlib import Path

import torch

from cgauto.export_d11_actor import export_actor
from cgauto.generate_d11_live_actor_v7 import generate_live_source_v7
from cgauto.train_level1_ppo import SpatialActorCritic


def test_v7_adds_optional_actual_worker_adoption_and_compiles(tmp_path: Path) -> None:
    torch.manual_seed(71)
    checkpoint = tmp_path / "model.pt"
    torch.save({"model": SpatialActorCritic().state_dict()}, checkpoint)
    payload = tmp_path / "actor.bin"
    manifest = tmp_path / "manifest.json"
    export_actor(
        checkpoint,
        payload_path=payload,
        manifest_path=manifest,
        verification_checkpoint_path=tmp_path / "verification.pt",
    )
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    source, accounting = generate_live_source_v7(metadata, payload.read_bytes())

    assert accounting["under_100000_bytes"] is True
    assert "--adopt-worker" in source
    assert "if self.adopt" in source
    assert "self.target=[u.ms as i8,u.cc as i8,u.hp as i8,u.chop as i8]" in source
    assert (
        accounting["production_default_delta"]
        == "none when --adopt-worker and --fallback are absent"
    )

    source_path = tmp_path / "live-v7.rs"
    source_path.write_text(source, encoding="utf-8")
    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(source_path), "-o", str(tmp_path / "live-v7")],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
