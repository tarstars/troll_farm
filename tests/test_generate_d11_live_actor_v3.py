import json
import subprocess
from pathlib import Path

import torch

from cgauto.export_d11_actor import export_actor
from cgauto.generate_d11_live_actor_v2 import generate_live_source_v2
from cgauto.generate_d11_live_actor_v3 import generate_live_source_v3
from cgauto.train_level1_ppo import SpatialActorCritic


def test_v3_has_only_frozen_own_chop_witness_changes_and_compiles(tmp_path: Path) -> None:
    torch.manual_seed(53)
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
    v2, _ = generate_live_source_v2(metadata, payload.read_bytes())
    v3, accounting = generate_live_source_v3(metadata, payload.read_bytes())

    restored = v3.replace(
        ",pending_chops:Vec<(usize,usize)>", ""
    ).replace(
        ",pending_chops:Vec::new()", ""
    ).replace(
        "let own_chop=self.created.is_some_and(|cell|self.pending_chops.contains(&cell));"
        "if self.created.is_some()&&!self.crop_exists(state)&&!own_chop{self.created=None;}self.pending_chops.clear();",
        "if self.created.is_some()&&!self.crop_exists(state){self.created=None;}",
    ).replace(
        "if plane==2&&self.created==Some((u.x,u.y)){self.pending_chops.push((u.x,u.y));}", ""
    )
    assert restored == v2
    assert accounting["under_100000_bytes"] is True
    assert "pending_chops" in v3

    source = tmp_path / "live-v3.rs"
    source.write_text(v3, encoding="utf-8")
    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(source), "-o", str(tmp_path / "live-v3")],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
