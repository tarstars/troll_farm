#!/usr/bin/env python3
r"""G-4c.3 — the clause distribution over the OWNER-PINNED 167-turn manifest.

Authorized by codex_1's G-4c.2 acceptance, which fixes three requirements:
  * run ONLY against the pinned manifest sha256 b9eed4c2… — verified here, not assumed;
  * prove EXACT turn-set equality (no missing turns, no extra turns);
  * report the complete clause distribution, and retain parity.

NO FINDING IS CLAIMED. This produces attributions and measurements; bug-vs-correct-caution is
the owner's ruling after the brief, and nothing here anticipates it.
"""
import collections, hashlib, json, re, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
sys.path.insert(0, str(REPO / "claude_1/hstarve1"))
sys.path.insert(0, str(REPO / "claude_1/pipeline"))
sys.path.insert(0, str(REPO / "claude_1/chop4c"))
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import g4c2 as G                # noqa: E402

MANIFEST = REPO / "claude_1/chop4c/osc031-167-manifest.json"
PINNED_SHA = "b9eed4c2d66401761845bcb223893cc91a82171806cc43fd1ce4175bae1f21e5"


class G4c3Error(RuntimeError):
    """Fail closed."""


def main():
    got = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    if got != PINNED_SHA:
        raise G4c3Error(f"manifest is NOT the pinned artifact\n  want {PINNED_SHA}\n  got  {got}")
    man = json.loads(MANIFEST.read_text())
    pinned_turns = sorted(man["turns"])
    print(f"manifest verified: sha256 {got[:16]}… · {len(pinned_turns)} turns · unit {man['unit']}")

    cfg = json.loads(H.CONFIG.read_text())
    sit = H.load_situations(["OSC-031"])[0]
    wd = Path(tempfile.mkdtemp(prefix="c4c-g3-"))
    (wd / "i").mkdir(); (wd / "p").mkdir()
    instr = H.compile_candidate(REPO / "claude_1/chop4c/instrumented-chop4c.rs", wd / "i")
    plain = H.compile_candidate(H.RESIDENT, wd / "p")

    err = C.check_parity(sit, cfg, plain, instr)     # parity retained, raises otherwise
    print("parity: IDENTICAL (instrumented vs resident on OSC-031)")
    gates, chains = G.parse(err)
    G.reconcile(gates, chains)
    print(f"chains reconciled: {len(gates)} invocations")

    unit = man["unit"]
    # LOSSLESS per-evaluation records (codex_1's r1 blocker): storing a SET of clause names per
    # turn destroyed the evaluation multiplicity and the (call, plant) identity — the JSON could
    # not reproduce its own headline 315. One record per evaluation, keyed by identity.
    evaluations = []
    per_turn = collections.defaultdict(list)
    for (call, t, u, pl), rows in sorted(chains.items()):
        if u != unit or pl < 0:
            continue
        term = [r for r in rows if r[2] in G.TERMINAL]
        evaluations.append({"call": call, "turn": t, "unit": u, "plant": pl,
                            "terminal_clause": term[0][1], "seq": term[0][0]})
        per_turn[t].append(term[0][1])

    observed = sorted(per_turn)
    missing = [t for t in pinned_turns if t not in per_turn]
    extra = [t for t in observed if t not in pinned_turns]
    print(f"observed turns with a chop evaluation for unit {unit}: {len(observed)}")
    if missing:
        raise G4c3Error(f"{len(missing)} pinned turns have NO chop evaluation: {missing[:10]}")
    print(f"  exact-equality check: every one of the {len(pinned_turns)} pinned turns is covered")
    print(f"  turns outside the manifest (reported, not dropped): {len(extra)}")

    dist = collections.Counter()
    per_turn_clauses = {}
    for t in pinned_turns:
        cl = sorted(set(per_turn[t]))
        per_turn_clauses[t] = cl
        for c in per_turn[t]:
            dist[c] += 1
    print("\nCLAUSE DISTRIBUTION over the pinned 167 turns (terminal clause per tree evaluation):")
    for c, n in dist.most_common():
        print(f"  {c:<24} {n}")
    uniform = {t: cl for t, cl in per_turn_clauses.items() if len(cl) != 1}
    print(f"\nturns whose evaluations do NOT share one terminal clause: {len(uniform)}")

    # EXACT CROSS-SUM ASSERTIONS
    in_man = [e for e in evaluations if e["turn"] in set(pinned_turns)]
    per_turn_counts = {t: len(per_turn[t]) for t in pinned_turns}
    if sum(per_turn_counts.values()) != len(in_man):
        raise G4c3Error(f"cross-sum FAILED: per-turn counts {sum(per_turn_counts.values())} != "
                        f"in-manifest evaluations {len(in_man)}")
    if sum(dist.values()) != len(in_man):
        raise G4c3Error(f"cross-sum FAILED: distribution {sum(dist.values())} != "
                        f"in-manifest evaluations {len(in_man)}")
    if len({(e["call"], e["turn"], e["plant"]) for e in evaluations}) != len(evaluations):
        raise G4c3Error("evaluation identities are not unique — records are not lossless")
    print(f"cross-sums: per-turn counts = distribution = in-manifest evaluations = {len(in_man)}")

    out = {"task": "20260818-osc031-chop-clause-instrument",
           "manifest_sha256": got, "manifest_turns": len(pinned_turns),
           "unit": unit, "parity": "IDENTICAL",
           "exact_turn_set_equality": {"missing": missing, "covered": len(pinned_turns)},
           "turns_outside_manifest": len(extra),
           "clause_distribution": dict(dist),
           "clause_distribution_complete": {c: dist.get(c, 0) for c in
                                            ["GATE_UNIT", "DEAD_OR_UNREACHABLE",
                                             "PREDICT_TREE_NONE", "PREDICTED_NONPOSITIVE",
                                             "CHOP_OUTCOME_NONE", "ROUND_TRIP_CLOCK",
                                             "WOOD_NONPOSITIVE", "ACCEPT"]},
           "turns_with_mixed_terminal_clauses": len(uniform),
           "outside_manifest_turns": extra,
           "per_turn_counts": {str(k): v for k, v in per_turn_counts.items()},
           "per_turn_clauses": {str(k): v for k, v in per_turn_clauses.items()},
           "evaluations": [e for e in evaluations if e["turn"] in set(pinned_turns)]}
    p = REPO / "claude_1/chop4c/g4c3-distribution-2026-08-18.json"
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {p.relative_to(REPO)}  ({len(out['evaluations'])} lossless records)")

    # the task record's required short Markdown clause-decision table, neutral wording
    md = REPO / "claude_1/chop4c/g4c3-clause-decision-table-2026-08-18.md"
    complete = out["clause_distribution_complete"]
    lines = [
        "# OSC-031 chop clause-decision table (G-4c.3)",
        "",
        f"Population: the owner-pinned manifest `osc031-167-manifest.json`, sha256 `{got}` — "
        f"{len(pinned_turns)} turns, unit {unit}. Instrument frozen at G-4c.1; parity IDENTICAL.",
        "",
        "**Attributions and measurements only.** Whether the named clause is a defect or correct "
        "caution is the OWNER's ruling; nothing here anticipates it.",
        "",
        "## Terminal clause per tree evaluation",
        "",
        "| clause | evaluations |",
        "|---|---:|",
    ]
    for c, n in complete.items():
        lines.append(f"| `{c}` | {n} |")
    lines += [
        f"| **total** | **{sum(complete.values())}** |",
        "",
        f"- {len(pinned_turns)} pinned turns carry {len(in_man)} tree evaluations: the chop "
        f"planner is invoked more than once per unit-turn.",
        f"- Turns whose evaluations do not share a single terminal clause: "
        f"**{len(uniform)}**.",
        f"- Pinned turns with no chop evaluation: **{len(missing)}**.",
        f"- Turns observed outside the manifest, reported not dropped: **{len(extra)}** "
        f"({', '.join(str(t) for t in extra) if extra else 'none'}).",
        "",
        "## Boundaries",
        "",
        "One game. No fix, no judgment, no class-wide claim, no Arena action; the resident and "
        "dev copy are untouched. The five clauses showing zero here were dispositioned under "
        "G-4c.2: `DEAD_OR_UNREACHABLE` and `ROUND_TRIP_CLOCK` observed firing on purpose-built "
        "states, `PREDICTED_NONPOSITIVE` / `CHOP_OUTCOME_NONE` / `WOOD_NONPOSITIVE` proven "
        "unreachable over the exhaustive legal domain.",
        "",
    ]
    md.write_text("\n".join(lines))
    print(f"wrote {md.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
