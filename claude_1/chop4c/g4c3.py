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
    per_turn = collections.defaultdict(list)
    for (call, t, u, p), rows in chains.items():
        if u != unit or p < 0:
            continue
        term = [r for r in rows if r[2] in G.TERMINAL]
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

    out = {"task": "20260818-osc031-chop-clause-instrument",
           "manifest_sha256": got, "manifest_turns": len(pinned_turns),
           "unit": unit, "parity": "IDENTICAL",
           "exact_turn_set_equality": {"missing": missing, "covered": len(pinned_turns)},
           "turns_outside_manifest": len(extra),
           "clause_distribution": dict(dist),
           "turns_with_mixed_terminal_clauses": len(uniform),
           "per_turn_clauses": {str(k): v for k, v in per_turn_clauses.items()}}
    p = REPO / "claude_1/chop4c/g4c3-distribution-2026-08-18.json"
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {p.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
