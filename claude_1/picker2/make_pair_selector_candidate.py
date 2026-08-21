#!/usr/bin/env python3
r"""20260820-pair-selector-anti-benching Phase 2 — ONE patch generator, TWO subjects.

The owner ruled D1 (P1+P2) and D2 (dual-base). The card requires **one** generator applied to
both possible champions — cure-C `ad3bfefe…` and door-1 `547fa706…` — with the guarantee that
the generated diff is *identical* across bases. That guarantee is not asserted here; it is
measured (`--check`) and it is only credible because Phase-1 step 0 measured the three selection
regions byte-identical in both arms.

## The builder's guards (house pattern, fail-closed)

1. **Subject digest verified** against the allowlist before a byte is read for patching. An
   unknown subject is refused, not patched.
2. **Every edit is confined to the selection region.** The region spans are located by the same
   anchors step 0 used; after patching, the builder recomputes the byte span of every region and
   requires that *nothing outside the union of those spans changed*. A patch that reaches wider
   is refused, even if it compiles.
3. **Every anchor must occur exactly once.** Zero occurrences or two occurrences are both a hard
   error: a patch applied to the wrong copy of an ambiguous string is a silent wrong edit.
4. **The generated unified diff must be byte-identical across the two bases.** Checked in
   `--check`; a mismatch fails the build rather than producing two different candidates.

## What the patch does, precisely

- **P1** — inside the existing 2-unit pair loop, drop a pair in which one unit's command is a
  `MOVE` onto a cell whose occupant is our own other unit *which the same pair orders to `WAIT`*.
  Reads only the pair itself plus the units' own cells. It cannot empty the candidate set: the
  (`WAIT`,`WAIT`) pair is always compatible and is never a `MOVE`, so `best_pair` is still
  always `Some`.
- **P2** — on an *exact* tie (`score == best_score`), prefer the pair with fewer `WAIT`s. The
  incumbent behaviour is "first pair enumerated wins", which is `BTreeMap` key order — undesigned
  (Phase-1 finding 2, 810 turns).
- **Nothing else.** The >2-unit greedy fallback is deliberately untouched and is stated as such
  rather than quietly covered: the measured mechanism is entirely in the 2-unit pair arm.

`unit_cells` is a new `select()` input because the selector genuinely does not have positions
today. It is built at the existing call site from `my_units` (before that Vec is moved by the
assembly loop) and passed by reference; no other caller exists.

Run:
    python3 claude_1/picker2/make_pair_selector_candidate.py --check
"""
from __future__ import annotations

import argparse, difflib, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

BASES = {
    "cureC": {
        "src": REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
        "sha256": "ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1",
        "out": HERE / "candidate-cureC-p1p2.rs",
    },
    "door1": {
        "src": REPO / "claude_1/chop4c/candidate-door1.rs",
        "sha256": "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0",
        "out": HERE / "candidate-door1-p1p2.rs",
    },
}

# The same anchors step 0 used. The union of these spans is the ONLY region the patch may touch.
REGIONS = {
    "select_block": ("            fn wait()->Candidate{", "            fn move_command(command:&str)"),
    "assembly": ("                let mut by_id=BTreeMap::new();",
                 "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"),
}

HELPERS = '''            fn move_dest(command:&str)->Option<Cell>{
                let fields:Vec<_> =command.split_whitespace().collect();
                if fields.len()!=4||!fields[0].eq_ignore_ascii_case("MOVE"){
                    return None;
                    }
                match(fields[2].parse::<i32>(),fields[3].parse::<i32>()){
                    (Ok(x),Ok(y))=>Some((x,y)),_=>None,
                }
                }
            fn self_blocked(a_id:i32,a:&Candidate,b_id:i32,b:&Candidate,unit_cells:&BTreeMap<i32,Cell>,)->bool{
                let blocks=|waiter:i32,mover:&Candidate|match(unit_cells.get(&waiter),Self::move_dest(&mover.command)){
                    (Some(cell),Some(dest))=>*cell==dest,_=>false,
                }
                ;
                (a.command=="WAIT"&&blocks(a_id,b))||(b.command=="WAIT"&&blocks(b_id,a))
                }
            fn wait_count(a:&Candidate,b:&Candidate)->usize{
                (a.command=="WAIT")as usize+(b.command=="WAIT")as usize
                }
'''

