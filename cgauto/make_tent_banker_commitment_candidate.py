#!/usr/bin/env python3
"""Build the productive tent-worker bank-commitment successor.

The exact active tent-proximity artifact assigns one productive worker in the one-or-two
adjacent-tree band. Once that worker receives wood, disappearance of the trigger currently
returns it to ordinary scoring, which can retarget the carrier before it reaches the
shack. This fail-closed transform persists that worker's bank intent until DROP succeeds
or its cargo is empty.

The non-banking planted-tree role, >2 full denial, global selector, scoring, and movement
conflict resolver are unchanged. No resident source file is edited.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.slim_live_source import _replace_item


REPO = Path(__file__).resolve().parent.parent
PARENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585578-owner-tent-proximity-denial-split-slim.min.rs"
)
PARENT_SHA256 = "3bd42d5b33dfb58724686ddfcca93205e953c0ac728595f520307798bb4fd900"
OUTPUT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6585739-owner-tent-banker-commitment-slim.min.rs"
)

STRUCT_TAIL = (
    "own_planted:BTreeSet<Cell>,nonbank_denial_units:BTreeSet<i32>,}"
)
STRUCT_TAIL_WITH_BANK = (
    "own_planted:BTreeSet<Cell>,nonbank_denial_units:BTreeSet<i32>,"
    "bank_commitment_units:BTreeSet<i32>,}"
)
INITIALIZER_TAIL = (
    "own_planted:BTreeSet::new(),nonbank_denial_units:BTreeSet::new(),}}"
)
INITIALIZER_TAIL_WITH_BANK = (
    "own_planted:BTreeSet::new(),nonbank_denial_units:BTreeSet::new(),"
    "bank_commitment_units:BTreeSet::new(),}}"
)

APPLY_TENT_DENIAL = (
    "fn apply_tent_denial(&mut self,view:&GameState,mut commands:Vec<String>)"
    "->Vec<String>{self.own_planted.retain(|cell|view.plant_at(*cell).is_some());"
    "let mut unit_ids:Vec<_>=view.units.iter().filter(|unit|unit.player==0)"
    ".map(|unit|unit.id).collect();unit_ids.sort_unstable();"
    "let workers:Vec<_>=unit_ids.iter().copied().filter(|id|view.unit(*id)"
    ".is_some_and(|unit|unit.stats.chop_power>0)).take(2).collect();"
    "let adjacent=Self::active_tent_adjacent(view);"
    "let prior_nonbank=self.nonbank_denial_units.clone();"
    "let prior_bank=self.bank_commitment_units.clone();"
    "let mut next_bank=BTreeSet::new();let mut forced_bank=BTreeSet::new();"
    "for id in workers.iter().copied(){let Some(unit)=view.unit(id)else{continue;};"
    "if prior_bank.contains(&id)&&unit.total_carried()>0{"
    "if let Some(action)=Self::banking_action(view,unit){Self::replace_action("
    "&mut commands,&unit_ids,id,action);next_bank.insert(id);"
    "forced_bank.insert(id);}}}"
    "if adjacent.is_empty(){self.nonbank_denial_units.clear();"
    "self.bank_commitment_units=next_bank;if!forced_bank.is_empty(){"
    "MoisanBot::resolve_move_conflicts(view,&mut commands);}"
    "self.remember_own_plant_commands(view,&commands,&unit_ids);return commands;}"
    "let mut next_nonbank=BTreeSet::new();let mut used=BTreeSet::new();"
    "if adjacent.len()>2{for id in workers.iter().copied()"
    ".filter(|id|!forced_bank.contains(id)){let Some(unit)=view.unit(id)else{continue;};"
    "if unit.total_carried()>0&&!prior_nonbank.contains(&id){"
    "if let Some(action)=Self::banking_action(view,unit){Self::replace_action("
    "&mut commands,&unit_ids,id,action);}continue;}"
    "let Some(target)=Self::best_denial_cell(view,unit,&adjacent,&used)else{continue;};"
    "used.insert(target);next_nonbank.insert(id);Self::replace_action("
    "&mut commands,&unit_ids,id,Self::tree_denial_action(unit,target));}}else{"
    "let banker=workers.iter().copied().filter(|id|!forced_bank.contains(id))"
    ".filter_map(|id|{let unit=view.unit(id)?;let target=Self::best_denial_cell("
    "view,unit,&adjacent,&BTreeSet::new())?;let distance=bfs_distances("
    "&view.walkable,&[unit.cell]);Some((distance[&target],id,target))}).min();"
    "let banker_id=banker.map(|(_,id,_)|id);if let Some((_,id,target))=banker{"
    "if let Some(unit)=view.unit(id){next_bank.insert(id);"
    "if let Some(action)=Self::banking_action(view,unit){Self::replace_action("
    "&mut commands,&unit_ids,id,action);}else{used.insert(target);"
    "Self::replace_action(&mut commands,&unit_ids,id,"
    "Self::tree_denial_action(unit,target));}}}"
    "let planted=self.opponent_planted_cells(view);for id in workers.iter().copied()"
    ".filter(|id|Some(*id)!=banker_id&&!forced_bank.contains(id)){"
    "let Some(unit)=view.unit(id)else{continue;};"
    "if unit.total_carried()>0&&!prior_nonbank.contains(&id){"
    "if let Some(action)=Self::banking_action(view,unit){Self::replace_action("
    "&mut commands,&unit_ids,id,action);}continue;}"
    "let Some(target)=Self::best_denial_cell(view,unit,&planted,&used)else{continue;};"
    "used.insert(target);next_nonbank.insert(id);Self::replace_action("
    "&mut commands,&unit_ids,id,Self::tree_denial_action(unit,target));break;}}"
    "self.bank_commitment_units=next_bank;self.nonbank_denial_units=next_nonbank;"
    "MoisanBot::resolve_move_conflicts(view,&mut commands);"
    "self.remember_own_plant_commands(view,&commands,&unit_ids);commands}"
)

PARENT_ANNOUNCEMENT = "yamo-tent-proximity-denial-split-rust"
CANDIDATE_ANNOUNCEMENT = "yamo-tent-banker-commitment-rust"


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one {label} anchor, found {count}")
    return text.replace(old, new, 1)


def make_candidate(parent: str) -> str:
    actual = digest_text(parent)
    if actual != PARENT_SHA256:
        raise ValueError(
            f"active parent hash changed: expected {PARENT_SHA256}, got {actual}"
        )
    result = replace_once(
        parent, STRUCT_TAIL, STRUCT_TAIL_WITH_BANK, "SecureOrchard struct tail"
    )
    result = replace_once(
        result,
        INITIALIZER_TAIL,
        INITIALIZER_TAIL_WITH_BANK,
        "SecureOrchard initializer tail",
    )
    result = _replace_item(result, "fn apply_tent_denial(", APPLY_TENT_DENIAL)
    return replace_once(
        result,
        PARENT_ANNOUNCEMENT,
        CANDIDATE_ANNOUNCEMENT,
        "announcement",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=PARENT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    candidate = make_candidate(args.parent.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate, encoding="utf-8")
    digest = digest_text(candidate)
    sidecar = args.output.with_name(args.output.name + ".sha256")
    sidecar.write_text(f"{digest}  {args.output.name}\n", encoding="utf-8")
    print(f"built {args.output}: {len(candidate.encode())} bytes")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
