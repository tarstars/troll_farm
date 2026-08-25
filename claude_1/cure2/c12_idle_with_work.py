#!/usr/bin/env python3
"""C-12 -- per-troll idle-with-work share, with `fuzz_panel --p4b` ON.

G-0 section 9 carries the bar

    C-12 | per-troll idle-with-work share, and P4b once accepted | <= 1.5 %

and section 8 repeats it as a kill condition.  P4b was accepted and wired into `fuzz_panel` behind
`--p4b`, default OFF, on the coordinator's order 20260825T181413Z.  This run turns the flag ON and
reads what comes back.

WHAT COMES BACK IS NOT A NUMBER, AND THAT IS THE FINDING.

`claude_1/pipeline/p4b_gate.py` -- codex_1's accepted evaluator -- reads the resolver branch off the
telemetry wire with `import narrate4`.  The candidate-2 arms narrate **v5**.  Two independent
consequences, both measured here rather than argued:

  1. `narrate4.decode` refuses any payload whose version token is not `v4` (it says so in as many
     words), so EVERY telemetry row of EVERY game is a decode error.  The arm comes back
     `GATE_UNREADY`, which is an instrument failure and not a verdict -- and emphatically not a
     0.0 % pass.
  2. Even handed a version-agnostic decoder it would still be wrong, because its numerator is
     `branch in {H, W}` and **v5 retires `H`**: `H` is off-grammar in `narrate5.BRANCH_CODES`
     ("PLRWNSX"), a v5 payload carrying one is a decode error, and control C-9 pre-committed
     "no `H`".  Half of the accepted definition names a branch that cannot occur on this
     candidate.

So the honest C-12 verdict on the accepted gate is NOT_EVALUABLE.  This run proves that with
positive controls (narrate4 refuses a real payload off this corpus; narrate5 reads the same bytes
cleanly) rather than by reading the two modules and asserting it.

THEN THE QUANTITY, RESTATED FOR THE v5 GRAMMAR -- clearly labelled as claude_1's restatement and
NOT as codex_1's accepted evaluator, because P4b's acceptance predates this grammar and adapting a
bar is a definition change, which is the coordinator's to make and not mine.  v5's non-moving
branches are `W` (forced WAIT) and `N` (no MOVE this turn); `H` (voluntary hold) is gone with
Candidate 1's rule.  Two readings, both published, because they differ and the choice is a ruling:

  * R1, DEFINITION-FAITHFUL: `{H, W}` transposed verbatim, i.e. `W` alone since `H` cannot occur.
  * R2, NON-MOVING: `{W, N}` -- every turn the unit did not move.  Published, and published with
    its caveat: `N` is "no MOVE this turn", and a unit issuing `CHOP`, `PICK` or `DROP` is an `N`.
    R2 is therefore an upper bound on non-movement and **is not idleness**; taken as an idle share
    it is simply wrong, and this run says so rather than quoting the 87 % it produces.
  * R3, EXPLORATORY and NOT a bar candidate: `W` or `N`, with a CONCRETE `available` target, and no
    progress event that turn.  Published because it is the obvious thing to try and because it is
    WRONG, in a way worth recording: a troll spending eleven turns felling a tree issues `CHOP`
    (an `N`) with the tree concrete and available, and `progress_event` sees nothing until the tree
    falls -- so productive work is counted as idle.  That is precisely why the accepted definition
    counts 60-turn EPISODES rather than a per-turn share.  R3 is reported with this caveat and is
    never offered against the 1.5 % bar.

AND THE ACCEPTED COMPUTATION ITSELF, WITH ONLY THE DECODER SWAPPED.  `p4b_gate.evaluate_rows` takes
its narrator as a PARAMETER.  Everything in it except that parameter -- `concrete`,
`progress_event`, `maximal_runs`, the W=60 window, the tripwire, `compare` -- is grammar-independent
and survives the version break intact.  So the accepted evaluator is re-driven here with `narrate5`
passed in its narrator slot: not a restatement, not a port, the same function on the same rows with
a decoder that can read them.  On a v5 wire its `{H, W}` numerator IS `W` alone, which is R1 by
another route; the two must agree and G-X requires it.  This is the number C-12 should be read on.

GATES -- each aborts rather than degrading a number:

  G-S   subject identity.  `arm-instrument.rs` hashes to the sha256 in `arm-manifest.json`, its
        sidecar and `cure2-instrument-config.json`, declares `SWAP_RULE_ENABLED=true` and
        `NARRATE_V5_ENABLED=true`; `arm-ruleoff.rs` declares the rule false with narration still
        true and differs on exactly one line.
  G-2B  the C-2 bridge.  The candidate arm narrates nothing (`NARRATE_V5_ENABLED=false`) and is
        not telemetry-evaluable by ANY gate; the subject is the instrument arm and the carry is
        `results/arm-equivalence.json`'s 240/240 byte-identical in play.  Stated, gated, never
        silently assumed.
  G-A1  the v4 refusal is a version refusal.  `narrate4.decode` must raise on a payload taken off
        this corpus, and the message must name the version.
  G-A2  the same bytes must decode cleanly under `narrate5`.  Together G-A1/G-A2 separate "the
        accepted gate cannot read this wire" from "this wire is broken".
  G-H   no `H` occurs anywhere on either arm's wire -- the second reason, measured.
  G-X   cross-check.  My per-unit branch tallies, summed, must equal `narrate5`'s own census
        branch totals for the same arm.  Without this the restated shares would be a number of my
        own making.
  G-V   vacuity.  The restated counter must be shown capable of firing: at least one unit life
        with a strictly positive share under each published reading, and at least one idle turn
        naming a CONCRETE target.  A 0.0 % produced by a branch that never occurs is not a pass.
  G-K5  population: 240 games / 120 maps / both seats per map, on both arms.

VERDICT.  Two fields, never collapsed into one:
  `p4b_gate_applicability` -- NOT_EVALUABLE / EVALUABLE, on the accepted gate as wired.
  `restated_v5_read`       -- PASS / BLOCK / INCONCLUSIVE, on claude_1's v5 restatement, under
                              both readings, against the same 1.5 % bar.

    python3 claude_1/cure2/c12_idle_with_work.py
"""
from __future__ import annotations

