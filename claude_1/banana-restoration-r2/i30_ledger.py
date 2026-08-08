#!/usr/bin/env python3
"""I-30 measurement ledger: deterministic opponent shadow referee.

Authoritative specification:
  chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md
  (branch agent/chatgpt_1, artifact_commit cad16c4d), sections 3, 5 and 6.

Scope: measurement only. This module reads recorded traces (the exact stdin
protocol already parsed by `trace_detectors.TraceParser`) and reconstructs the
opponent's score-bearing resource flow with source provenance. It never
touches a bot, candidate, parent, gate, host game, submission or Arena state.

Why a shadow ledger rather than referee instrumentation: the offline corpus is
transcripts + command streams. The transcript is a full observation of both
players (both inventories, every plant, every unit with its carry vector), so
opponent acquisition, planting, banking and TRAIN are all derivable by exact
state differencing. Anything not derivable stays `unknown` and fails closed.

Engine rules mirrored (rust/src/game/engine.rs, cross-checked against
docs/mechanics.md and cgauto/mechanics_rederivation_audit.py):

  recompute_scores : score = PLUM+LEMON+APPLE+BANANA + 4*WOOD  (IRON scores 0)
  near_shack       : |ux - sx| + |uy - sy| <= 1
  apply_drop       : whole carry vector moves into inventories[player]
  apply_pick       : one unit moves inventories[player] -> carry (a bank
                     WITHDRAWAL, which spec sec. 5.3 does not name; see
                     "Ambiguity resolutions" below)
  training_cost    : n + stat^2 in PLUM/LEMON/APPLE/IRON, BANANA and WOOD
                     free; IRON only charged when the map has iron terrain

Governing ruling (schema version 2):
  chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md (branch agent/chatgpt_1).

  D1. Gross deposits, bank withdrawals and net bank flow are three SEPARATELY
      named quantities. `dep_*` / `gdep_*` are gross, matching the spec's
      frozen term; `wdr_*` are withdrawals; `net_bank_flow_*` is the
      difference and is what the exact conservation identity uses.
  D5. Every attributed transition must have a unique derivation from the
      recorded state. Where it does not, the affected atoms become `unknown`
      and the pair is `GATE_UNREADY`. Determinism is not identifiability:
      no unit-id ordering, FIFO bank order or other tie-break may turn an
      observationally non-identifiable allocation into claimed truth.

Ambiguity resolutions (the spec and the ruling are authoritative; these fill
gaps they leave, and every one is restated in i30-implementation-2026-08-08.md):

  R1. Bank withdrawals. `apply_pick` removes score-bearing atoms from the same
      inventory that `recompute_scores` sums, so the spec's original gross-only
      identity cannot close for any opponent that PICKs. Per ruling D1 the
      identity uses NET BANK FLOW, and gross deposits and gross withdrawals
      remain separately reported mandatory diagnostics.
  R2. Initial bank stock and initial unit carry are map-seeded, so they are
      classified `natural` (spec sec. 5.2: "A map-seeded tree or plant is
      natural"). They are identical across an exact pair, so they cancel in
      every paired delta.
  R3. Indistinguishable atoms of one resource are held as a multiset (spec
      sec. 5.1). A take of the WHOLE multiset, or of a multiset whose atoms
      all share one source class, is uniquely determined. A PARTIAL take from
      a mixed-class multiset is NOT: FIFO would merely be a tie-break, so the
      whole multiset is relabelled `unknown` and the pair fails closed.
  R4. A plant's creator is the sole player occupying its cell in the
      post-state. Absent or mixed occupancy -> `unknown`, never guessed. An
      asset can only source an acquisition if it actually stood on the unit's
      cell in the pre-state, so a long-dead asset cannot launder a later atom.
  R5. Deposits and withdrawals of one resource in one turn are constrained by
      `budget = inventory_delta + TRAIN_bill`. The feasible withdrawal count
      is the integer interval [max(0,-budget), min(pick_cand, drop_cand-budget)].
      A single feasible point is identifiable; two or more are not, and every
      atom that could have moved -- both bank side and carry side -- is
      relabelled `unknown`. An EMPTY interval is not an ambiguity but an
      unexplained observation: nothing is relabelled and the conservation
      residual reports it.
  R6. TRAIN is derived independently from unit spawns and engine
      `training_cost`, never as the arithmetic remainder -- otherwise the
      conservation residual would be zero by construction and could never bite.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trace_detectors as td  # noqa: E402  (real transcript/command parser)

# I-30 result/ledger schema version.
#   1 -- gross-only `DEP_*` (spec sec. 6 as written), then the withdrawal
#        correction that silently redefined `DEP_*` as net; rejected by the
#        D1 ruling.
#   2 -- gross deposits (`gdep_*` / `dep_*`), bank withdrawals (`wdr_*`) and
#        net bank flow (`net_bank_flow_*`) separately named; identity on net;
#        non-identifiable attribution fails closed as `unknown` (D5).
SCHEMA_VERSION = 2

ITEM_NAMES = td.ITEM_NAMES
PLUM, LEMON, APPLE, BANANA, IRON, WOOD = td.PLUM, td.LEMON, td.APPLE, \
    td.BANANA, td.IRON, td.WOOD

# spec sec. 5.1 frozen score weights (engine.rs recompute_scores / WOOD_POINTS)
SCORE_WEIGHT = (1, 1, 1, 1, 0, 4)

SOURCE_CLASSES = ("ours", "opponent", "natural", "unknown")
OPPONENT_PLAYER = 1
OWN_PLAYER = 0

FRUIT_KINDS = {"PLUM": PLUM, "LEMON": LEMON, "APPLE": APPLE, "BANANA": BANANA}


def score_of(inventory):
    """Score-equivalent value of a 6-vector (engine.rs recompute_scores)."""
    return sum(int(inventory[k]) * SCORE_WEIGHT[k] for k in range(6))


def training_cost(n, talents, iron_present):
    """Charged TRAIN bill (engine.rs training_cost + apply_train `pay` set).

    `n` is the trainer's unit count before the spawn; `talents` is
    (move_speed, carry_cap, harvest_power, chop_power). IRON is only deducted
    when the map contains iron terrain.
    """
    ms, cc, hp, cp = talents
    cost = [0] * 6
    cost[PLUM] = n + ms * ms
    cost[LEMON] = n + cc * cc
    cost[APPLE] = n + hp * hp
    if iron_present:
        cost[IRON] = n + cp * cp
    return cost


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _map_digest(smap):
    return sha256_text(_canonical({
        "width": smap.width, "height": smap.height,
        "walkable": sorted(list(smap.walkable)),
        "shacks": [list(c) for c in smap.shacks],
        "iron": sorted(list(smap.iron)), "water": sorted(list(smap.water)),
    }))


def _state_digest(state):
    return sha256_text(_canonical({
        "inventories": state.inventories,
        "plants": sorted([p.kind, list(p.cell), p.size, p.health, p.fruits,
                          p.cooldown] for p in state.plants),
        "units": sorted([u.id, u.player, list(u.cell), u.speed, u.capacity,
                         u.harvest_power, u.chop_power, list(u.carry)]
                        for u in state.units),
    }))


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class RunRecord:
    """One side of a pair: transcript + command stream + identity hashes.

    Derived identity fields (map / initial state / command stream / transcript
    digests) are computed here so a fixture cannot silently declare a pair
    exact while feeding two different worlds.
    """

    def __init__(self, run_id, transcript_text, commands_text, identity=None,
                 banana_mechanism_claimed=False):
        self.run_id = run_id
        self.transcript_text = transcript_text
        self.commands_text = commands_text
        self.banana_mechanism_claimed = bool(banana_mechanism_claimed)
        self.trace = td.build_trace(transcript_text, commands_text)

        ident = dict(identity or {})
        ident.setdefault("map_sha256", _map_digest(self.trace.smap))
        ident.setdefault("initial_state_sha256",
                         _state_digest(self.trace.state(1)))
        ident.setdefault("command_stream_sha256", sha256_text(commands_text))
        ident.setdefault("transcript_sha256", sha256_text(transcript_text))
        ident.setdefault("seat", OWN_PLAYER)
        self.identity = ident
        self._ledger = None

    @property
    def ledger(self):
        if self._ledger is None:
            self._ledger = build_run_ledger(self)
        return self._ledger

    def banana_commands(self):
        """[(turn, raw)] for every own PLANT/PICK naming BANANA (spec sec. 4)."""
        out = []
        for t in range(1, self.trace.T + 1):
            for cmd in self.trace.cmds(t).all:
                if cmd.verb in ("PLANT", "PICK") and "BANANA" in cmd.raw.upper():
                    out.append((t, cmd.raw.strip()))
        return out

    def command_lines(self):
        return [line.strip()
                for line in self.commands_text.split("\n")][:self.trace.T]


# --------------------------------------------------------------------------
# Identifiability predicates (ruling D5)
#
# Each one answers a single question: "is this allocation UNIQUELY determined
# by the recorded state?" -- never "which allocation shall I pick?". They are
# module-level and resolved through the module namespace so that a mutation
# control can revert them to the old unconditional tie-break
# (`lambda *a: True`) and watch the adversarial fixtures stop failing closed.
# See test_i30_invariant.TestD5MutationRevertedTieBreakIsCaught.
# --------------------------------------------------------------------------

def split_is_identifiable(lo, hi):
    """Is the deposit/withdrawal split of one resource-turn unique?

    `lo`/`hi` bound the feasible withdrawal count. Exactly one feasible
    integer means one derivation; two or more means the classes that moved
    are not observable, however deterministically we might choose between
    them.
    """
    return hi <= lo


def partial_take_is_identifiable(atoms, n):
    """Is removing `n` atoms from this multiset class-determined?

    Taking none, or taking all of them, determines the classes removed. So
    does taking from a multiset whose atoms all carry one source class. Any
    other partial take would be decided by FIFO order, which the engine does
    not define and the transcript does not record.
    """
    if n <= 0 or n >= len(atoms):
        return True
    return len({a["source_class"] for a in atoms}) <= 1


def assignment_is_identifiable(total, capacity, contributors):
    """Is the allocation of `total` across `contributors` units unique?

    With one contributing unit, or when every candidate unit-atom moved
    (`total == capacity`), or when none did, the assignment is forced.
    Otherwise which unit's cargo moved is a unit-id tie-break.
    """
    if contributors <= 1:
        return True
    return total == 0 or total == capacity


def _atom(resource, source_class, source_creator, source_asset_id,
          source_event_id, acquired_turn, acquired_verb):
    return {
        "resource_kind": ITEM_NAMES[resource],
        "resource": resource,
        "source_class": source_class,
        "source_creator": source_creator,
        "source_asset_id": source_asset_id,
        "source_event_id": source_event_id,
        "acquired_turn": acquired_turn,
        "acquired_verb": acquired_verb,
    }


class RunLedger:
    """Per-run opponent accounting (spec sec. 5 / 6; ruling D1 / D5).

    Three separate quantities per source class, never substituted for one
    another:

        gdep[c]            gross score-equivalent deposits into the bank
        wdr[c]             gross score-equivalent withdrawals from the bank
        net_bank_flow(c)   gdep[c] - wdr[c], the terminal-score contribution
    """

    def __init__(self, run_id, events, gdep, wdr, lost, train_spend,
                 unknown_atoms, ambiguities, initial_score, terminal_score,
                 terminal_turn, counts, first_productive_turn,
                 productive_turns, opp_live_assets, direct_interactions):
        self.run_id = run_id
        self.events = events
        self.gdep = dict(gdep)
        self.wdr = dict(wdr)
        self.lost = dict(lost)
        self.train_spend = train_spend
        self.unknown_atoms = unknown_atoms
        self.ambiguities = list(ambiguities)
        self.initial_score = initial_score
        self.terminal_score = terminal_score
        self.terminal_turn = terminal_turn
        self.counts = dict(counts)
        self.first_productive_turn = first_productive_turn
        self.productive_turns = productive_turns
        self.opp_live_assets = opp_live_assets
        self.direct_interactions = direct_interactions

    def net_bank_flow(self, source_class):
        """NBF_c = GDEP_c - WDR_c (ruling D1)."""
        return self.gdep[source_class] - self.wdr[source_class]

    @property
    def gdep_total(self):
        return sum(self.gdep[c] for c in SOURCE_CLASSES)

    @property
    def wdr_total(self):
        return sum(self.wdr[c] for c in SOURCE_CLASSES)

    @property
    def net_bank_flow_total(self):
        return self.gdep_total - self.wdr_total

    @property
    def identifiable(self):
        """False iff any transition's provenance was not uniquely derivable."""
        return not self.ambiguities

    @property
    def residual(self):
        """Per-run conservation residual; must be exactly 0 (spec sec. 6).

        Uses NET bank flow, per ruling D1.
        """
        return ((self.terminal_score - self.initial_score)
                - (self.net_bank_flow_total - self.train_spend))

    def to_json(self):
        out = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "initial_score": self.initial_score,
            "terminal_score": self.terminal_score,
            "terminal_turn": self.terminal_turn,
            "train_spend": self.train_spend,
            "unknown_atoms": self.unknown_atoms,
            "identifiable": self.identifiable,
            "ambiguity_count": len(self.ambiguities),
            "ambiguities": [dict(a) for a in self.ambiguities],
            "residual": self.residual,
            "gdep_total": self.gdep_total,
            "wdr_total": self.wdr_total,
            "net_bank_flow_total": self.net_bank_flow_total,
            "first_productive_turn": self.first_productive_turn,
            "productive_turns": self.productive_turns,
            "opp_live_assets": self.opp_live_assets,
            "direct_interactions": self.direct_interactions,
            "event_count": len(self.events),
            "event_ids": [e["event_id"] for e in self.events],
        }
        for c in SOURCE_CLASSES:
            # `dep_*` keeps the spec's frozen term name and its GROSS meaning
            # (ruling D1 change 1); `gdep_*` says so in the name.
            out["dep_" + c] = self.gdep[c]
            out["gdep_" + c] = self.gdep[c]
            out["wdr_" + c] = self.wdr[c]
            out["net_bank_flow_" + c] = self.net_bank_flow(c)
            out["lost_" + c] = self.lost[c]
        for k, v in self.counts.items():
            out[k] = v
        return out


