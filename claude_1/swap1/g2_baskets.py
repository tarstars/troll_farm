#!/usr/bin/env python3
r"""G-2 basket exhibits — the named fixtures, re-graded on cure alpha rev 2 with identity ENFORCED.

Task `20260821-swap-r1-cure`, gate **G-2**, second half of the amended gate
(`local_claude_1` `20260821T105914Z`):

> Basket evidence only through the episode-identity gate ... 005, 012, 001 reproduce and must turn
> FIXED there; **027 reproduces but alpha never fires on it** -- report "not alpha's shape", never
> count it. No basket is FIXED without identity.

Three arms through the SHARED harness (`claude_1/t1/fixture_harness.py`, whose `grade()` refuses
to run without an identity verdict):

- **subject** -- the bot that recorded the windows (`98628e98`), identity ENFORCED. It must
  reproduce 34/34; it is the gate's positive control, and if it fails no row in any other arm is
  worth reading.
- **base** -- the champion of record `547fa706`.
- **alpha rev 2** -- `cgauto/submissions/candidate-swap-r1-rev2.rs`, the P5 (yield-path-only)
  candidate codex_1 approved at `20260821T110533Z`.

The fire counts per fixture are NOT recomputed here; they are read from the G-1 rev-2 sweep, which
measured them with the parity-gated probe. A fixture where alpha never fires is reported as
"not alpha's shape" and is never counted as healed, whatever its verdict does.

Run:  python3 claude_1/swap1/g2_baskets.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
           "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / _p))
import fixture_harness as H  # noqa: E402

CHAMPION = REPO / "claude_1/chop4c/candidate-door1.rs"
CHAMPION_SHA256 = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
SUBJECT_SHA256 = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"
ALPHA = REPO / "cgauto/submissions/candidate-swap-r1-rev2.rs"
SWEEP = HERE / "g1-sweep-rev2-2026-08-21.json"
OUT = HERE / "g2-baskets-rev2-2026-08-21.json"

NAMED_MUST_FIX = ["OSC-001", "OSC-005", "OSC-012"]
NAMED_NOT_ALPHAS_SHAPE = ["OSC-027"]


class BasketError(Exception):
    """Anything that would make a number here mean something other than it says."""


def sha256_of(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def arm(label, source, sits, cfg, workdir, enforce_identity):
    binary = H.compile_candidate(source, workdir)
    rows = {}
    for sit in sorted(sits, key=lambda s: s["id"]):
        tr, eps, p4, _, lines = H.run_situation_ex(sit, binary, cfg)
        ident = H.episode_identity(sit["id"], sit, tr, lines)
        if enforce_identity and not ident["reproduces_the_recorded_episode"]:
            raise BasketError(f"{sit['id']}: the SUBJECT arm does not reproduce its own recorded "
                              f"episode ({ident['reasons']}).")
        row = H.grade(sit, tr, eps, p4, ident)
        row["identity_reasons"] = ident["reasons"]
        rows[row["id"]] = row
        print(f"  [{label}] {row['id']:<8} {row['verdict']}")
    return rows


def main() -> int:
    if sha256_of(CHAMPION) != CHAMPION_SHA256:
        raise BasketError("the champion file is not the champion of record.")
    if sha256_of(H.RESIDENT) != SUBJECT_SHA256:
        raise BasketError("the resident is not the library's subject bytes.")
    sweep = json.loads(SWEEP.read_text())
    if sweep.get("revision") is None and "g1-sweep-rev2" not in SWEEP.name:
        raise BasketError("the fire counts must come from the rev-2 sweep.")
    fires = {r["id"]: r["fires"] for r in sweep["rows"]}
    fire_turns = {r["id"]: sorted(d["turn"] for d in r.get("fire_detail", []))
                  for r in sweep["rows"]}

    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations()
    if len(sits) != 34:
        raise BasketError(f"the corpus IS the 34; got {len(sits)}.")

    with tempfile.TemporaryDirectory(prefix="swap-g2-baskets-") as wd:
        wd = Path(wd)
        for name in ("subject", "base", "alpha"):
            (wd / name).mkdir()
        subject = arm("subject", H.RESIDENT, sits, cfg, wd / "subject", enforce_identity=True)
        base = arm("base", CHAMPION, sits, cfg, wd / "base", enforce_identity=False)
        alpha = arm("alpha", ALPHA, sits, cfg, wd / "alpha", enforce_identity=False)

    if sum(1 for r in subject.values()
           if r["verdict"] != "NOT_REPRODUCIBLE_ON_BASE") != 34:
        raise BasketError("the subject arm does not reproduce 34/34.")

    # Why a cure arm can be NOT_REPRODUCIBLE: `episode_identity` asks whether THIS run replays the
    # RECORDED window, so any alpha fire at or before the window's last turn changes the window's
    # command lines and the gate rejects -- a cure that works on a fixture cannot also replay the
    # bug on it. The relation is computed here, per fixture, rather than asserted in prose.
    windows = {s["id"]: s["window"] for s in sits}

    table = []
    for fid in sorted(base):
        b, a = base[fid]["verdict"], alpha[fid]["verdict"]
        table.append({
            "id": fid, "kind": base[fid]["kind"],
            "base_verdict": b, "alpha_rev2_verdict": a,
            "alpha_fires": fires.get(fid),
            "reproduces_on_the_base": b != "NOT_REPRODUCIBLE_ON_BASE",
            "changed": b != a,
            "alphas_shape": bool(fires.get(fid)),
            "identity_reasons": alpha[fid]["identity_reasons"],
            "window_turns": [windows[fid]["turn_start"], windows[fid]["turn_end"]],
            "alpha_fire_turns": fire_turns.get(fid, []),
            "alpha_fires_inside_the_recorded_window": any(
                windows[fid]["turn_start"] <= t <= windows[fid]["turn_end"]
                for t in fire_turns.get(fid, [])),
        })

    reproducing = [r for r in table if r["reproduces_on_the_base"]]
    healed = [r["id"] for r in reproducing
              if r["base_verdict"] != "FIXED" and r["alpha_rev2_verdict"] == "FIXED"
              and r["alphas_shape"]]
    lost = [r["id"] for r in reproducing
            if r["base_verdict"] == "FIXED" and r["alpha_rev2_verdict"] != "FIXED"]
    not_alphas_shape = [r["id"] for r in reproducing if not r["alphas_shape"]]

    named = {}
    for fid in NAMED_MUST_FIX + NAMED_NOT_ALPHAS_SHAPE:
        row = next((r for r in table if r["id"] == fid), None)
        named[fid] = None if row is None else {
            "reproduces_on_the_base": row["reproduces_on_the_base"],
            "base_verdict": row["base_verdict"],
            "alpha_rev2_verdict": row["alpha_rev2_verdict"],
            "alpha_fires": row["alpha_fires"],
            "meets_the_amendment": (
                row["reproduces_on_the_base"] and row["alpha_rev2_verdict"] == "FIXED"
                if fid in NAMED_MUST_FIX
                else row["reproduces_on_the_base"] and row["alpha_fires"] == 0),
        }

    verdict = {
        "task": "20260821-swap-r1-cure", "gate": "G-2", "revision": 2,
        "amendment": ("coordination/messages/local_claude_1/"
                      "20260821T105914Z-20260821-swap-r1-cure-gate-amendment-policy.md"),
        "subject_reproduces": 34,
        "fixtures": len(table),
        "reproducing_on_the_base": len(reproducing),
        "healed_by_alpha_where_alpha_fires": healed,
        "fixed_on_the_base_and_lost": lost,
        "reproducing_but_not_alphas_shape": not_alphas_shape,
        "named_by_the_amendment": named,
        "rows": table,
    }
    verdict["named_all_met"] = all(v and v["meets_the_amendment"] for v in named.values())

    # The structural claim, MEASURED: on the alpha arm, is "fires inside the recorded window"
    # exactly the set that the identity gate rejects? If it is, NOT_REPRODUCIBLE on a cure arm is
    # an artefact of asking a replay question of a bot that was built to change the replay, and
    # not evidence about the cure.
    # The claim only has content over fixtures whose episode reproduces on the BASE at all: a
    # fixture the base already fails to replay is rejected for its own reasons, and alpha firing
    # inside its window tells us nothing. Scoping this correctly is the difference between a
    # measured claim and a coincidence -- the first version of this check compared the two sets
    # over all 34 and disagreed on the five fixtures that were already NOT_REPRODUCIBLE.
    inside = {r["id"] for r in table
              if r["alpha_fires_inside_the_recorded_window"] and r["reproduces_on_the_base"]}
    rejected = {r["id"] for r in table
                if r["alpha_rev2_verdict"] == "NOT_REPRODUCIBLE_ON_BASE"
                and base[r["id"]]["verdict"] != "NOT_REPRODUCIBLE_ON_BASE"}
    verdict["identity_gate_on_a_cure_arm"] = {
        "population": "the fixtures whose recorded episode reproduces on the base",
        "alpha_fires_inside_the_recorded_window": sorted(inside),
        "fires_inside_a_window_but_the_base_already_failed_to_replay_it": sorted(
            r["id"] for r in table
            if r["alpha_fires_inside_the_recorded_window"] and not r["reproduces_on_the_base"]),
        "newly_rejected_by_identity_on_the_alpha_arm": sorted(rejected),
        "the_two_sets_are_equal": inside == rejected,
        "why": ("fixture_harness.episode_identity asks whether the run replays the RECORDED "
                "window. An alpha fire at or before the window's last turn necessarily rewrites "
                "those command lines, so grade() returns NOT_REPRODUCIBLE_ON_BASE for precisely "
                "the fixtures where the cure acted on the episode. On a CURE arm the gate is "
                "therefore incapable of returning FIXED for a fixture the cure reached, which "
                "makes the amendment's 'must turn FIXED there' unreachable as written for those "
                "fixtures. Handed back, not worked around."),
    }
    OUT.write_text(json.dumps(verdict, indent=2) + "\n")

    print(f"\n  reproducing on the base: {len(reproducing)}/34")
    print(f"  healed by alpha (and alpha fires there): {healed or 'none'}")
    print(f"  FIXED on the base and lost: {lost or 'none'}")
    for fid, v in named.items():
        print(f"  {fid}: base={v['base_verdict']} alpha={v['alpha_rev2_verdict']} "
              f"fires={v['alpha_fires']}  meets-the-amendment={v['meets_the_amendment']}")
    print(f"\n  -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
