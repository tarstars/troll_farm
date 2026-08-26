#!/usr/bin/env python3
r"""Adjudication probe — OBSERVE the post-selection command rewrite instead of inferring it.

The decoder handoff named a candidate mechanism for the 120 intention/command divergences:
`select_recording` records the intention, and the command can be rewritten afterwards.  That was
named as a candidate, not asserted.  This probe tests it by observation: it prints the command
vector immediately after `select_recording` and again after `resolve_move_conflicts`, on the same
turn, from the source that PLAYED the corpus.

    IDLESEL  turn=<t> cmds=<a;b>     after select_recording, before conflict resolution
    IDLEPOST turn=<t> cmds=<a;b>     after resolve_move_conflicts

Two edits, both anchored exactly once, everything else byte-identical to the subject.  As with the
G-b probe, the parity gate in the driver -- the re-executed stream must equal the seat's recorded
stdout for the whole game -- is what makes the observation an observation.

Run:  python3 claude_1/narrate2/make_idle_probe.py [--out PATH]
"""
from __future__ import annotations

import argparse, hashlib, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SUBJECT = REPO / "claude_1" / "narrate1" / "instrument-swap-r1-narrate-v2.rs"
SUBJECT_SHA = "aaebc503cc2660e9"

OLD = """                let mut selected=MoisanBot::select_recording(by_id,&view.inventories[0],&mut narrate_chosen,);
                MoisanBot::resolve_move_conflicts(view,&mut selected);
"""
NEW = """                let mut selected=MoisanBot::select_recording(by_id,&view.inventories[0],&mut narrate_chosen,);
                eprintln!("IDLESEL turn={} cmds={}",view.turn,selected.join(";"));
                MoisanBot::resolve_move_conflicts(view,&mut selected);
                eprintln!("IDLEPOST turn={} cmds={}",view.turn,selected.join(";"));
"""


# The three sites in `resolve_move_conflicts_with_priority_and_forbidden` that can write over a
# selected command.  Tagging them makes the mechanism OBSERVED per row instead of argued from the
# source: `no-progress` is the projected-landing-equals-current-cell site, `blocked-no-detour` is
# the tail where the unit is boxed in, and `swap` is the branch that manufactures a MOVE for a
# partner whose own command was WAIT.
WAIT1_OLD = """                for(_,index,current,_,landing)in&projections{
                    if landing==current{
                        commands[*index]="WAIT".to_string();
                        }
                    }
"""
WAIT1_NEW = """                for(id,index,current,_,landing)in&projections{
                    if landing==current{
                        eprintln!("IDLEWAIT turn={} unit={} site=no-progress",view.turn,id);
                        commands[*index]="WAIT".to_string();
                        }
                    }
"""

WAIT2_OLD = """                    else{
                        "WAIT".to_string()
                    }
                    ;
"""
WAIT2_NEW = """                    else{
                        eprintln!("IDLEWAIT turn={} unit={} site=blocked-no-detour",view.turn,id);
                        "WAIT".to_string()
                    }
                    ;
"""

SWAP_OLD = """                            commands[u_index]=format!("MOVE {} {} {}",u_id,unit.cell.0,unit.cell.1);
"""
SWAP_NEW = """                            eprintln!("IDLEWAIT turn={} unit={} site=swap",view.turn,u_id);
                            commands[u_index]=format!("MOVE {} {} {}",u_id,unit.cell.0,unit.cell.1);
"""

EDITS = ((OLD, NEW), (WAIT1_OLD, WAIT1_NEW), (WAIT2_OLD, WAIT2_NEW), (SWAP_OLD, SWAP_NEW))


class ProbeError(RuntimeError):
    """Fail-closed refusal."""


def build() -> str:
    src = SUBJECT.read_text(encoding="utf-8")
    got = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()[:16]
    if got != SUBJECT_SHA:
        raise ProbeError("subject digest %s != pinned %s" % (got, SUBJECT_SHA))
    out = src
    for old, new in EDITS:
        if src.count(old) != 1:
            raise ProbeError("anchor %r matches %d times, expected exactly 1"
                             % (old.strip()[:50], src.count(old)))
        out = out.replace(old, new)
    check = out
    for old, new in EDITS:
        check = check.replace(new, old)
    if check != src:
        raise ProbeError("probe differs from the subject outside the declared edits")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(HERE / "probe-idle.rs"))
    args = ap.parse_args(argv)
    text = build()
    Path(args.out).write_text(text, encoding="utf-8")
    print("%s  sha256=%s" % (args.out, hashlib.sha256(text.encode()).hexdigest()[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
