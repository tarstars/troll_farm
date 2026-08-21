#!/usr/bin/env python3
"""Phase-2 de-novo decomposition: door-1 candidate against the cure-C matched floor.

Card 1 requires the decomposition keyed EXACTLY `(map_id, seat)`, with both directions
exercised. Aggregate blocking counts are deliberately NOT the verdict here: cure C taught that
lesson expensively — its aggregate improved (blocking 119->58) while the gate, which is per-game
de-novo, failed. So this tool reports the aggregate only as context and decides on the keyed sets.

The matched-corpus check is a GATE, not a formality. If the two arms did not face the same map,
seat, seed and opponent command stream, then "de-novo" is measuring the corpus, not the bot. Every
mismatch class fails closed rather than being reported as a difference.
"""
import json, sys, collections
from pathlib import Path

DETECTORS = [f"D-{i}" for i in range(1, 10)]


class GateError(RuntimeError):
    """Fail closed."""


def load(path):
    d = json.loads(Path(path).read_text())
    rows = {}
    for g in d["games"]:
        key = (g["map_id"], g["seat"])
        if key in rows:
            raise GateError(f"{path}: duplicate key {key} — (map_id, seat) is not unique")
        rows[key] = g
    return d, rows


def matched_corpus_gate(cand, floor):
    """Both arms must have faced the identical corpus. Any divergence invalidates the join.

    The subtlety, found by this gate firing on its first run: `opponent_commands_sha256` is an
    OUTCOME, not a corpus input. The opponent reacts to the world, so a candidate that plays
    differently necessarily produces a different opponent stream — here on 39 of 240 games. Gating
    on it would reject every real difference as a corpus fault.

    The stream that MUST match is the floor bot's own. Cure-C plays the parent side of the
    candidate arm and both sides of the floor arm, so
    `cand.parent_opponent_commands_sha256 == floor.opponent_commands_sha256` on every key proves
    two things at once: the corpus (map, seat, seed, opponent policy) really is identical, and the
    floor bot is deterministic across runs. That is a parity assertion, not a formality.
    """
    ck, fk = set(cand), set(floor)
    if ck != fk:
        raise GateError(f"key sets differ: {len(ck - fk)} candidate-only, {len(fk - ck)} floor-only")
    diverged = 0
    for k in sorted(ck):
        c, f = cand[k], floor[k]
        for field in ("seed", "class", "profile", "turns"):
            if c[field] != f[field]:
                raise GateError(f"{k}: {field} differs between arms ({c[field]!r} vs {f[field]!r}) "
                                f"— the arms are not matched and the comparison is void")
        if c["parent_opponent_commands_sha256"] != f["opponent_commands_sha256"]:
            raise GateError(f"{k}: the floor bot's own opponent stream differs between arms "
                            f"— corpus not matched, or the floor bot is non-deterministic")
        if f["opponent_commands_sha256"] != f["parent_opponent_commands_sha256"]:
            raise GateError(f"{k}: floor arm's two sides disagree — a self-judged floor must not")
        if c["opponent_commands_sha256"] != c["parent_opponent_commands_sha256"]:
            diverged += 1
    return len(ck), diverged


def decompose(cand, floor):
    out = {"de_novo": [], "healed": [], "both": [], "neither": []}
    for k in sorted(cand):
        cb, fb = bool(cand[k]["block"]), bool(floor[k]["block"])
        bucket = ("de_novo" if cb and not fb else
                  "healed" if fb and not cb else
                  "both" if cb and fb else "neither")
        if bucket != "neither":
            out[bucket].append({
                "map_id": k[0], "seat": k[1], "class": cand[k]["class"],
                "profile": cand[k]["profile"], "seed": cand[k]["seed"],
                "candidate_detectors": {d: n for d, n in cand[k]["detector_counts"].items() if n},
                "floor_detectors": {d: n for d, n in floor[k]["detector_counts"].items() if n},
                # WHICH PROPERTY blocked, not just which detector. Four of the de-novo games carry
                # NO detector at all -- they are P3 orchard-dormancy inertness failures, and a
                # detector-only view would have reported them as unexplained blocks.
                "candidate_properties": sorted({v.get("property") for v in cand[k]["violations"]
                                                if v.get("property")}),
                "floor_properties": sorted({v.get("property") for v in floor[k]["violations"]
                                            if v.get("property")}),
            })
        else:
            out["neither"].append({"map_id": k[0], "seat": k[1]})
    return out