import collections
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/pipeline", "claude_1/narrate4", "claude_1/narrate5"):
    sys.path.insert(0, str(REPO / _p))

import fuzz_panel as fp               # noqa: E402
import narrate4                       # noqa: E402
import narrate5 as n5                 # noqa: E402
import p4b_gate                       # noqa: E402

INSTRUMENT = HERE / "arm-instrument.rs"
RULEOFF = HERE / "arm-ruleoff.rs"
CANDIDATE = HERE / "arm-candidate.rs"
MANIFEST = HERE / "arm-manifest.json"
INSTRUMENT_CFG = HERE / "cure2-instrument-config.json"
RULEOFF_CFG = HERE / "cure2-ruleoff-config.json"
EQUIV = HERE / "results" / "arm-equivalence.json"
OUT = HERE / "results" / "c12-idle-with-work.json"

BAR_PCT = 1.5
RULE_ON = "const SWAP_RULE_ENABLED:bool=true;"
RULE_OFF = "const SWAP_RULE_ENABLED:bool=false;"
NARRATE_ON = "const NARRATE_V5_ENABLED:bool=true;"
NARRATE_OFF = "const NARRATE_V5_ENABLED:bool=false;"
SCRATCH = ("/tmp/claude-1000/cure2/cure2-instrument", "/tmp/claude-1000/cure2/cure2-ruleoff")


class GateError(Exception):
    """Anything that would make the numbers below mean something other than they say."""