PAIR_LOOP_OLD = '''                    let mut best_score=f64::NEG_INFINITY;
                    let mut best_pair=None;
                    for a in&candidates_by_id[&ids[0]]{
                        for b in&candidates_by_id[&ids[1]]{
                            if!Self::compatible(a.target,b.target)||!Self::stock_compatible(a,b,inventory){
                                continue;
                                }
                            let score=a.score+b.score;
                            if score>best_score{
                                best_score=score;
                                best_pair=Some((a.command.clone(),b.command.clone()));
                                }
                            }
                        }
'''

PAIR_LOOP_NEW = '''                    let mut best_score=f64::NEG_INFINITY;
                    let mut best_pair=None;
                    let mut best_waits=usize::MAX;
                    for a in&candidates_by_id[&ids[0]]{
                        for b in&candidates_by_id[&ids[1]]{
                            if!Self::compatible(a.target,b.target)||!Self::stock_compatible(a,b,inventory){
                                continue;
                                }
                            if Self::self_blocked(ids[0],a,ids[1],b,unit_cells){
                                continue;
                                }
                            let score=a.score+b.score;
                            let waits=Self::wait_count(a,b);
                            if score>best_score||(best_pair.is_some()&&score==best_score&&waits<best_waits){
                                best_score=score;
                                best_waits=waits;
                                best_pair=Some((a.command.clone(),b.command.clone()));
                                }
                            }
                        }
'''

EDITS = [
    ("P1/P2 helpers (move_dest, self_blocked, wait_count)",
     "            fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;",
     HELPERS + "            fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;"),
    ("select() takes the units' own cells",
     "            6],)->Vec<String>{",
     "            6],unit_cells:&BTreeMap<i32,Cell>,)->Vec<String>{"),
    ("P1 drop + P2 tie-break inside the 2-unit pair loop", PAIR_LOOP_OLD, PAIR_LOOP_NEW),
    ("build unit_cells at the existing call site (before my_units is moved)",
     "                let mut by_id=BTreeMap::new();\n                for unit in my_units{",
     "                let mut by_id=BTreeMap::new();\n"
     "                let unit_cells:BTreeMap<i32,Cell> =my_units.iter().map(|unit|(unit.id,unit.cell)).collect();\n"
     "                for unit in my_units{"),
    ("pass unit_cells at the call site",
     "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);",
     "let mut selected=MoisanBot::select(by_id,&view.inventories[0],&unit_cells);"),
]


class BuildError(Exception):
    """Anything that would make the candidate something other than what this file describes."""


def patched_anchor(anchor):
    """The same anchor as it reads AFTER patching, so the candidate's regions are locatable.

    Derived from the edit table rather than restated, so an anchor can never drift away from the
    edit that moved it.
    """
    for _, o, n in EDITS:
        if o in anchor:
            anchor = anchor.replace(o, n)
    return anchor


def spans(src, patched=False):
    out = {}
    for name, (a, b) in REGIONS.items():
        if patched:
            a, b = patched_anchor(a), patched_anchor(b)
        if src.count(a) != 1:
            raise BuildError(f"region anchor {name!r} start occurs {src.count(a)} times, not once")
        i = src.index(a)
        j = src.index(b, i)
        out[name] = (i, j + len(b))
    return out


def apply_edits(src):
    for label, old, new in EDITS:
        n = src.count(old)
        if n != 1:
            raise BuildError(f"edit {label!r}: anchor occurs {n} times, not exactly once")
        src = src.replace(old, new, 1)
    return src


def confined(base, cand):
    """Nothing outside the union of the selection regions may differ. Measured, not asserted."""
    bs, cs = spans(base), spans(cand, patched=True)
    # Outside-region text is the concatenation of the gaps between the regions, in order.
    def outside(text, sp):
        cuts = sorted(sp.values())
        parts, prev = [], 0
        for lo, hi in cuts:
            parts.append(text[prev:lo]); prev = hi
        parts.append(text[prev:])
        return parts
    ob, oc = outside(base, bs), outside(cand, cs)
    return ob == oc, [i for i, (x, y) in enumerate(zip(ob, oc)) if x != y]


