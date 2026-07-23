import json
import subprocess
from pathlib import Path

import torch

from cgauto.export_d11_actor import export_actor
from cgauto.generate_d11_live_actor_v4 import generate_live_source_v4
from cgauto.generate_d11_live_actor_v5 import NEW_PHASE, OLD_PHASE, generate_live_source_v5
from cgauto.train_level1_ppo import SpatialActorCritic


def test_v5_has_only_frozen_persistent_buffer_changes_and_compiles(tmp_path: Path) -> None:
    torch.manual_seed(61)
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
    v4, _ = generate_live_source_v4(metadata, payload.read_bytes())
    v5, accounting = generate_live_source_v5(metadata, payload.read_bytes())

    restored = v5.replace(
        ",obs:Vec<u8>,mask:Vec<u8>,logits:Vec<f32>", ""
    ).replace(
        ",obs:vec![0u8;OBS_C*AREA],mask:vec![0u8;ACTIONS],logits:vec![0.0f32;ACTIONS]", ""
    ).replace(NEW_PHASE, OLD_PHASE)
    assert restored == v4
    assert accounting["under_100000_bytes"] is True
    assert "std::mem::take(&mut self.obs)" in v5
    assert "let mut obs=vec!" not in v5

    source = tmp_path / "live-v5.rs"
    source.write_text(v5, encoding="utf-8")
    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(source), "-o", str(tmp_path / "live-v5")],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