def main():
    cand_path, floor_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    cd, cand = load(cand_path)
    fd, floor = load(floor_path)

    if cd.get("run_identity") != "candidate":
        raise GateError(f"candidate arm declares run_identity {cd.get('run_identity')!r}")
    if fd.get("run_identity") != "floor":
        raise GateError(f"floor arm declares run_identity {fd.get('run_identity')!r} — a floor must "
                        f"be the parent judged against itself")
    if fd["candidate_sha256"] != fd["parent_sha256"]:
        raise GateError("floor arm is not self-judged")
    if cd["parent_sha256"] != fd["candidate_sha256"]:
        raise GateError(f"candidate's parent {cd['parent_sha256'][:12]} is not the floor bot "
                        f"{fd['candidate_sha256'][:12]} — this is not a matched floor")

    n, diverged = matched_corpus_gate(cand, floor)
    dec = decompose(cand, floor)

    # BOTH DIRECTIONS EXERCISED: a decomposition that only ever finds one direction has not
    # demonstrated it can see the other. Report it explicitly rather than implying coverage.
    directions = {"de_novo": len(dec["de_novo"]), "healed": len(dec["healed"])}
    by_property = collections.Counter()
    for r in dec["de_novo"]:
        for prop in (r["candidate_properties"] or ["(none recorded)"]):
            by_property[prop] += 1
    per_det = {}
    for d in DETECTORS:
        per_det[d] = {
            "de_novo_games": sum(1 for r in dec["de_novo"] if r["candidate_detectors"].get(d)),
            "healed_games": sum(1 for r in dec["healed"] if r["floor_detectors"].get(d)),
        }

    report = {
        "task": cd["task"],
        "candidate_sha256": cd["candidate_sha256"],
        "floor_sha256": fd["candidate_sha256"],
        "parent_of_candidate_sha256": cd["parent_sha256"],
        "corpus_version": cd["corpus_version"],
        "instrument_version": cd["instrument_version"],
        "games_per_arm": n,
        "games_where_candidate_changed_opponent_behaviour": diverged,
        "aggregate_context_only": {
            "candidate_blocking": sum(1 for g in cand.values() if g["block"]),
            "floor_blocking": sum(1 for g in floor.values() if g["block"]),
        },
        "keyed_by": "(map_id, seat)",
        "directions": directions,
        "both_directions_exercised": directions["de_novo"] > 0 and directions["healed"] > 0,
        "de_novo_by_property": dict(sorted(by_property.items())),
        "per_detector": per_det,
        "de_novo": dec["de_novo"],
        "healed": dec["healed"],
        "blocking_in_both": len(dec["both"]),
    }
    Path(out_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(f"  matched corpus gate PASS — {n} keyed games per arm; floor bot's stream "
          f"byte-identical across arms on all {n} (corpus matched AND floor deterministic)")
    print(f"  candidate changed opponent behaviour in {diverged} of {n} games")
    print(f"  aggregate (CONTEXT, NOT THE GATE): candidate "
          f"{report['aggregate_context_only']['candidate_blocking']} vs floor "
          f"{report['aggregate_context_only']['floor_blocking']} blocking")
    print(f"  DE-NOVO (blocks under candidate, not under floor): {directions['de_novo']}")
    print(f"  HEALED  (blocks under floor, not under candidate): {directions['healed']}")
    print(f"  both directions exercised: {report['both_directions_exercised']}")
    print(f"  de-novo by property: {dict(sorted(by_property.items()))}")
    for r in dec["de_novo"]:
        print(f"    de-novo  {r['map_id']} seat {r['seat']} [{r['class']}/{r['profile']}] "
              f"props={','.join(r['candidate_properties']) or '-'} det={r['candidate_detectors']}")
    print(f"  wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
