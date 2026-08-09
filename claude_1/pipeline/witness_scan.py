#!/usr/bin/env python3
"""Corpus witness census for the fuzz panel (committed, not scratch).

r2's review asked which repaired rules the 240-game corpus actually
EXERCISES, as opposed to which ones the unit tests pin.  r3 answered it and
found six of eleven unwitnessed; this is the same census, mechanised, so the
answer is measured rather than asserted and can be re-measured after any
corpus bump.

It replays the corpus with an instrumented subclass of `FuzzReferee` that
counts, per game, the situations each repaired rule governs.  It changes no
rule: every override calls `super()` and only observes.

    python3 witness_scan.py --config fuzz-panel-floor-config.json
    python3 witness_scan.py --config fuzz-panel-config.json
"""

from __future__ import annotations

import argparse
import collections
import multiprocessing
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fuzz_panel as fp                                     # noqa: E402

sys.path.insert(0, str(fp.BR2))
import regression_tests as rt                               # noqa: E402

NON_TRAIN = ("MOVE", "HARVEST", "PLANT", "CHOP", "PICK", "DROP", "MINE")
LATE_PHASES = ("DROP", "MINE")
EARLY_PHASES = ("MOVE", "HARVEST", "PLANT", "CHOP", "PICK", "TRAIN")


