#!/usr/bin/env python3
"""H-STARVE-1 pool #1 revision 2 — OBSERVED-FIRING controls for the two logging taps.

codex_1's pool-#2 blocker was not only "the taps are in the wrong place". It was:

> A direct-log gate that has never demonstrated those mutation paths is not yet evidence
> that the table attributes WAIT to the right generator stage.

Moving the taps is unfalsifiable on its own: if `force_unique_door_clear` and
`resolve_move_conflicts` never change anything on this corpus, the repaired records are
byte-identical to the broken ones and nobody can tell whether the fix did anything. So the
repaired instrument emits BOTH stages (`HS2PRE`/`HS2`, `HS2CHOSENPRE`/`HS2CHOSEN`) and this
control searches the corpus for turns where they DISAGREE:

- **door-clear control** — a turn where `force_unique_door_clear` replaced a unit's candidate
  list, so the pre-mutation record would have named a candidate set the selector never saw;
- **conflict control** — a turn where `resolve_move_conflicts` rewrote a command, so the
  pre-mutation record would have named a command the engine never received.

Each is reported with the exact situation, turn, and both texts. Fail-closed: if either path
never fires anywhere in the corpus, this exits non-zero and says so, rather than reporting a
green run that proves nothing.

**Negative control.** The comparator is also run PRE-against-PRE, where it must find ZERO
differences. Without that, a comparator with an off-by-one or a stray-field bug would report
"both paths observed firing" on any input at all — which is the same inert-check disease this
whole revision is about (see the viewer inference-marking check and the D-1 clause that read
the wrong keys, both of which passed for days while testing nothing).
"""
from __future__ import annotations

import collections
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "t1"))
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402

ROW_ANY = re.compile(r"HS2(PRE)? turn=(\d+) unit=(\d+) .*? ncand=(\d+) kinds=([^\n]*)")
CHOSEN_ANY = re.compile(r"HS2CHOSEN(PRE)? turn=(\d+) line=([^\n]*)")


def candidates_by_stage(err):
    """-> {turn: {unit: (ncand, kinds)}} for the pre stage and the final stage."""
    pre, final = {}, {}
    for m in ROW_ANY.finditer(err):
        bucket = pre if m.group(1) else final
        bucket.setdefault(int(m.group(2)), {})[int(m.group(3))] = (int(m.group(4)), m.group(5))
    return pre, final


def chosen_by_stage(err):
    """-> {turn: line} for the pre stage and the final stage."""
    pre, final = {}, {}
    for m in CHOSEN_ANY.finditer(err):
        (pre if m.group(1) else final)[int(m.group(2))] = m.group(3)
    return pre, final


def diff_candidates(pre, final):
    out = []
    for turn in sorted(set(pre) | set(final)):
        a, b = pre.get(turn, {}), final.get(turn, {})
        if a != b:
            for unit in sorted(set(a) | set(b)):
                if a.get(unit) != b.get(unit):
                    out.append((turn, unit, a.get(unit), b.get(unit)))
    return out


def diff_chosen(pre, final):
    return [(t, pre.get(t), final.get(t))
            for t in sorted(set(pre) | set(final)) if pre.get(t) != final.get(t)]


def verb_flips(pre_line, final_line):
    """Per-slot (verb_before, verb_after) pairs where the VERB changed, not just the target.

    This is the distinction the cause table turns on. `resolve_move_conflicts` rewriting
    `MOVE 0 2 2` to `MOVE 0 10 2` is the engine's order-vs-landing semantics and changes no
    attribution. Rewriting `MOVE ...` to `WAIT` MANUFACTURES a WAIT after the generator has
    already produced a real candidate — and a table built from the pre-mutation tap would
    attribute that WAIT to the generator stage, which never emitted it.
    """
    a = (pre_line or "").split(";")
    b = (final_line or "").split(";")
    out = []
    for i in range(max(len(a), len(b))):
        va = a[i].split()[0] if i < len(a) and a[i].split() else "?"
        vb = b[i].split()[0] if i < len(b) and b[i].split() else "?"
        if va != vb:
            out.append((va, vb))
    return out


