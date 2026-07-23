import json
import subprocess
from pathlib import Path

import torch

from cgauto.export_d11_actor import export_actor
from cgauto.generate_d11_live_actor_v6 import generate_live_source_v6
from cgauto.train_level1_ppo import SpatialActorCritic


def test_v6_adds_optional_target_fallback_and_compiles(tmp_path: Path) -> None:
    torch.manual_seed(67)
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
    source, accounting = generate_live_source_v6(metadata, payload.read_bytes())

    assert accounting["under_100000_bytes"] is True
    assert "--fallback" in source
    assert "fallback:Option<([i8;4],usize)>" in source
    assert "if state.turn>=turn" in source
    assert accounting["production_default_delta"] == "none when --fallback is absent"

    source_path = tmp_path / "live-v6.rs"
    source_path.write_text(source, encoding="utf-8")
    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(source_path), "-o", str(tmp_path / "live-v6")],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
