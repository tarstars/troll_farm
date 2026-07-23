#!/usr/bin/env python3
"""Generate a behavior-neutral stderr probe from the formatted live Yamo source.

The probe reports three distinct events:

* ``@IH_CAND``: the inner idle-harvest gate produced at least one candidate;
* ``@IH_SELECT``: one of those candidates won the inner assignment;
* ``@IH_ORCHARD_FORCE``: the outer orchard wrapper independently forced a harvest.

Only ``eprintln!`` calls and local bookkeeping are added. Standard output, which is the command
stream consumed by the game, is unchanged and must be parity-checked after generation.
"""

from __future__ import annotations

import argparse
from pathlib import Path


INSERT_PROBE_MAP = (
    "                let mut by_id = BTreeMap::new();\n"
    "                for unit in my_units {",
    "                let mut by_id = BTreeMap::new();\n"
    "                let mut idle_harvest_probe: BTreeMap<i32, Vec<String>> = BTreeMap::new();\n"
    "                for unit in my_units {",
)

INSTRUMENT_CANDIDATES = (
    """                        candidates.extend(Self::idle_harvest_candidates(
                            view,
                            unit,
                            protected_tree,
                        ));""",
    """                        let idle_candidates =
                            Self::idle_harvest_candidates(view, unit, protected_tree);
                        if !idle_candidates.is_empty() {
                            let commands: Vec<String> = idle_candidates
                                .iter()
                                .map(|candidate| candidate.command.clone())
                                .collect();
                            eprintln!(
                                "@IH_CAND t={} unit={} commands={}",
                                view.turn,
                                unit.id,
                                commands.join("|")
                            );
                            idle_harvest_probe.insert(unit.id, commands);
                        }
                        candidates.extend(idle_candidates);""",
)

INSTRUMENT_SELECTION = (
    """                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);""",
    """                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);
                for (unit_id, probe_commands) in &idle_harvest_probe {
                    if let Some(command) = selected
                        .iter()
                        .find(|command| probe_commands.contains(command))
                    {
                        eprintln!(
                            "@IH_SELECT t={} unit={} command={}",
                            view.turn, unit_id, command
                        );
                    }
                }""",
)

INSTRUMENT_ORCHARD = (
    """                };
                Self::replace_action(&mut commands, &unit_ids, starter_id, forced);""",
    """                };
                if forced.starts_with("HARVEST ") {
                    eprintln!(
                        "@IH_ORCHARD_FORCE t={} unit={} command={}",
                        view.turn, starter_id, forced
                    );
                }
                Self::replace_action(&mut commands, &unit_ids, starter_id, forced);""",
)

REPLACEMENTS = [INSERT_PROBE_MAP, INSTRUMENT_CANDIDATES, INSTRUMENT_SELECTION, INSTRUMENT_ORCHARD]

MINIFIED_REPLACEMENTS = [
    (
        "let mut by_id=BTreeMap::new();for unit in my_units{",
        "let mut by_id=BTreeMap::new();"
        "let mut idle_harvest_probe:BTreeMap<i32,Vec<String>>=BTreeMap::new();"
        "for unit in my_units{",
    ),
    (
        "candidates.extend(Self::idle_harvest_candidates(view,unit,protected_tree));",
        "let idle_candidates=Self::idle_harvest_candidates(view,unit,protected_tree);"
        "if!idle_candidates.is_empty(){"
        "let commands:Vec<String>=idle_candidates.iter()"
        ".map(|candidate|candidate.command.clone()).collect();"
        'eprintln!("@IH_CAND t={} unit={} commands={}",view.turn,unit.id,commands.join("|"));'
        "idle_harvest_probe.insert(unit.id,commands);"
        "}candidates.extend(idle_candidates);",
    ),
    (
        "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);",
        "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"
        "for(unit_id,probe_commands)in &idle_harvest_probe{"
        "if let Some(command)=selected.iter()"
        ".find(|command|probe_commands.contains(command)){"
        'eprintln!("@IH_SELECT t={} unit={} command={}",view.turn,unit_id,command);'
        "}}",
    ),
    (
        "Self::replace_action(&mut commands,&unit_ids,starter_id,forced);",
        'if forced.starts_with("HARVEST "){'
        'eprintln!("@IH_ORCHARD_FORCE t={} unit={} command={}",'
        "view.turn,starter_id,forced);"
        "}Self::replace_action(&mut commands,&unit_ids,starter_id,forced);",
    ),
]


def instrument(source: str) -> str:
    result = source
    for before, after in REPLACEMENTS:
        count = result.count(before)
        if count != 1:
            raise RuntimeError(f"expected one instrumentation anchor, found {count}: {before[:80]!r}")
        result = result.replace(before, after, 1)
    return result


def instrument_minified(source: str) -> str:
    result = source
    for before, after in MINIFIED_REPLACEMENTS:
        count = result.count(before)
        if count != 1:
            raise RuntimeError(
                f"expected one minified instrumentation anchor, found {count}: {before[:80]!r}"
            )
        result = result.replace(before, after, 1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--minified",
        action="store_true",
        help="use whitespace-free anchors for the exact recovered artifact",
    )
    args = parser.parse_args()

    transform = instrument_minified if args.minified else instrument
    result = transform(args.source.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    print(f"instrumented {args.source} -> {args.output} ({len(result)} bytes)")


if __name__ == "__main__":
    main()