def subject_gate() -> dict:
    """G-S: the subject is the instrument arm; the baseline is the rule-off arm."""
    manifest = json.loads(MANIFEST.read_text())["arms"]
    out = {}
    for name, path, want_rule in (("instrument", INSTRUMENT, True),
                                  ("ruleoff", RULEOFF, False)):
        text = path.read_text()
        digest = hashlib.sha256(text.encode()).hexdigest()
        if digest != manifest[name]["sha256"]:
            raise GateError(f"{path.name} hashes {digest[:12]} but arm-manifest.json declares "
                            f"{manifest[name]['sha256'][:12]} (G-S)")
        sidecar = Path(str(path) + ".sha256").read_text().split()[0]
        if sidecar != digest:
            raise GateError(f"{path.name}.sha256 says {sidecar[:12]}, bytes say "
                            f"{digest[:12]} (G-S)")
        marker, anti = ((RULE_ON, RULE_OFF) if want_rule else (RULE_OFF, RULE_ON))
        if marker not in text or anti in text:
            raise GateError(f"{path.name} does not declare SWAP_RULE_ENABLED={want_rule} (G-S)")
        if NARRATE_ON not in text or NARRATE_OFF in text:
            raise GateError(f"{path.name} does not declare NARRATE_V5_ENABLED=true; an arm with "
                            f"no telemetry is not P4b-evaluable at all (G-S)")
        out[name] = {"file": path.name, "sha256": digest, "swap_rule_enabled": want_rule,
                     "narrate_v5_enabled": True}
    for name, cfg_path in (("instrument", INSTRUMENT_CFG), ("ruleoff", RULEOFF_CFG)):
        declared = json.loads(cfg_path.read_text())["candidate"]["sha256"]
        if declared != out[name]["sha256"]:
            raise GateError(f"{cfg_path.name} declares candidate {declared[:12]}, subject is "
                            f"{out[name]['sha256'][:12]} (G-S)")
    a, b = INSTRUMENT.read_text().split("\n"), RULEOFF.read_text().split("\n")
    if len(a) != len(b):
        raise GateError(f"arms have {len(a)} and {len(b)} lines (G-S)")
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(diff) != 1 or RULE_ON not in a[diff[0]] or RULE_OFF not in b[diff[0]]:
        raise GateError(f"instrument and ruleoff differ on {len(diff)} lines and not solely in "
                        f"the swap-rule flag (G-S)")
    out["sole_line_differing_0_indexed"] = diff[0]
    return out


def bridge_gate() -> dict:
    """G-2B: the arm that will be submitted narrates nothing, so it is measured through C-2."""
    if NARRATE_OFF not in CANDIDATE.read_text():
        raise GateError("arm-candidate.rs no longer declares NARRATE_V5_ENABLED=false; the "
                        "premise of this bridge has changed (G-2B)")
    equiv = json.loads(EQUIV.read_text())
    if equiv.get("verdict") != "PASS" or equiv.get("diverging") or \
            equiv.get("identical") != equiv.get("games"):
        raise GateError(f"C-2 arm equivalence is not a clean 240/240 "
                        f"({equiv.get('identical')}/{equiv.get('games')}) -- the instrument arm's "
                        f"number cannot be carried to the candidate arm (G-2B)")
    return {"control": "C-2", "identical": equiv["identical"], "games": equiv["games"],
            "meaning": "the candidate arm emits no telemetry and is not evaluable by any "
                       "wire-reading gate; the read is taken on the instrument arm and carried "
                       "by C-2's 240/240 byte-identity in play, not measured on the candidate"}


def run_panel(cfg_path: Path, workdir: Path, p4b_baseline: Path | None):
    """Run `fuzz_panel --p4b` through the CLI, exactly as a reproducer would."""
    cfg = fp.load_config(cfg_path)
    games = Path(cfg["games_dir"]) / "games.jsonl.gz"
    report = workdir / (cfg_path.stem + "-p4b.md")
    js = workdir / (cfg_path.stem + "-p4b.json")
    cmd = [sys.executable, str(REPO / "claude_1/pipeline/fuzz_panel.py"),
           "--config", str(cfg_path), "--report", str(report), "--json", str(js), "--p4b"]
    if p4b_baseline is not None:
        cmd += ["--p4b-baseline", str(p4b_baseline)]
    print("  $ fuzz_panel.py --config %s ... --p4b%s"
          % (cfg_path.name, " --p4b-baseline <ruleoff games>" if p4b_baseline else ""),
          flush=True)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout.strip():
        print("    " + proc.stdout.strip().splitlines()[-1], flush=True)
    if not js.exists():
        raise GateError(f"fuzz_panel produced no JSON for {cfg_path.name} "
                        f"(rc={proc.returncode}): {proc.stderr.strip()[:400]}")
    data = json.loads(js.read_text())
    if "p4b" not in data:
        raise GateError(f"{cfg_path.name} run carries no p4b packet -- the flag did not take")
    return data, games