def diff(base, cand, label):
    return "\n".join(difflib.unified_diff(base.splitlines(), cand.splitlines(),
                                          fromfile=f"{label}/base", tofile=f"{label}/p1p2",
                                          lineterm="", n=3))


def build(name, write=True):
    spec = BASES[name]
    src = spec["src"].read_text()
    got = hashlib.sha256(src.encode()).hexdigest()
    if got != spec["sha256"]:
        raise BuildError(f"{name}: subject digest {got[:16]}… != allowlisted {spec['sha256'][:16]}…")
    cand = apply_edits(src)
    ok, bad = confined(src, cand)
    if not ok:
        raise BuildError(f"{name}: patch reached OUTSIDE the selection regions (gap indices {bad})")
    d = diff(src, cand, name)
    if write:
        spec["out"].write_text(cand)
    return {"base": name, "base_sha256": got, "cand_sha256": hashlib.sha256(cand.encode()).hexdigest(),
            "out": str(spec["out"].relative_to(REPO)), "diff": d,
            "changed_lines": sum(1 for l in d.splitlines()
                                 if l[:1] in "+-" and l[:3] not in ("+++", "---"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="also assert the diff is base-independent")
    args = ap.parse_args()
    results = {n: build(n) for n in BASES}
    for n, r in results.items():
        print(f"  {n:6} base {r['base_sha256'][:16]}…  ->  candidate {r['cand_sha256'][:16]}…  "
              f"{r['changed_lines']} changed lines  {r['out']}")
    # Two independent statements of "same patch", because each alone is weaker than it looks.
    #
    # (a) The diff BODY — every -, + and context line, in order. The `@@` headers are dropped
    #     because they carry absolute line numbers, and the door-1 base is 8 lines shorter than
    #     cure-C by construction (the deleted `predicted_opp_chop` hunk). Dropping them is stated
    #     here rather than done quietly, and the offsets are printed below so nothing is hidden.
    # (b) The patched selection REGIONS themselves, byte for byte. Step 0 measured the three
    #     regions identical BEFORE the patch; if they are still identical AFTER it, the two
    #     candidates' selection code is the same code, which is the property the dual-base ruling
    #     actually depends on.
    def body(d):
        return "\n".join(l for l in d.splitlines()
                          if not l.startswith(("---", "+++", "@@")))

    def heads(d):
        return [l for l in d.splitlines() if l.startswith("@@")]

    a, b = (body(results[n]["diff"]) for n in ("cureC", "door1"))
    same_diff = a == b
    print(f"  generated diff body identical across bases: {'YES' if same_diff else 'NO'} "
          f"(sha256 {hashlib.sha256(a.encode()).hexdigest()[:16]}… vs "
          f"{hashlib.sha256(b.encode()).hexdigest()[:16]}…)")
    print(f"    hunk offsets (excluded from the comparison, shown not hidden): "
          f"cureC {heads(results['cureC']['diff'])} vs door1 {heads(results['door1']['diff'])}")

    same_region = True
    for name in REGIONS:
        texts = {}
        for n in BASES:
            cand = BASES[n]["out"].read_text()
            lo, hi = spans(cand, patched=True)[name]
            texts[n] = cand[lo:hi]
        ident = texts["cureC"] == texts["door1"]
        same_region &= ident
        print(f"    patched region {name:14} {'IDENTICAL' if ident else 'DIFFERS'}  "
              f"sha256={hashlib.sha256(texts['cureC'].encode()).hexdigest()[:16]} "
              f"bytes={len(texts['cureC'])}")

    (HERE / "p1p2.diff").write_text(a + "\n")
    manifest = {n: {k: v for k, v in r.items() if k != "diff"} for n, r in results.items()}
    manifest["_patch"] = {"diff_body_sha256": hashlib.sha256(a.encode()).hexdigest(),
                          "diff_body_identical_across_bases": same_diff,
                          "patched_regions_identical_across_bases": same_region,
                          "path": "claude_1/picker2/p1p2.diff"}
    (HERE / "build-manifest-2026-08-20.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    if args.check and not (same_diff and same_region):
        print("BUILD FAILED: one generator did not produce one patch")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
