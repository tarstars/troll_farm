import json
import subprocess
from pathlib import Path

import torch

from cgauto.export_d11_actor import export_actor
from cgauto.generate_d11_live_actor_v3 import generate_live_source_v3
from cgauto.generate_d11_live_actor_v4 import generate_live_source_v4
from cgauto.train_level1_ppo import SpatialActorCritic


def test_v4_has_only_frozen_persistent_provenance_changes_and_compiles(tmp_path: Path) -> None:
    torch.manual_seed(59)
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
    v3, _ = generate_live_source_v3(metadata, payload.read_bytes())
    v4, accounting = generate_live_source_v4(metadata, payload.read_bytes())

    restored = v4.replace(
        ",own_removed_crop:bool", ""
    ).replace(
        ",own_removed_crop:false", ""
    ).replace(
        "let crop_exists=self.crop_exists(state);let own_chop=self.created.is_some_and(|cell|self.pending_chops.contains(&cell));"
        "if crop_exists{self.own_removed_crop=false;}else if own_chop{self.own_removed_crop=true;}"
        "else if self.created.is_some()&&!self.own_removed_crop{self.created=None;}self.pending_chops.clear();",
        "let own_chop=self.created.is_some_and(|cell|self.pending_chops.contains(&cell));"
        "if self.created.is_some()&&!self.crop_exists(state)&&!own_chop{self.created=None;}self.pending_chops.clear();",
    ).replace(
        "self.created=Some((x,y));self.own_removed_crop=false;",
        "self.created=Some((x,y));",
    )
    assert restored == v3
    assert accounting["under_100000_bytes"] is True
    assert "own_removed_crop" in v4

    source = tmp_path / "live-v4.rs"
    source.write_text(v4, encoding="utf-8")
    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(source), "-o", str(tmp_path / "live-v4")],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