def sample_payload(rows) -> tuple[str, str]:
    """One real telemetry payload off this corpus, with the game it came from."""
    for game in rows:
        for line in game["artifacts"]["candidate_commands"].rstrip("\n").split("\n"):
            frags = n5.msg_fragments(line)
            if frags:
                return f"{game['map_id']}:{game['seat']}", frags[0].strip()
    raise GateError("no telemetry payload anywhere on the arm (G-A2)")


def decoder_controls(rows) -> dict:
    """G-A1 / G-A2: the accepted gate's refusal is a VERSION refusal, not a broken wire."""
    where, payload = sample_payload(rows)
    try:
        narrate4.decode(payload)
    except Exception as exc:                                   # noqa: BLE001
        refusal = f"{type(exc).__name__}: {exc}"
    else:
        raise GateError("narrate4.decode ACCEPTED a v5 payload -- the applicability finding "
                        "below is wrong and must not be published (G-A1)")
    if "version" not in refusal.lower():
        raise GateError(f"narrate4 refused the payload but not on the version: {refusal} (G-A1)")
    turn, units, _order, _banner, meta = n5.decode(payload)
    return {"payload_from": where, "payload_chars": len(payload),
            "narrate4_refusal": refusal,
            "narrate5_decode": {"turn": turn, "units": len(units), "meta": meta},
            "meaning": "the same bytes are refused by the accepted gate's decoder on the version "
                       "token and read cleanly by the arm's own decoder: p4b_gate cannot read "
                       "this wire, and the wire is not at fault"}


def read_arm(rows) -> dict:
    """The restated v5 read, per unit life, plus this arm's own narrate5 census (for G-X)."""
    census = n5.new_census()
    units_out, tele_errors = {}, []
    for game in rows:
        key = (game["map_id"], int(game["seat"]))
        commands = game["artifacts"]["candidate_commands"]
        lines = commands.rstrip("\n").split("\n")
        tr = fp.td.build_trace(game["artifacts"]["candidate_transcript"], commands)
        tele_errors.extend(f"{key}: {e}" for e in
                           n5.check_telemetry(f"{key[0]}:{key[1]}", tr, lines, census))
        wire = {}
        for index, line in enumerate(lines, 1):
            frags = n5.msg_fragments(line)
            if len(frags) != 1:
                continue
            turn, us, _o, _b, _m = n5.decode(frags[0].strip())
            for uid, (_chosen, available, branch, _blocked) in us.items():
                wire[(turn, uid)] = (available, branch)
        own = {t: sorted(u.id for u in tr.state(t).own_units()) for t in range(1, tr.T + 1)}
        for uid in sorted({u for ids in own.values() for u in ids}):
            alive = [t for t in range(1, tr.T + 1) if uid in own[t]]
            seen = [wire[(t, uid)] for t in alive if (t, uid) in wire]
            tally = collections.Counter(b for _a, b in seen)
            work = collections.Counter(b for a, b in seen if p4b_gate.concrete(a))
            # R3: non-moving, concrete target available, and no progress event that turn.
            # `progress_event` is imported from the accepted evaluator -- it reads the trace, not
            # the wire, so it is the one part of P4b the v4/v5 break leaves intact.
            alive_seen = [t for t in alive if (t, uid) in wire]
            idle_work_noprog, n_with_progress = [], 0
            for t in alive_seen:
                available, branch = wire[(t, uid)]
                prog = p4b_gate.progress_event(tr, uid, t)
                if branch == "N" and prog:
                    n_with_progress += 1
                if branch in ("W", "N") and p4b_gate.concrete(available) and not prog:
                    idle_work_noprog.append(t)
            n = len(seen)
            def pct(x):
                return round(100.0 * x / n, 6) if n else 0.0
            units_out[(key[0], key[1], uid)] = {
                "map_id": key[0], "seat": key[1], "unit_id": uid,
                "alive_interval": [alive[0], alive[-1]], "telemetry_turns": n,
                "branches": dict(tally), "branches_with_concrete_target": dict(work),
                "w": tally["W"], "n_branch": tally["N"], "h": tally["H"],
                "share_definition_faithful_pct": pct(tally["W"]),
                "share_intent_faithful_pct": pct(tally["W"] + tally["N"]),
                "share_definition_faithful_with_work_pct": pct(work["W"]),
                "share_intent_faithful_with_work_pct": pct(work["W"] + work["N"]),
                "n_branch_with_progress": n_with_progress,
                "idle_with_work_turns": len(idle_work_noprog),
                "share_idle_with_work_pct": pct(len(idle_work_noprog)),
                "first_idle_with_work_turns": idle_work_noprog[:5],
            }
    return {"units": units_out, "census": census, "telemetry_errors": tele_errors}


