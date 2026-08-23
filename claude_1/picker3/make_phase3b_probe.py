#!/usr/bin/env python3
r"""Phase 3b — ONE probe builder for BOTH arms (P1+P2 base and the Phase-3b candidate).

The G-a census and the G-c partition need the SAME words `formed`, `selected` and `duplicated`
measured on both arms, or the classification compares two different definitions. So this builder
taps the idle-fallback site the same way in both shapes — the incumbent REPLACE body and the ruled
EXTEND body — and emits two rows per reaching tick:

    P3BFALL arm=<BASE|CAND> turn=<t> unit=<id> carried=<n> items=<cmd|score|target~...>
    P3BRET  arm=<BASE|CAND> turn=<t> unit=<id> items=<cmd|score|target~...>

`P3BFALL` is the state of `out` at the moment the fallback is entered — i.e. exactly what the
incumbent discards and what the candidate keeps. `P3BRET` is what the fallback actually returns.
Δ-A and Δ-B are read off these rows by the analyser, never recomputed inside the probe: the probe
prints, it does not classify.

Guards, all fail-closed:

1. **Subject digests verified** against the two build manifests (Phase 2's for the base arm,
   `build-manifest-phase3b-2026-08-23.json` for the candidate arm). A drifted subject is refused.
2. **Each anchor must match exactly once**, and the two fallback shapes must not BOTH match: an
   ambiguous subject is refused, not guessed at.
3. **The edit is confined to `main_candidates`**, verified by re-locating the function after the
   patch and requiring everything outside it to be byte-identical.
4. The probe is built FROM the shipped candidate, never the other way round (design §5, probe-shim
   inertness (b)): the panel/identity arms use `candidate-*-p3b.rs`, which carries no recorder.

Run:  python3 claude_1/picker3/make_phase3b_probe.py
"""
from __future__ import annotations

import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
P2 = REPO / "claude_1" / "picker2"

FN_HEAD = "            fn main_candidates(view:&GameState,unit:&Unit,"
FN_TAIL = "            fn carried_fruit(unit:&Unit)->Option<PlantKind>{"

BASE_OLD = """                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    return fallback;
                    }
"""

CAND_OLD = """                if idle_regeneration&&chops.is_empty(){
                    out.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        out.extend(Self::bank_candidates(view,unit));
                        }
                    return out;
                    }
"""

DUMP = ('.iter().map(|c|format!("{}|{:.6}|{:?}",c.command,c.score,c.target))'
        '.collect::<Vec<_>>().join("~")')

BASE_NEW = """                if idle_regeneration&&chops.is_empty(){
                    eprintln!("P3BFALL arm=BASE turn={} unit={} carried={} items={}",
                        view.turn,unit.id,unit.total_carried(),out%(DUMP)s);
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    eprintln!("P3BRET arm=BASE turn={} unit={} items={}",
                        view.turn,unit.id,fallback%(DUMP)s);
                    return fallback;
                    }
""" % {"DUMP": DUMP}

CAND_NEW = """                if idle_regeneration&&chops.is_empty(){
                    eprintln!("P3BFALL arm=CAND turn={} unit={} carried={} items={}",
                        view.turn,unit.id,unit.total_carried(),out%(DUMP)s);
                    out.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        out.extend(Self::bank_candidates(view,unit));
                        }
                    eprintln!("P3BRET arm=CAND turn={} unit={} items={}",
                        view.turn,unit.id,out%(DUMP)s);
                    return out;
                    }
""" % {"DUMP": DUMP}

SUBJECTS = {
    "cureC-base": (P2 / "candidate-cureC-p1p2.rs", HERE / "probe-cureC-base.rs"),
    "door1-base": (P2 / "candidate-door1-p1p2.rs", HERE / "probe-door1-base.rs"),
    "cureC-p3b": (HERE / "candidate-cureC-p3b.rs", HERE / "probe-cureC-p3b.rs"),
    "door1-p3b": (HERE / "candidate-door1-p3b.rs", HERE / "probe-door1-p3b.rs"),
}


class BuildError(Exception):
    """Anything that would make a probe row mean something other than it says."""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def allowlist() -> dict:
    p2 = json.loads((P2 / "build-manifest-2026-08-20.json").read_text())
    p3b = json.loads((HERE / "build-manifest-phase3b-2026-08-23.json").read_text())
    return {
        "cureC-base": p2["cureC"]["cand_sha256"], "door1-base": p2["door1"]["cand_sha256"],
        "cureC-p3b": p3b["subjects"]["cureC"]["output_sha256"],
        "door1-p3b": p3b["subjects"]["door1"]["output_sha256"],
    }


def locate_fn(text: str) -> tuple[int, int]:
    if text.count(FN_HEAD) != 1 or text.count(FN_TAIL) != 1:
        raise BuildError("main_candidates anchors are not unique")
    head, tail = text.find(FN_HEAD), text.find(FN_TAIL)
    if tail <= head:
        raise BuildError("tail anchor precedes head anchor")
    return head, tail


def patch(name: str, text: str) -> str:
    base_hits, cand_hits = text.count(BASE_OLD), text.count(CAND_OLD)
    if base_hits + cand_hits != 1:
        raise BuildError(f"{name}: fallback shapes matched BASE={base_hits} CAND={cand_hits}; "
                         f"exactly one match across both shapes is required")
    old, new = (BASE_OLD, BASE_NEW) if base_hits else (CAND_OLD, CAND_NEW)
    head, tail = locate_fn(text)
    if not (head < text.find(old) < tail):
        raise BuildError(f"{name}: the fallback is outside main_candidates")
    patched = text.replace(old, new)
    new_head, new_tail = locate_fn(patched)
    if text[:head] != patched[:new_head] or text[tail:] != patched[new_tail:]:
        raise BuildError(f"{name}: probe patch reached outside main_candidates")
    return patched


def main() -> int:
    want = allowlist()
    manifest = {"builder": "claude_1/picker3/make_phase3b_probe.py", "probes": {}}
    for name, (src, out) in SUBJECTS.items():
        text = src.read_text()
        digest = sha256(text)
        if digest != want[name]:
            raise BuildError(f"{name}: subject digest {digest[:16]} != manifest {want[name][:16]}")
        patched = patch(name, text)
        out.write_text(patched)
        manifest["probes"][name] = {
            "subject": str(src.relative_to(REPO)), "subject_sha256": digest,
            "probe": str(out.relative_to(REPO)), "probe_sha256": sha256(patched),
        }
        print(f"  probe {out.relative_to(REPO)}  sha256 {sha256(patched)[:16]}…")
    (HERE / "probe-manifest-phase3b-2026-08-23.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"PROBE BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