def main():
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(only) if only else H.load_situations(None)

    door_hits, conflict_hits, per_sit = [], [], []
    with tempfile.TemporaryDirectory(prefix="hs2-taps-") as wd:
        di, dp = Path(wd) / "i", Path(wd) / "p"
        di.mkdir(); dp.mkdir()
        instr = H.compile_candidate(C.INSTR, di)
        plain = H.compile_candidate(H.RESIDENT, dp)
        for sit in sits:
            err = C.check_parity(sit, cfg, plain, instr)   # parity still gates every read
            cpre, cfin = candidates_by_stage(err)
            spre, sfin = chosen_by_stage(err)

            if not cpre or not spre:
                print(f"  FAIL {sit['id']}: no PRE records — this is not the repaired instrument")
                return 2

            d_cand = diff_candidates(cpre, cfin)
            d_chosen = diff_chosen(spre, sfin)

            # NEGATIVE CONTROL: the comparator against itself must find nothing.
            if diff_candidates(cpre, cpre) or diff_chosen(spre, spre):
                print(f"  FAIL {sit['id']}: comparator reports differences against ITSELF — "
                      f"it would report firing on any input, so its positives mean nothing")
                return 2

            door_hits += [(sit["id"], *d) for d in d_cand]
            conflict_hits += [(sit["id"], *d) for d in d_chosen]
            per_sit.append((sit["id"], len(d_cand), len(d_chosen)))
            print(f"  OK   {sit['id']}: parity IDENTICAL · door-clear rewrites {len(d_cand)} · "
                  f"conflict rewrites {len(d_chosen)}")

    print(f"\nnegative control: comparator vs itself found 0 differences on {len(sits)} situations")

    ok = True
    print("\n=== control 1: force_unique_door_clear CHANGES a candidate list ===")
    if door_hits:
        for sid, turn, unit, before, after in door_hits[:5]:
            print(f"  OBSERVED {sid} turn={turn} unit={unit}\n"
                  f"    before door clear: ncand={before[0]} kinds={before[1]}\n"
                  f"    selector actually saw: ncand={after[0]} kinds={after[1]}")
        print(f"  total: {len(door_hits)} unit-turns where the OLD tap recorded a candidate list "
              f"the selector never received")
    else:
        ok = False
        print("  NOT OBSERVED anywhere in the corpus — the repaired tap is unfalsified here.")

    print("\n=== control 2: resolve_move_conflicts CHANGES a command ===")
    if conflict_hits:
        for sid, turn, before, after in conflict_hits[:5]:
            print(f"  OBSERVED {sid} turn={turn}\n"
                  f"    select() returned: {before}\n"
                  f"    actually emitted:  {after}")
        print(f"  total: {len(conflict_hits)} turns where the OLD tap recorded a command "
              f"the engine never received")
        flips = collections.Counter()
        manufactured = []
        for sid, turn, before, after in conflict_hits:
            for va, vb in verb_flips(before, after):
                flips[(va, vb)] += 1
                if vb == "WAIT" and va != "WAIT":
                    manufactured.append((sid, turn, before, after))
        print("\n  verb changes caused by conflict resolution "
              "(target-only rewrites are order-vs-landing and change no attribution):")
        for (va, vb), n in sorted(flips.items(), key=lambda kv: -kv[1]):
            print(f"    {va:>8} -> {vb:<8} {n}")
        if manufactured:
            sid, turn, before, after = manufactured[0]
            print(f"\n  MANUFACTURED WAIT — {len(manufactured)} turns. Example {sid} turn={turn}:\n"
                  f"    select() returned: {before}\n"
                  f"    actually emitted:  {after}\n"
                  f"  A table built from the PRE tap would credit these WAITs to the generator, "
                  f"which never produced them.")
        else:
            print("\n  no MOVE->WAIT flips: every rewrite was target-only "
                  "(order-vs-landing), so no WAIT was manufactured downstream of the generator.")
    else:
        ok = False
        print("  NOT OBSERVED anywhere in the corpus — the repaired tap is unfalsified here.")

    out = HERE / "logging-taps-control-2026-08-17.json"
    out.write_text(json.dumps({
        "situations": len(sits),
        "per_situation": [{"id": s, "door_clear_rewrites": d, "conflict_rewrites": c}
                          for s, d, c in per_sit],
        "door_clear_observed": len(door_hits),
        "conflict_observed": len(conflict_hits),
        "door_clear_examples": [{"situation": s, "turn": t, "unit": u,
                                 "pre": {"ncand": b[0], "kinds": b[1]},
                                 "final": {"ncand": a[0], "kinds": a[1]}}
                                for s, t, u, b, a in door_hits[:20]],
        "conflict_examples": [{"situation": s, "turn": t, "pre": b, "final": a}
                              for s, t, b, a in conflict_hits[:20]],
        "conflict_verb_flips": {f"{a}->{b}": n for (a, b), n in sorted(
            collections.Counter(
                f for _, _, before, after in conflict_hits for f in verb_flips(before, after)
            ).items(), key=lambda kv: -kv[1])},
        "manufactured_waits": sum(
            1 for _, _, before, after in conflict_hits
            if any(vb == "WAIT" and va != "WAIT" for va, vb in verb_flips(before, after))),
        "negative_control": "comparator vs itself: 0 differences on every situation",
    }, indent=2) + "\n")
    print(f"\nwrote {out.relative_to(HERE.parent.parent)}")

    print("\nBOTH PATHS OBSERVED FIRING" if ok else "\nAT LEAST ONE PATH NEVER FIRED — fail-closed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