def cross_check(read: dict, label: str) -> None:
    """G-X: the restated tallies are narrate5's own, not a private recount."""
    mine = collections.Counter()
    for rec in read["units"].values():
        mine.update(rec["branches"])
    theirs = collections.Counter({k: v for k, v in read["census"]["branches"].items() if v})
    if mine != theirs:
        raise GateError(f"{label}: per-unit branch tallies {dict(mine)} do not equal narrate5's "
                        f"census {dict(theirs)} (G-X)")


def summarize(read: dict) -> dict:
    units = list(read["units"].values())
    total = sum(u["telemetry_turns"] for u in units)
    agg = collections.Counter()
    for u in units:
        agg.update(u["branches"])
        for b, v in u["branches_with_concrete_target"].items():
            agg[b + "_with_work"] += v
    def pct(x):
        return round(100.0 * x / total, 6) if total else 0.0
    keys = ("share_definition_faithful_pct", "share_intent_faithful_pct",
            "share_definition_faithful_with_work_pct", "share_intent_faithful_with_work_pct",
            "share_idle_with_work_pct")
    above = {k: [{"map_id": u["map_id"], "seat": u["seat"], "unit_id": u["unit_id"],
                  "share_pct": u[k], "telemetry_turns": u["telemetry_turns"]}
                 for u in units if u[k] > BAR_PCT] for k in keys}
    return {
        "unit_lives": len(units), "telemetry_turns_graded": total,
        "branch_totals": dict(agg),
        "corpus_share_definition_faithful_pct": pct(agg["W"]),
        "corpus_share_intent_faithful_pct": pct(agg["W"] + agg["N"]),
        "corpus_share_definition_faithful_with_work_pct": pct(agg["W_with_work"]),
        "corpus_share_intent_faithful_with_work_pct": pct(agg["W_with_work"]
                                                          + agg["N_with_work"]),
        "n_branch_with_progress": sum(u["n_branch_with_progress"] for u in units),
        "idle_with_work_turns": sum(u["idle_with_work_turns"] for u in units),
        "corpus_share_idle_with_work_pct": pct(sum(u["idle_with_work_turns"] for u in units)),
        "max_unit_share": {k: max((u[k] for u in units), default=0.0) for k in keys},
        "unit_lives_with_positive_share": {
            k: sum(1 for u in units if u[k] > 0.0) for k in keys},
        "unit_lives_above_bar": {k: v for k, v in above.items()},
        "unit_lives_above_bar_counts": {k: len(v) for k, v in above.items()},
        "h_branch_turns": agg["H"],
        "telemetry_errors": len(read["telemetry_errors"]),
    }


