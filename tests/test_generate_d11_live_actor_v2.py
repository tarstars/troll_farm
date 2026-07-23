import json
import subprocess
from pathlib import Path

import torch

from cgauto.export_d11_actor import export_actor
from cgauto.generate_d11_live_actor import generate_live_source
from cgauto.generate_d11_live_actor_v2 import generate_live_source_v2
from cgauto.train_level1_ppo import SpatialActorCritic


def test_v2_has_only_frozen_tracker_replacements_and_compiles(tmp_path: Path) -> None:
    torch.manual_seed(47)
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
    v1, _ = generate_live_source(metadata, payload.read_bytes())
    v2, accounting = generate_live_source_v2(metadata, payload.read_bytes())

    restored = v2.replace(
        "pending_harvests:Vec<(i32,i32,(usize,usize))>",
        "pending_harvests:Vec<(i32,i32)>",
    ).replace(
        "for (id,before,cell) in self.pending_harvests.drain(..){if self.created==Some(cell)&&state.unit(id).is_some_and(|u|u.carry[3]>before){self.renewable=self.renewable.saturating_add(1);}}",
        "for (id,before) in self.pending_harvests.drain(..){if state.unit(id).is_some_and(|u|u.carry[3]>before){self.renewable=self.renewable.saturating_add(1);}}",
    ).replace(
        "self.pending_harvests.push((u.id,u.carry[3],(u.x,u.y)));",
        "self.pending_harvests.push((u.id,u.carry[3]));",
    )
    assert restored == v1
    assert accounting["under_100000_bytes"] is True
    assert "self.created==Some(cell)" in v2

    source = tmp_path / "live-v2.rs"
    source.write_text(v2, encoding="utf-8")
    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(source), "-o", str(tmp_path / "live-v2")],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