def build_run_ledger(record):
    """Reconstruct the opponent's score-bearing flow from a recorded trace."""
    tr = record.trace
    smap = tr.smap
    opp_shack = smap.shacks[OPPONENT_PLAYER]
    iron_present = bool(smap.iron)
    T = tr.T

    events = []
    seq = [0]

    def emit(**kw):
        seq[0] += 1
        kw["event_id"] = "%s-e%04d" % (record.run_id, seq[0])
        events.append(kw)
        return kw["event_id"]

    gdep = {c: 0 for c in SOURCE_CLASSES}
    wdr = {c: 0 for c in SOURCE_CLASSES}
    lost = {c: 0 for c in SOURCE_CLASSES}
    counts = {"plant_events": 0, "harvest_events": 0, "chop_events": 0,
              "pick_events": 0, "drop_events": 0, "train_events": 0,
              "mine_events": 0, "loss_events": 0, "deposit_atoms": 0,
              "withdraw_atoms": 0, "ambiguity_events": 0}
    train_spend = 0
    unknown_atoms = [0]
    ambiguities = []
    direct_interactions = 0
    productive_turns = 0
    first_productive_turn = None

    st1 = tr.state(1)

    # --- asset provenance registry (spec sec. 5.2) -------------------------
    assets = {}
    for p in st1.plants:
        assets[p.cell] = {
            "asset_id": "a-nat-%d-%d" % p.cell, "kind": p.kind,
            "source_class": "natural", "source_creator": "natural",
            "seed_source_class": "natural", "created_turn": 0,
        }

    # --- initial bank / carry stock (R2) ----------------------------------
    bank = {k: deque() for k in range(6)}
    for k in range(6):
        for _ in range(st1.inventories[OPPONENT_PLAYER][k]):
            bank[k].append(_atom(k, "natural", "natural", "initial-bank",
                                 None, 0, "INITIAL"))
    carry = {}
    for u in st1.units:
        if u.player != OPPONENT_PLAYER:
            continue
        carry[u.id] = {k: deque() for k in range(6)}
        for k in range(6):
            for _ in range(u.carry[k]):
                carry[u.id][k].append(_atom(k, "natural", "natural",
                                            "initial-carry", None, 0,
                                            "INITIAL"))

    def new_unknown(k, turn, verb):
        unknown_atoms[0] += 1
        return _atom(k, "unknown", "unknown", None, None, turn, verb)

    # ---- fail-closed machinery (ruling D5) --------------------------------

    def record_ambiguity(reason, turn, resource=None, detail=None):
        """One non-identifiable allocation. Any of these -> GATE_UNREADY."""
        amb = {"turn": turn, "reason": reason, "resource": resource,
               "detail": detail}
        ambiguities.append(amb)
        counts["ambiguity_events"] += 1
        emit(kind="AMBIGUITY", turn=turn, reason=reason, resource=resource,
             detail=detail)
        return amb

    def poison(atoms):
        """Relabel a whole multiset `unknown`.

        Used when the recorded state does not determine which atoms of the
        multiset moved: the classes of the atoms that left AND of the atoms
        that stayed are equally undetermined, so neither may keep a claimed
        class.
        """
        n = 0
        for a in atoms:
            if a["source_class"] != "unknown":
                a["source_class"] = "unknown"
                a["source_creator"] = "unknown"
                a["non_identifiable"] = True
                unknown_atoms[0] += 1
                n += 1
        return n

    def take(slot, k, n, turn, verb):
        """Remove `n` atoms of kind `k`, failing closed on a mixed partial take.

        FIFO is used only to order an ALREADY identifiable take; where the
        take is not identifiable the multiset is relabelled `unknown` first,
        so the order cannot decide anything (ruling D5).
        """
        atoms = slot[k]
        if not partial_take_is_identifiable(list(atoms), n):
            record_ambiguity("class_composition", turn, ITEM_NAMES[k],
                             "%d of %d atoms, classes %s"
                             % (n, len(atoms),
                                sorted({a["source_class"] for a in atoms})))
            poison(atoms)
        out = []
        for _ in range(n):
            out.append(atoms.popleft() if atoms else new_unknown(k, turn, verb))
        return out

    for t in range(1, T):
        s0, s1 = tr.state(t), tr.state(t + 1)
        inv_prev = s0.inventories[OPPONENT_PLAYER]
        inv_next = s1.inventories[OPPONENT_PLAYER]
        turn_productive = False

        # ---- TRAIN, derived independently from unit spawns (R6) ----------
        prev_ids = {u.id for u in s0.units if u.player == OPPONENT_PLAYER}
        n_before = len(prev_ids)
        train_bill = [0] * 6
        for u in sorted((u for u in s1.units
                         if u.player == OPPONENT_PLAYER and u.id not in prev_ids),
                        key=lambda u: u.id):
            cost = training_cost(n_before, (u.speed, u.capacity,
                                            u.harvest_power, u.chop_power),
                                 iron_present)
            n_before += 1
            train_spend += score_of(cost)
            counts["train_events"] += 1
            turn_productive = True
            for k in range(6):
                train_bill[k] += cost[k]
                # the TRAIN bill is class-agnostic for the identity, but the
                # atoms it consumes still leave the bank, so the take must be
                # identifiable like any other (ruling D5)
                take(bank, k, min(cost[k], len(bank[k])), t, "TRAIN")
            emit(kind="TRAIN", turn=t, unit=u.id, cost=list(cost),
                 score=score_of(cost), talents=[u.speed, u.capacity,
                                                u.harvest_power, u.chop_power],
                 roster_before=n_before - 1)
            carry[u.id] = {k: deque() for k in range(6)}
            for k in range(6):
                for _ in range(u.carry[k]):
                    carry[u.id][k].append(new_unknown(k, t, "SPAWN"))

        # ---- new assets (spec sec. 5.2, R4) ------------------------------
        assets_prev = dict(assets)
        prev_cells = {p.cell for p in s0.plants}
        new_plants = {}
        for p in s1.plants:
            if p.cell in prev_cells:
                continue
            occupants = [u for u in s1.units if u.cell == p.cell]
            players = {u.player for u in occupants}
            if len(players) == 1:
                who = players.pop()
                klass = "ours" if who == OWN_PLAYER else "opponent"
                creator = "player %d" % who
            else:
                klass, creator, who = "unknown", "unknown", None
            assets[p.cell] = {
                "asset_id": "a-%s-%d-%d-t%d" % (klass, p.cell[0], p.cell[1], t),
                "kind": p.kind, "source_class": klass,
                "source_creator": creator, "seed_source_class": None,
                "created_turn": t,
            }
            new_plants[p.cell] = (p, who)

        # ---- movers and per-unit carry deltas -----------------------------
        movers = []
        for u0 in sorted((u for u in s0.units if u.player == OPPONENT_PLAYER),
                         key=lambda u: u.id):
            u1 = s1.unit(u0.id)
            if u1 is None or u1.player != OPPONENT_PLAYER:
                movers.append((u0, None, False))
                continue
            movers.append((u0, u1, _manhattan(u1.cell, opp_shack) <= 1))

        # A successful own PLANT consumes exactly one fruit of the planted
        # kind from the planter's carry, and the planter is the cell's sole
        # occupant (otherwise the asset class is already `unknown`). That
        # decrease is therefore explained and is not a bank-flow candidate.
        seed_use = {}
        for (u0, u1, _near) in movers:
            if u1 is None:
                continue
            planted = new_plants.get(u1.cell)
            if planted is None or planted[1] != OPPONENT_PLAYER:
                continue
            if planted[0].kind not in FRUIT_KINDS:
                continue
            k = FRUIT_KINDS[planted[0].kind]
            if u1.carry[k] < u0.carry[k]:
                seed_use[u0.id] = k

        # ---- inventory budget split (R5, ruling D5) -----------------------
        drop_by_unit = [dict() for _ in range(6)]
        pick_by_unit = [dict() for _ in range(6)]
        for (u0, u1, near) in movers:
            if u1 is None or not near:
                continue
            for k in range(6):
                d = u1.carry[k] - u0.carry[k]
                if d < 0:
                    out = -d - (1 if seed_use.get(u0.id) == k else 0)
                    if out > 0:
                        drop_by_unit[k][u0.id] = out
                elif d > 0:
                    pick_by_unit[k][u0.id] = d

        deposits = [0] * 6
        withdrawals = [0] * 6
        for k in range(6):
            drop_cand = sum(drop_by_unit[k].values())
            pick_cand = sum(pick_by_unit[k].values())
            budget = (inv_next[k] - inv_prev[k]) + train_bill[k]

            # every feasible withdrawal count w satisfies
            #   deposits = budget + w,  0 <= w <= pick_cand,
            #   0 <= budget + w <= drop_cand
            lo = max(0, -budget)
            hi = min(pick_cand, drop_cand - budget)
            w = min(pick_cand, max(0, drop_cand - budget))
            withdrawals[k] = w
            deposits[k] = max(0, min(drop_cand, budget + w))

            if hi < lo:
                # No allocation explains the observation, so there is nothing
                # to choose between: this is an unexplained transition, not a
                # non-identifiable one. The conservation residual reports it.
                continue

            ambiguous = False
            if not split_is_identifiable(lo, hi):
                record_ambiguity("deposit_withdrawal_split", t, ITEM_NAMES[k],
                                 "feasible withdrawals %d..%d" % (lo, hi))
                ambiguous = True
            if not assignment_is_identifiable(deposits[k], drop_cand,
                                              len(drop_by_unit[k])):
                record_ambiguity("deposit_unit_assignment", t, ITEM_NAMES[k],
                                 "%d of %d across %d units"
                                 % (deposits[k], drop_cand,
                                    len(drop_by_unit[k])))
                ambiguous = True
            if not assignment_is_identifiable(w, pick_cand,
                                              len(pick_by_unit[k])):
                record_ambiguity("withdrawal_unit_assignment", t,
                                 ITEM_NAMES[k],
                                 "%d of %d across %d units"
                                 % (w, pick_cand, len(pick_by_unit[k])))
                ambiguous = True

            if ambiguous:
                # every atom that could have crossed the tent threshold this
                # turn, on either side, loses its claimed class
                poison(bank[k])
                for uid in set(drop_by_unit[k]) | set(pick_by_unit[k]):
                    poison(carry.setdefault(
                        uid, {j: deque() for j in range(6)})[k])

        # ---- per-unit atom flow ------------------------------------------
        for (u0, u1, near) in movers:
            uid = u0.id
            slots = carry.setdefault(uid, {k: deque() for k in range(6)})
            if u1 is None:
                for k in range(6):
                    for a in take(slots, k, len(slots[k]), t, "LOSS"):
                        lost[a["source_class"]] += SCORE_WEIGHT[k]
                        counts["loss_events"] += 1
                        emit(kind="LOSS", turn=t, unit=uid, reason="unit_gone",
                             resource=ITEM_NAMES[k],
                             source_class=a["source_class"])
                continue

            cell = u1.cell
            planted = new_plants.get(cell)
            seed_pending = (planted is not None
                            and planted[1] == OPPONENT_PLAYER)
            # An asset can only be the source of an acquisition if it was
            # actually standing on the unit's cell in the pre-state. The
            # registry is never pruned, so consulting it alone would let a
            # long-dead plant launder a later untagged atom (R4).
            src_asset = (assets_prev.get(cell)
                         if s0.plant_at(cell) is not None else None)
            banked_this_turn = False

            for k in range(6):
                d = u1.carry[k] - u0.carry[k]

                if d < 0:
                    out = -d
                    # 1. seed consumed by a successful own PLANT
                    if seed_pending and planted[0].kind in FRUIT_KINDS \
                            and FRUIT_KINDS[planted[0].kind] == k and out > 0:
                        a = take(slots, k, 1, t, "SEED")[0]
                        assets[cell]["seed_source_class"] = a["source_class"]
                        counts["plant_events"] += 1
                        turn_productive = True
                        seed_pending = False
                        out -= 1
                        emit(kind="PLANT", turn=t, unit=uid, cell=list(cell),
                             kind_planted=planted[0].kind,
                             asset_id=assets[cell]["asset_id"],
                             asset_source_class=assets[cell]["source_class"],
                             seed_source_class=a["source_class"])
                    # 2. banked
                    if near and out > 0 and deposits[k] > 0:
                        n = min(out, deposits[k])
                        deposits[k] -= n
                        for a in take(slots, k, n, t, "DROP"):
                            gdep[a["source_class"]] += SCORE_WEIGHT[k]
                            bank[k].append(a)
                            counts["deposit_atoms"] += 1
                            emit(kind="DEPOSIT", turn=t, unit=uid,
                                 resource=ITEM_NAMES[k],
                                 score=SCORE_WEIGHT[k],
                                 source_class=a["source_class"],
                                 source_creator=a["source_creator"],
                                 source_asset_id=a["source_asset_id"],
                                 source_event_id=a["source_event_id"])
                        # one DROP moves the whole carry vector (apply_drop),
                        # so a unit-turn is a single DROP event however many
                        # resource kinds it contained
                        if not banked_this_turn:
                            counts["drop_events"] += 1
                            banked_this_turn = True
                        turn_productive = True
                        out -= n
                    # 3. anything else left the unit without banking
                    for a in take(slots, k, out, t, "LOSS"):
                        lost[a["source_class"]] += SCORE_WEIGHT[k]
                        counts["loss_events"] += 1
                        emit(kind="LOSS", turn=t, unit=uid, reason="uncarried",
                             resource=ITEM_NAMES[k],
                             source_class=a["source_class"])

                elif d > 0:
                    inn = d
                    # 1. withdrawn from the own bank (apply_pick)
                    if near and withdrawals[k] > 0:
                        n = min(inn, withdrawals[k])
                        withdrawals[k] -= n
                        for a in take(bank, k, n, t, "PICK"):
                            wdr[a["source_class"]] += SCORE_WEIGHT[k]
                            slots[k].append(a)
                            counts["withdraw_atoms"] += 1
                            emit(kind="WITHDRAW", turn=t, unit=uid,
                                 resource=ITEM_NAMES[k],
                                 score=SCORE_WEIGHT[k],
                                 source_class=a["source_class"])
                        # apply_pick moves exactly one item per command
                        counts["pick_events"] += n
                        inn -= n
                    # 2. acquired from an asset on the unit's cell
                    for _ in range(inn):
                        if src_asset is not None:
                            verb = "CHOP" if k == WOOD else "HARVEST"
                            counts["chop_events" if k == WOOD
                                   else "harvest_events"] += 1
                            if src_asset["source_class"] == "ours":
                                direct_interactions += 1
                            a = _atom(k, src_asset["source_class"],
                                      src_asset["source_creator"],
                                      src_asset["asset_id"], None, t, verb)
                        elif k == IRON and cell in smap.iron:
                            counts["mine_events"] += 1
                            a = _atom(k, "natural", "natural",
                                      "iron-%d-%d" % cell, None, t, "MINE")
                        else:
                            verb = "PICK"
                            a = new_unknown(k, t, verb)
                        slots[k].append(a)
                        turn_productive = True
                        a["source_event_id"] = emit(
                            kind="ACQUIRE", turn=t, unit=uid,
                            cell=list(cell), resource=ITEM_NAMES[k],
                            verb=a["acquired_verb"],
                            source_class=a["source_class"],
                            source_creator=a["source_creator"],
                            source_asset_id=a["source_asset_id"])

        if turn_productive:
            productive_turns += 1
            if first_productive_turn is None:
                first_productive_turn = t

    terminal = tr.state(T)
    opp_live_assets = sum(
        1 for p in terminal.plants
        if assets.get(p.cell, {}).get("source_class") == "opponent")

    return RunLedger(
        run_id=record.run_id, events=events, gdep=gdep, wdr=wdr,
        lost=lost, train_spend=train_spend, unknown_atoms=unknown_atoms[0],
        ambiguities=ambiguities,
        initial_score=score_of(st1.inventories[OPPONENT_PLAYER]),
        terminal_score=score_of(terminal.inventories[OPPONENT_PLAYER]),
        terminal_turn=T, counts=counts,
        first_productive_turn=first_productive_turn,
        productive_turns=productive_turns, opp_live_assets=opp_live_assets,
        direct_interactions=direct_interactions)