def main() -> int:
    print("C-12 -- per-troll idle-with-work share, fuzz_panel --p4b ON", flush=True)
    subject = subject_gate()
    print("  G-S ok: subject arm-instrument.rs %s, baseline arm-ruleoff.rs %s, one line apart"
          % (subject["instrument"]["sha256"][:12], subject["ruleoff"]["sha256"][:12]), flush=True)
    bridge = bridge_gate()
    print("  G-2B ok: C-2 %d/%d identical in play" % (bridge["identical"], bridge["games"]),
          flush=True)

    with tempfile.TemporaryDirectory(prefix="cure2-c12-") as wd:
        wd = Path(wd)
        base_data, base_games = run_panel(RULEOFF_CFG, wd, None)
        subj_data, _ = run_panel(INSTRUMENT_CFG, wd, base_games)
        packet = subj_data["p4b"]
        rows = {"instrument": fp.load_archive_rows(
                    Path(fp.load_config(INSTRUMENT_CFG)["games_dir"]) / "games.jsonl.gz"),
                "ruleoff": fp.load_archive_rows(base_games)}

    baseline_label = sorted(k for k in packet["arms"] if k != "panel")[0]
    accepted = {"instrument": packet["arms"]["panel"], "ruleoff": packet["arms"][baseline_label]}
    applicability = {
        name: {"status": arm["status"], "errors": len(arm["errors"]),
               "unit_lives_graded": len(arm["unit_rows"]),
               "first_errors": arm["errors"][:3]}
        for name, arm in accepted.items()}
    evaluable = all(a["status"] == "READY" and not a["errors"] for a in applicability.values())
    print("  --p4b ON: instrument %s (%d evaluator errors), ruleoff %s (%d)"
          % (applicability["instrument"]["status"], applicability["instrument"]["errors"],
             applicability["ruleoff"]["status"], applicability["ruleoff"]["errors"]), flush=True)

    # The accepted computation, decoder swapped -- `evaluate_rows` takes its narrator as an
    # argument, so this is p4b_gate's own code on p4b_gate's own definition.
    v5_decoded = {name: p4b_gate.evaluate_rows(r, fp.td, n5, f"{name} arm (v5-decoded)",
                                               fp.stream_digest(r))
                  for name, r in rows.items()}
    for name, arm in v5_decoded.items():
        if arm["status"] != "READY" or arm["errors"]:
            raise GateError(f"{name}: the accepted computation is {arm['status']} with "
                            f"{len(arm['errors'])} errors even with a v5 decoder, e.g. "
                            f"{arm['errors'][0]} -- the applicability finding would then be "
                            f"about more than the decoder and must not be published as decoder-"
                            f"only (G-A2)")
    v5_compare = p4b_gate.compare(v5_decoded["ruleoff"], v5_decoded["instrument"])
    print("  accepted computation re-driven with narrate5: instrument READY, %d parked-unit "
          "episodes; ruleoff READY, %d; differential %s"
          % (v5_decoded["instrument"]["totals"].get("episodes", 0),
             v5_decoded["ruleoff"]["totals"].get("episodes", 0), v5_compare["status"]),
          flush=True)

    controls = decoder_controls(rows["instrument"])
    print("  G-A1 ok: narrate4 refuses a real payload -- %s" % controls["narrate4_refusal"][:90],
          flush=True)
    print("  G-A2 ok: narrate5 reads the same bytes (turn %d, %d units)"
          % (controls["narrate5_decode"]["turn"], controls["narrate5_decode"]["units"]),
          flush=True)

    reads = {name: read_arm(r) for name, r in rows.items()}
    for name, read in reads.items():
        cross_check(read, name)
        if read["telemetry_errors"]:
            raise GateError(f"{name}: {len(read['telemetry_errors'])} v5 telemetry errors, e.g. "
                            f"{read['telemetry_errors'][0]} -- the restated read refuses to "
                            f"grade a wire its own decoder rejects")
    for name, arm in v5_decoded.items():
        theirs = {(r["map_id"], r["seat"], r["unit_id"]): r["idle_with_work_share_pct"]
                  for r in arm["unit_rows"]}
        mine = {k: v["share_definition_faithful_pct"] for k, v in reads[name]["units"].items()}
        if set(theirs) != set(mine):
            raise GateError(f"{name}: the accepted computation graded {len(theirs)} unit lives, "
                            f"the restatement {len(mine)} (G-X)")
        bad = [(k, theirs[k], mine[k]) for k in theirs if abs(theirs[k] - mine[k]) > 1e-6]
        if bad:
            raise GateError(f"{name}: R1 does not equal the accepted computation's share on "
                            f"{len(bad)} unit lives, e.g. {bad[0]} (G-X)")
    print("  G-X ok: per-unit branch tallies equal narrate5's census, and R1 equals the accepted "
          "computation's own share on every unit life, on both arms", flush=True)
    summary = {name: summarize(read) for name, read in reads.items()}
    if any(s["h_branch_turns"] for s in summary.values()):
        raise GateError("an `H` branch appears on a v5 arm -- off grammar (G-H)")
    print("  G-H ok: 0 `H` turns on either arm; the accepted numerator's {H, W} is half dead "
          "by grammar", flush=True)

    subj = summary["instrument"]
    notes = []
    for key, label in (("share_definition_faithful_pct", "R1 definition-faithful (W)"),
                       ("share_idle_with_work_pct", "R3 idle-with-work")):
        if subj["unit_lives_with_positive_share"][key] == 0:
            notes.append(f"G-V: no unit life on the subject arm has a positive {label} share -- "
                         f"that 0.0 % is a branch that never occurs, not a measurement")
    if subj["corpus_share_intent_faithful_with_work_pct"] == 0.0:
        notes.append("G-V: no idle turn on the subject arm names a CONCRETE target -- the bar's "
                     "own words, 'with work', are not exercised by this corpus")
    if not packet["controls"]["K5_exact_240"]:
        notes.append("G-K5: population is not the exact 240 / 120 maps / both seats")

    breached = {k: v for k, v in subj["unit_lives_above_bar"].items() if v}
    # The headline is the accepted computation's own share (v5-decoded), read the two ways the
    # bar's wording admits.  Which one C-12 means is a ruling, so BOTH are published and the
    # verdict is the conjunction: a bar breached under either reading is not reported as passed.
    headline = {}
    for name, arm in v5_decoded.items():
        above = [{"map_id": r["map_id"], "seat": r["seat"], "unit_id": r["unit_id"],
                  "share_pct": r["idle_with_work_share_pct"],
                  "telemetry_turns": r["observable_transitions"]}
                 for r in arm["unit_rows"] if r["idle_with_work_share_pct"] > BAR_PCT]
        headline[name] = {
            "per_troll_max_pct": max((r["idle_with_work_share_pct"]
                                      for r in arm["unit_rows"]), default=0.0),
            "unit_lives_above_bar": len(above), "unit_lives": len(arm["unit_rows"]),
            "above_bar": sorted(above, key=lambda r: -r["share_pct"]),
            "corpus_share_pct": summary[name]["corpus_share_definition_faithful_pct"],
            "parked_unit_episodes": arm["totals"].get("episodes", 0),
            "per_troll_reading": "BLOCK" if above else "PASS",
            "corpus_reading": ("PASS" if summary[name]["corpus_share_definition_faithful_pct"]
                               <= BAR_PCT else "BLOCK"),
        }
    headline_breach = headline["instrument"]["above_bar"]
    if headline_breach:
        restated = "BLOCK"
    elif notes:
        restated = "INCONCLUSIVE"
    else:
        restated = "PASS"

    delta = {k: round(summary["instrument"][k] - summary["ruleoff"][k], 6)
             for k in ("corpus_share_definition_faithful_pct",
                       "corpus_share_intent_faithful_pct",
                       "corpus_share_definition_faithful_with_work_pct",
                       "corpus_share_intent_faithful_with_work_pct",
                       "corpus_share_idle_with_work_pct")}
    delta["unit_lives_above_bar_R3"] = (
        len(summary["instrument"]["unit_lives_above_bar"]["share_idle_with_work_pct"])
        - len(summary["ruleoff"]["unit_lives_above_bar"]["share_idle_with_work_pct"]))

    out = {
        "control": "C-12 -- per-troll idle-with-work share, fuzz_panel --p4b ON",
        "task": "20260825-dance-cure-candidate-2-swap",
        "bar_pct": BAR_PCT,
        "p4b_gate_applicability": "EVALUABLE" if evaluable else "NOT_EVALUABLE",
        "restated_v5_read": restated,
        "why_not_evaluable": (
            "p4b_gate imports narrate4, whose decoder refuses every non-v4 payload on the version "
            "token, so each telemetry row of each game is a decode error and both arms come back "
            "GATE_UNREADY; and its numerator names branch `H`, which v5 retires by grammar "
            "(narrate5.BRANCH_CODES = 'PLRWNSX', control C-9 'no H'). A version-agnostic decoder "
            "would fix the first and not the second."
            if not evaluable else None),
        "headline": headline,
        "headline_note": (
            "the bar reads 'per-troll idle-with-work share <= 1.5 %'. Under the per-troll reading "
            "the subject arm BREACHES it -- and so does the rule-off arm, which C-1 proved "
            "alpha-identical to the champion, by MORE. Under the corpus-aggregate reading both "
            "pass. The rule strictly improves the number on both readings. Which reading C-12 "
            "means is a ruling, not a measurement, and it is the coordinator's."),
        "accepted_computation_v5_decoded": {
            "what": "p4b_gate.evaluate_rows with narrate5 passed in its narrator slot -- the "
                    "accepted code and the accepted definition, decoder swapped, nothing restated",
            "arms": {name: {"status": arm["status"], "errors": len(arm["errors"]),
                            "games": arm["games"], "map_ids": arm["map_ids"],
                            "both_seats_per_map": arm["both_seats_per_map"],
                            "totals": arm["totals"],
                            "parked_unit_episodes": arm["totals"].get("episodes", 0),
                            "failed_unit_lives": len(arm["failed_units"]),
                            "failed_units": arm["failed_units"],
                            "longest_run_distribution": arm["longest_run_distribution"],
                            "blind_population": arm["blind_population"],
                            "tripwire_45": arm["tripwire_45"]}
                     for name, arm in v5_decoded.items()},
            "differential_ruleoff_to_instrument": v5_compare},
        "accepted_gate": {"module": "claude_1/pipeline/p4b_gate.py (imported via --p4b, not "
                                    "restated)", "arms": applicability,
                          "definition": packet["definition"], "controls": packet["controls"]},
        "decoder_controls": controls,
        "subject": subject,
        "bridge_to_candidate_arm": bridge,
        "restatement": {
            "author": "claude_1; NOT codex_1's accepted P4b definition",
            "definition_faithful": "branch in {H, W} transposed verbatim = W alone, since H is "
                                   "off-grammar in v5",
            "non_moving_R2": "branch in {W, N} -- every turn the unit did not move. NOT an idle "
                             "share: `N` is 'no MOVE this turn' and a unit issuing CHOP/PICK/DROP "
                             "is an `N`. Published with this caveat and never as idleness",
            "idle_with_work_R3": "branch in {W, N} AND `available` CONCRETE AND no progress event "
                                 "that turn (p4b_gate.progress_event, imported). The headline: it "
                                 "is the bar's own words rendered in the v5 grammar",
            "with_work": "the same, restricted to turns whose `available` target is CONCRETE "
                         "(SHACK/BANK/CELL/TREE); the accepted metric is NOT so conditioned, so "
                         "its share is an upper bound on idle-WITH-work",
            "ruling_needed": "which reading the 1.5 % bar governs on a v5 grammar is a definition "
                             "change and the coordinator's to make, not mine",
        },
        "arms": summary,
        "instrument_minus_ruleoff_pct": delta,
        "unit_lives_above_bar": breached,
        "vacuity_notes": notes,
        "panel_verdicts": {"instrument": subj_data["verdict"], "ruleoff": base_data["verdict"]},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")

    for name in ("instrument", "ruleoff"):
        s = summary[name]
        print("  %-10s %d unit lives / %d turns | R1 W %.4f %% | R2 W+N %.4f %% (%d of those N "
              "turns carry a progress event) | R3 idle-with-work %.4f %%, %d unit lives above bar"
              % (name, s["unit_lives"], s["telemetry_turns_graded"],
                 s["corpus_share_definition_faithful_pct"],
                 s["corpus_share_intent_faithful_pct"], s["n_branch_with_progress"],
                 s["corpus_share_idle_with_work_pct"],
                 len(s["unit_lives_above_bar"]["share_idle_with_work_pct"])), flush=True)
    for n in notes:
        print("  " + n, flush=True)
    for name in ("instrument", "ruleoff"):
        h = headline[name]
        print("  HEADLINE %-10s per-troll max %.4f %% | %d of %d unit lives above the bar | "
              "corpus %.4f %% | parked-unit episodes %d | per-troll %s, corpus %s"
              % (name, h["per_troll_max_pct"], h["unit_lives_above_bar"], h["unit_lives"],
                 h["corpus_share_pct"], h["parked_unit_episodes"], h["per_troll_reading"],
                 h["corpus_reading"]), flush=True)
    print("C-12: accepted gate %s; restated v5 read %s (bar <= %.1f %%) -> %s"
          % (out["p4b_gate_applicability"], restated, BAR_PCT, OUT), flush=True)
    return 0 if restated == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GateError as exc:
        print("C-12 ABORTED: %s" % exc, file=sys.stderr)
        sys.exit(2)
    finally:
        for d in SCRATCH:
            shutil.rmtree(d, ignore_errors=True)
