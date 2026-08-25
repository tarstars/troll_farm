#!/usr/bin/env python3
"""PRINT-ONLY probes that answer the last link of the `m061` diagnosis.

On both `m061` seats the rule-off arm runs the champion's shack-side regeneration cycle from
turn ~100 (PICK a fruit beside the shack, PLANT it, CHOP it, DROP) and the instrument arm never
does, even though both arms have a fruit in the inventory and an own unit standing empty-handed
on a shack-adjacent cell. Rather than reason about which clause differs, print the clause's own
inputs at the point of decision:

  REGENBRANCH t u endgame committed early     -- which candidate generator ran for this unit
  REGEN      t u cell carried plants adj here_empty fruits safe turn_ok
                                              -- every input of the `main_candidates` PICK clause

Two probes are generated, one over each arm, so the same turn can be read on both. Print-only is
GATED by `m061_regen_probe.py`: each probe's stdout must be byte-identical to its own arm's.

    python3 claude_1/cure2/make_regen_probe.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

ARMS = {"instrument": HERE / "arm-instrument.rs", "ruleoff": HERE / "arm-ruleoff.rs"}

PICK_ANCHOR = ("                if safe_regeneration&&carried==0&&view.turn>=100"
               "&&view.plants.len()<=2&&view.units.iter().filter(|unit|unit.player==0).count()>=2"
               "&&is_adjacent(unit.cell,view.shacks[0])&&view.plant_at(unit.cell).is_none(){\n")
PICK_PRINT = ('                eprintln!("REGEN t={} u={} cell={},{} carried={} plants={} own={} '
              'adj={} here_empty={} fruits={} safe={} turn_ok={}",view.turn,unit.id,unit.cell.0,'
              'unit.cell.1,carried,view.plants.len(),view.units.iter().filter(|unit|unit.player==0)'
              '.count(),is_adjacent(unit.cell,view.shacks[0]) as i32,'
              'view.plant_at(unit.cell).is_none() as i32,Self::inventory_fruits(view).len(),'
              'safe_regeneration as i32,(view.turn>=100) as i32);\n')

BRANCH_ANCHOR = ("                    let committed_regeneration="
                 "self.regeneration_commitments.contains_key(&unit.id);\n")
BRANCH_PRINT = ('                    eprintln!("REGENBRANCH t={} u={} endgame={} committed={} '
                'early={}",view.turn,unit.id,endgame as i32,committed_regeneration as i32,'
                'early as i32);\n')


TRAIN_ANCHOR = ("                let train_now=!self.opening_abandoned"
                "&&MoisanBot::can_train(view,desired);\n")
TRAIN_PRINT = ('                eprintln!("TRAINNOW t={} train_now={} abandoned={}",view.turn,'
               'train_now as i32,self.opening_abandoned as i32);\n')

CANDS_ANCHOR = "                    by_id.insert(unit.id,candidates);\n"
CANDS_PRINT = ('                    eprintln!("CANDS t={} u={} n={} list={:?}",view.turn,unit.id,'
               'candidates.len(),candidates.iter().map(|c|(c.command.clone(),c.score))'
               '.collect::<Vec<_>>());\n')


def main() -> int:
    for name, src in ARMS.items():
        text = src.read_text()
        for anchor, printer, before in ((PICK_ANCHOR, PICK_PRINT, True),
                                        (BRANCH_ANCHOR, BRANCH_PRINT, False),
                                        (TRAIN_ANCHOR, TRAIN_PRINT, False),
                                        (CANDS_ANCHOR, CANDS_PRINT, True)):
            if text.count(anchor) != 1:
                print(f"{name}: anchor matched {text.count(anchor)} times, refusing:\n{anchor!r}",
                      file=sys.stderr)
                return 1
            text = text.replace(anchor, printer + anchor if before else anchor + printer)
        out = HERE / f"arm-{name}-regenprobe.rs"
        added = len(text.splitlines()) - len(src.read_text().splitlines())
        if added != 4:
            print(f"{name}: expected 4 added lines, got {added}", file=sys.stderr)
            return 1
        out.write_text(text)
        digest = hashlib.sha256(text.encode()).hexdigest()
        (HERE / f"{out.name}.sha256").write_text(f"{digest}  {out.name}\n")
        print(f"wrote {out.name}  +{added} lines  sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
