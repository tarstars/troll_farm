#!/usr/bin/env python3
"""Add behavior-neutral wood-conversion telemetry to the exact live Yamo artifact."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


REPLACEMENTS = (
    (
        "fn commands(&mut self,view:&GameState)->Vec<String>{"
        "self.reconcile_regeneration_commitments(view);",
        "fn commands(&mut self,view:&GameState)->Vec<String>{"
        "for unit in view.units.iter().filter(|unit|unit.player==0){"
        'eprintln!("@WC_STATE t={} u={} x={} y={} cw={} free={} iw={}",'
        "view.turn,unit.id,unit.cell.0,unit.cell.1,unit.carry[WOOD],"
        "unit.free_capacity(),view.inventories[0][WOOD]);}"
        "self.reconcile_regeneration_commitments(view);",
    ),
    (
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
        "self.remember_selected_regeneration(&selected);",
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
        "for command in &selected{"
        "let Some(cell)=tree_targets.get(command)else{continue;};"
        "let Some(id)=command.split_whitespace().nth(1)"
        ".and_then(|value|value.parse::<i32>().ok())else{continue;};"
        "let(Some(unit),Some(index))=(view.unit(id),view.plant_at(*cell))else{continue;};"
        "let plant=&view.plants[index];"
        "let op=command.split_whitespace().next().unwrap_or(\"?\");"
        'eprintln!("@WC_SELECT t={} u={} op={} kind={} x={} y={} size={} health={} '
        'fruits={} chop={} free={}",view.turn,id,op,plant.kind.as_str(),cell.0,cell.1,'
        "plant.size,plant.health,plant.fruits,unit.stats.chop_power,unit.free_capacity());}"
        "self.remember_selected_regeneration(&selected);",
    ),
    (
        "Self::replace_action(&mut commands,&unit_ids,starter_id,forced);",
        'eprintln!("@WC_OVERRIDE t={} u={} op={}",view.turn,starter_id,'
        'forced.split_whitespace().next().unwrap_or("?"));'
        "Self::replace_action(&mut commands,&unit_ids,starter_id,forced);",
    ),
)


def instrument_minified(source: str) -> str:
    result = source
    for before, after in REPLACEMENTS:
        count = result.count(before)
        if count != 1:
            raise RuntimeError(
                f"expected one wood-probe anchor, found {count}: {before[:90]!r}"
            )
        result = result.replace(before, after, 1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    result = instrument_minified(args.source.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    digest = hashlib.sha256(result.encode()).hexdigest()
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{digest}  {args.output.name}\n"
    )
    print(f"instrumented {args.source} -> {args.output} ({len(result.encode())} bytes)")
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()