class WitnessReferee(fp.FuzzReferee):
    """Observes; never decides.  Every override delegates to `super()`."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.w = collections.Counter()

    # -- line-level witnesses ---------------------------------------------
    def apply_two(self, command_line, opp_command_line):
        frags = [" ".join(f.split())
                 for _, _, f in self.split_fragments(command_line)
                 if f.strip()]
        verbs = [f.split()[0].upper() for f in frags]
        seen = set()
        for i, verb in enumerate(verbs):
            if verb in LATE_PHASES and any(v in EARLY_PHASES
                                           for v in verbs[i + 1:]):
                self.w["c4_phase_order_line"] += 1
                break
        for frag, verb in zip(frags, verbs):
            if verb not in NON_TRAIN:
                continue
            tok = frag.split()
            if len(tok) < 2:
                continue
            uid = tok[1]
            if uid in seen:
                self.w["c5_duplicate_unit_command"] += 1
            seen.add(uid)
            unit = self.units.get(int(uid)) if uid.lstrip("-").isdigit() \
                else None
            if unit is not None and unit["player"] == 1:
                self.w["candidate_commands_an_opponent_unit"] += 1
            if verb == "MOVE" and unit is not None and unit["speed"] == 0:
                self.w["speed_zero_move"] += 1
        if verbs.count("TRAIN") > 1:
            self.w["o2_multiple_train_on_one_line"] += 1
        if verbs.count("TRAIN"):
            self.w["train_emitted_line"] += 1

        opp_frags = [f.strip() for f in opp_command_line.split(";")
                     if f.strip()]
        for f in opp_frags:
            self.w["opponent_" + f.split()[0].upper()] += 1
        if opp_frags:
            self.w["opponent_commanded_turn"] += 1
            own_targets = {tuple(f.split()[2:4]) for f in frags
                           if f.split()[0].upper() == "MOVE"
                           and len(f.split()) == 4}
            opp_targets = {tuple(f.split()[2:4]) for f in opp_frags
                           if f.split()[0].upper() == "MOVE"}
            if own_targets & opp_targets:
                self.w["cross_player_move_same_target"] += 1
        self._planted_this_turn = set()
        return super().apply_two(command_line, opp_command_line)

    # -- applier-level witnesses ------------------------------------------
    def _apply_harvest(self, uids):
        before = {uid: sum(self.units[uid]["carry"])
                  for uid in uids if uid in self.units}
        super()._apply_harvest(uids)
        for uid, was in before.items():
            got = sum(self.units[uid]["carry"]) - was
            if got >= 2:
                self.w["multi_round_harvest"] += 1

    def _apply_plant(self, entries):
        super()._apply_plant(entries)
        self._planted_this_turn = {self.units[uid]["cell"]
                                   for uid, _ in entries
                                   if uid in self.units}

    def _apply_chop(self, uids, allowed_cells):
        for uid in uids:
            u = self.units.get(uid)
            if u is None:
                continue
            if (u["cell"] in getattr(self, "_planted_this_turn", ())
                    and u["cell"] not in allowed_cells):
                self.w["chop_snapshot_protected_a_fresh_tree"] += 1
        super()._apply_chop(uids, allowed_cells)

    def _apply_pick(self, entries):
        for uid, _ in entries:
            u = self.units.get(uid)
            if u is not None and u["cell"] == self.shacks[u["player"]]:
                self.w["pick_from_the_shack_cell_itself"] += 1
        super()._apply_pick(entries)

    def _apply_drop(self, uids):
        for uid in uids:
            u = self.units.get(uid)
            if u is not None and u["cell"] == self.shacks[u["player"]]:
                self.w["drop_from_the_shack_cell_itself"] += 1
        super()._apply_drop(uids)


def _scan(job):
    spec = job["spec"]
    plants = {}
    for k, x, y, size, health, fruits, cd in spec["plants"]:
        plants[(x, y)] = {"kind": k, "size": size, "health": health,
                          "fruits": fruits, "cd": cd}
    units = {}
    for row in spec["units"]:
        uid, player, x, y, speed, cap, harvest, chop = row[:8]
        units[uid] = {"player": player, "cell": (x, y), "speed": speed,
                      "cap": cap, "harvest": harvest, "chop": chop,
                      "carry": list(row[8:14])}
    ref = WitnessReferee(spec["rows"], spec["inventory"], plants, units,
                         spec["profile"])
    rt.run_binary_custom(Path(job["candidate"]), ref, job["turns"])
    w = dict(ref.w)
    for kind, n in ref.error_counts.items():
        w["trust_boundary_" + kind] = n
    w["successful_train"] = len(ref.spawn_events())
    return w


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="witness_scan")
    ap.add_argument("--config", required=True)
    args = ap.parse_args(argv)
    cfg = fp.load_config(Path(args.config))
    with tempfile.TemporaryDirectory(prefix="witness-") as workdir:
        candidate = fp.compile_bot(cfg, "candidate", Path(workdir))
        parent = fp.compile_bot(cfg, "parent", Path(workdir))
        jobs = fp.build_jobs(cfg, candidate, parent)
        with multiprocessing.get_context("fork").Pool(
                min(8, multiprocessing.cpu_count())) as pool:
            per_game = pool.map(_scan, jobs)

    # Every rule the census answers for, so a rule with NO witness is a
    # printed zero rather than a missing row.
    total = collections.Counter({k: 0 for k in (
        "c4_phase_order_line", "c5_duplicate_unit_command",
        "o2_multiple_train_on_one_line", "train_emitted_line",
        "successful_train", "candidate_commands_an_opponent_unit",
        "speed_zero_move", "multi_round_harvest",
        "chop_snapshot_protected_a_fresh_tree",
        "pick_from_the_shack_cell_itself", "drop_from_the_shack_cell_itself",
        "cross_player_move_same_target", "opponent_commanded_turn",
        "opponent_MOVE", "opponent_HARVEST", "opponent_CHOP", "opponent_DROP",
        "trust_boundary_" + fp.ERROR_UNSUPPORTED_VERB,
        "trust_boundary_" + fp.ERROR_MALFORMED)})
    games = collections.Counter()
    for w in per_game:
        for k, v in w.items():
            total[k] += v
            if v:
                games[k] += 1
    print("witness census: %s (%s run, %d games)"
          % (cfg["corpus_version"], cfg["run_identity"], len(per_game)))
    print()
    print("| witnessed situation | occurrences | games (of %d) |"
          % len(per_game))
    print("|---|---|---|")
    for k in sorted(set(total) | set(games)):
        print("| `%s` | %d | %d |" % (k, total[k], games[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
