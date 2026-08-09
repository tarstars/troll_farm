#!/usr/bin/env python3
"""I-30 bite-test fixtures (spec sec. 10).

Every fixture is a real stdin-protocol transcript plus a real command stream,
so it executes through `trace_detectors.TraceParser` / `CommandParser` (the
production parser), then through the I-30 shadow ledger and analyzer.

Map (11x9), own tent '0' at (4,3), opponent shack '1' at (8,6), no water,
no iron:

      0123456789A
    0 ...........
    1 ...........
    2 ...........
    3 ....0......
    4 ...........
    5 ...........
    6 ........1..
    7 ...........
    8 ...........

Own tent ring cells include the door (4,2) used for every legal own BANANA
plant (D-5 requires cheby(cell, tent) == 1).
Opponent bank cells are Manhattan distance <= 1 from (8,6): (7,6), (8,5),
(9,6), (8,7) and (8,6) itself (engine.rs `near_shack`).

Nothing here is a candidate, parent, bot, submission or Arena artifact: these
are measurement fixtures only.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i30_ledger as ledger  # noqa: E402

MAP_HEADER = "11 9"
MAP_ROWS = [
    "...........",
    "...........",
    "...........",
    "....0......",
    "...........",
    "...........",
    "........1..",
    "...........",
    "...........",
]

OWN_TENT = (4, 3)
OPP_SHACK = (8, 6)
OWN_DOOR = (4, 2)          # cheby == 1 from own tent -> legal D-5 plant slot
OPP_BANK = (7, 6)          # Manhattan == 1 from the opponent shack

# Shared identity block (spec sec. 3). Every field except the three
# PAIR_VARIABLE_FIELDS is identical across a pair by construction.
BASE_IDENTITY = {
    "seat": 0,
    "opponent_source_sha256": "op" + "0" * 62,
    "opponent_binary_sha256": "ob" + "0" * 62,
    "opponent_config_sha256": "oc" + "0" * 62,
    "engine_sha256": "en" + "0" * 62,
    "rng_seed": 424242,
    "turn_cap": 300,
    "termination_rule": "turn_cap_or_no_units",
    "toolchain_sha256": "tc" + "0" * 62,
    "harness_sha256": "ha" + "0" * 62,
    "analyzer_config_sha256": "ac" + "0" * 62,
    "detector_config_sha256": "dc" + "0" * 62,
}

CANDIDATE_BOT = {
    "bot_source_sha256": "ca" + "0" * 62,
    "bot_binary_sha256": "cb" + "0" * 62,
}
PARENT_BOT = {
    "bot_source_sha256": "pa" + "0" * 62,
    "bot_binary_sha256": "pb" + "0" * 62,
}


# --------------------------------------------------------------------------
# transcript builders (exact stdin protocol)
# --------------------------------------------------------------------------

def C(**kw):
    """Carry / inventory 6-vector: C(apple=2, banana=1)."""
    v = [0] * 6
    for name, n in kw.items():
        v[ledger.ITEM_NAMES.index(name.upper())] = n
    return v


def U(uid, player, cell, carry=None, speed=1, cap=4, hp=1, cp=1):
    return " ".join(str(x) for x in
                    [uid, player, cell[0], cell[1], speed, cap, hp, cp]
                    + list(carry or [0] * 6))


def P(kind, cell, size=1, health=3, fruits=0, cooldown=4):
    return "%s %d %d %d %d %d %d" % (kind, cell[0], cell[1], size, health,
                                     fruits, cooldown)


def B(units, plants=(), inv0=None, inv1=None):
    """One turn block."""
    lines = [" ".join(str(x) for x in (inv0 or [0] * 6)),
             " ".join(str(x) for x in (inv1 or [0] * 6)),
             str(len(plants))]
    lines.extend(plants)
    lines.append(str(len(units)))
    lines.extend(units)
    return lines


def transcript_of(blocks):
    body = [MAP_HEADER] + MAP_ROWS
    for blk in blocks:
        body.extend(blk)
    return "\n".join(body) + "\n"


# --------------------------------------------------------------------------
# Harness command-execution declaration (review I30R2-8)
#
# These fixtures stand in for the REPAIRED referee (`fuzz-panel/2-train`),
# which implements TRAIN and MINE and retains an `unsupported_verb` error
# instead of silently discarding a verb. `fixture_m040_discarded_train`
# reproduces the PRE-repair declaration and must be rejected.
# --------------------------------------------------------------------------

REPAIRED_VERB_MANIFEST = ("MOVE", "PLANT", "PICK", "DROP", "HARVEST", "CHOP",
                          "TRAIN", "MINE", "MSG", "WAIT")
# the pre-repair dispatcher: TRAIN sat in a skip list and MINE fell out of the
# bottom of the if/elif chain (claude_1/pipeline/referee-train-repair-*.md)
PRE_REPAIR_VERB_MANIFEST = ("MOVE", "PLANT", "PICK", "DROP", "HARVEST",
                            "CHOP", "MSG", "WAIT")
REFEREE_SHA256 = "re" + "0" * 62
PRE_REPAIR_REFEREE_SHA256 = "r1" + "0" * 62
ENGINE_SHA256 = "en" + "0" * 62


def count_commands(commands_text):
    return sum(1 for line in commands_text.split("\n")
               for frag in line.split(";") if frag.strip())


def execution_block(commands_text, **overrides):
    """A complete, valid harness execution-validity declaration."""
    manifest = overrides.pop("verb_manifest", REPAIRED_VERB_MANIFEST)
    emitted = count_commands(commands_text)
    block = {
        "execution_status": ledger.EXECUTION_OK,
        "commands_emitted": emitted,
        "commands_executed": emitted,
        "unsupported_command_events": 0,
        "malformed_command_events": 0,
        "verb_manifest": list(manifest),
        "verb_manifest_sha256": ledger.verb_manifest_sha256(manifest),
        "referee_sha256": REFEREE_SHA256,
        "engine_sha256": ENGINE_SHA256,
        "instrument_version": "i30-fixture-referee/2-train",
        "corpus_version": "i30-fixtures-r3-2026-08-09",
    }
    block.update(overrides)
    return block


def record(run_id, blocks, cmd_lines, bot=None, claimed=False,
           identity_overrides=None, execution=None, claimed_mechanisms=(),
           activation_telemetry=None):
    ident = dict(BASE_IDENTITY)
    ident.update(bot or CANDIDATE_BOT)
    ident.update(identity_overrides or {})
    commands_text = "\n".join(cmd_lines) + "\n"
    return ledger.RunRecord(
        run_id, transcript_of(blocks), commands_text, identity=ident,
        banana_mechanism_claimed=claimed,
        claimed_mechanisms=claimed_mechanisms,
        activation_telemetry=activation_telemetry,
        execution=(execution_block(commands_text) if execution is None
                   else execution))


def _pad(blocks, cmds, n, filler_cmd="WAIT"):
    """Repeat the last state/command until there are n turns."""
    blocks = list(blocks)
    cmds = list(cmds)
    while len(blocks) < n:
        blocks.append(list(blocks[-1]))
    while len(cmds) < len(blocks):
        cmds.append(filler_cmd)
    return blocks, cmds


PLANT_BANANA = "PLANT 0 BANANA"


# --------------------------------------------------------------------------
# 1 / 2 / 3 -- negative controls
# --------------------------------------------------------------------------

def _quiet_blocks():
    """Opponent harvests one natural apple and banks it. No own banana."""
    own = U(0, 0, OWN_DOOR)
    return [
        B([own, U(9, 1, (7, 5))], [P("APPLE", (7, 5), fruits=1)]),
        B([own, U(9, 1, (7, 5), C(apple=1))], [P("APPLE", (7, 5))]),
        B([own, U(9, 1, (8, 5), C(apple=1))], [P("APPLE", (7, 5))]),
        B([own, U(9, 1, (8, 5))], [P("APPLE", (7, 5))], inv1=C(apple=1)),
    ]


def fixture_01_exact_self_pair():
    """Bite-test 1: exact parent-vs-parent; all hashes and commands equal."""
    blocks = _quiet_blocks()
    cmds = ["WAIT"] * 4
    cand = record("bt01-parent-a", blocks, cmds, bot=PARENT_BOT)
    par = record("bt01-parent-b", blocks, cmds, bot=PARENT_BOT)
    return cand, par


def fixture_02_inert_candidate():
    """Bite-test 2: streams differ only by a non-state-changing MSG."""
    blocks = _quiet_blocks()
    cand = record("bt02-candidate", blocks,
                  ["WAIT;MSG i30-diagnostic", "WAIT", "WAIT", "WAIT"],
                  bot=CANDIDATE_BOT)
    par = record("bt02-parent", blocks, ["WAIT"] * 4, bot=PARENT_BOT)
    return cand, par


def fixture_03_no_banana_activation():
    """Bite-test 3: candidate changes own movement, never touches Banana."""
    opp = [U(9, 1, (7, 5)), U(9, 1, (7, 5), C(apple=1)),
           U(9, 1, (8, 5), C(apple=1)), U(9, 1, (8, 5))]
    opp_plants = [[P("APPLE", (7, 5), fruits=1)], [P("APPLE", (7, 5))],
                  [P("APPLE", (7, 5))], [P("APPLE", (7, 5))]]
    opp_inv = [None, None, None, C(apple=1)]

    cand_cells = [OWN_DOOR, (4, 1), (4, 0), (4, 0)]
    par_cells = [OWN_DOOR] * 4
    cand_blocks = [B([U(0, 0, c), o], p, inv1=i)
                   for c, o, p, i in zip(cand_cells, opp, opp_plants, opp_inv)]
    par_blocks = [B([U(0, 0, c), o], p, inv1=i)
                  for c, o, p, i in zip(par_cells, opp, opp_plants, opp_inv)]
    cand = record("bt03-candidate", cand_blocks,
                  ["MOVE 0 4 1", "MOVE 0 4 0", "WAIT", "WAIT"],
                  bot=CANDIDATE_BOT)
    par = record("bt03-parent", par_blocks, ["WAIT"] * 4, bot=PARENT_BOT)
    return cand, par


# --------------------------------------------------------------------------
# 4 -- direct theft only
# --------------------------------------------------------------------------

def fixture_04_direct_theft():
    """Bite-test 4: we create an our-origin banana, opponent banks it."""
    seed = U(0, 0, (7, 4), C(banana=1))
    cand_blocks = [
        B([seed, U(9, 1, (7, 5))]),
        B([U(0, 0, (7, 4)), U(9, 1, (7, 5))],
          [P("BANANA", (7, 4), cooldown=6)]),
        B([U(0, 0, (6, 4)), U(9, 1, (7, 4))],
          [P("BANANA", (7, 4), fruits=1, cooldown=0)]),
        B([U(0, 0, (6, 4)), U(9, 1, (7, 4), C(banana=1))],
          [P("BANANA", (7, 4), cooldown=0)]),
        B([U(0, 0, (6, 4)), U(9, 1, (7, 5), C(banana=1))],
          [P("BANANA", (7, 4), cooldown=0)]),
        B([U(0, 0, (6, 4)), U(9, 1, (8, 5), C(banana=1))],
          [P("BANANA", (7, 4), cooldown=0)]),
        B([U(0, 0, (6, 4)), U(9, 1, (8, 5))],
          [P("BANANA", (7, 4), cooldown=0)], inv1=C(banana=1)),
    ]
    cand_cmds = [PLANT_BANANA, "MOVE 0 6 4"] + ["WAIT"] * 5

    par_blocks = [B([seed, U(9, 1, (7, 5))])]
    par_blocks += [B([U(0, 0, (6, 4), C(banana=1)), U(9, 1, (7, 5))])
                   for _ in range(6)]
    par_cmds = ["MOVE 0 6 4"] + ["WAIT"] * 6

    cand = record("bt04-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt04-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# 5 -- indirect opponent production only
# --------------------------------------------------------------------------

def fixture_05_indirect_only():
    """Bite-test 5: opponent plants and banks its own crop; D-6 stays zero."""
    own1 = U(1, 0, (5, 3))
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    cand_blocks = [
        B([U(0, 0, OWN_DOOR, C(banana=1)), own1, U(9, 1, (6, 5), C(apple=1))]),
        B([U(0, 0, OWN_DOOR), own1, U(9, 1, (6, 5), C(apple=1))], [banana]),
        B([U(0, 0, OWN_DOOR), own1, U(9, 1, (6, 5))],
          [banana, P("APPLE", (6, 5), cooldown=4)]),
        B([U(0, 0, OWN_DOOR), own1, U(9, 1, (6, 5))],
          [banana, P("APPLE", (6, 5), fruits=3, cooldown=0)]),
        B([U(0, 0, OWN_DOOR), own1, U(9, 1, (6, 5), C(apple=1))],
          [banana, P("APPLE", (6, 5), fruits=2, cooldown=0)]),
        B([U(0, 0, OWN_DOOR), own1, U(9, 1, (6, 5), C(apple=2))],
          [banana, P("APPLE", (6, 5), fruits=1, cooldown=0)]),
        B([U(0, 0, OWN_DOOR), own1, U(9, 1, (6, 5), C(apple=3))],
          [banana, P("APPLE", (6, 5), cooldown=0)]),
        B([U(0, 0, OWN_DOOR), own1, U(9, 1, OPP_BANK, C(apple=3))],
          [banana, P("APPLE", (6, 5), cooldown=0)]),
        B([U(0, 0, OWN_DOOR), own1, U(9, 1, OPP_BANK)],
          [banana, P("APPLE", (6, 5), cooldown=0)], inv1=C(apple=3)),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 8

    par_blocks = [
        B([U(0, 0, OWN_DOOR, C(banana=1)), own1, U(9, 1, (6, 5), C(apple=1))]),
        B([U(0, 0, OWN_DOOR, C(banana=1)), own1, U(9, 1, (6, 5), C(apple=1))]),
        B([U(0, 0, OWN_DOOR, C(banana=1)), own1, U(9, 1, OPP_BANK, C(apple=1))]),
        B([U(0, 0, OWN_DOOR, C(banana=1)), own1, U(9, 1, OPP_BANK)],
          inv1=C(apple=1)),
    ]
    par_blocks, par_cmds = _pad(par_blocks, ["WAIT"] * 4, 9)

    cand = record("bt05-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt05-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# 6 -- natural opportunity
# --------------------------------------------------------------------------

def fixture_06_natural_opportunity():
    """Bite-test 6: we stop contesting a natural asset; opponent banks it."""
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    ripe = P("APPLE", (6, 4), fruits=1)
    bare = P("APPLE", (6, 4))
    cand_blocks = [
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(1, 0, (6, 4)), U(9, 1, (6, 5))],
          [ripe]),
        B([U(0, 0, OWN_DOOR), U(1, 0, (5, 4)), U(9, 1, (6, 5))],
          [ripe, banana]),
        B([U(0, 0, OWN_DOOR), U(1, 0, (5, 4)), U(9, 1, (6, 4))],
          [ripe, banana]),
        B([U(0, 0, OWN_DOOR), U(1, 0, (5, 4)), U(9, 1, (6, 4), C(apple=1))],
          [bare, banana]),
        B([U(0, 0, OWN_DOOR), U(1, 0, (5, 4)), U(9, 1, (7, 5), C(apple=1))],
          [bare, banana]),
        B([U(0, 0, OWN_DOOR), U(1, 0, (5, 4)), U(9, 1, OPP_BANK, C(apple=1))],
          [bare, banana]),
        B([U(0, 0, OWN_DOOR), U(1, 0, (5, 4)), U(9, 1, OPP_BANK)],
          [bare, banana], inv1=C(apple=1)),
    ]
    cand_cmds = ["%s;MOVE 1 5 4" % PLANT_BANANA] + ["WAIT"] * 6

    par_blocks = [
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(1, 0, (6, 4)), U(9, 1, (6, 5))],
          [ripe]),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(1, 0, (6, 4), C(apple=1)),
           U(9, 1, (6, 5))], [bare]),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(1, 0, (5, 4), C(apple=1)),
           U(9, 1, (6, 5))], [bare]),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(1, 0, (4, 4), C(apple=1)),
           U(9, 1, (6, 5))], [bare]),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(1, 0, (4, 4)), U(9, 1, (6, 5))],
          [bare], inv0=C(apple=1)),
    ]
    par_cmds = ["HARVEST 1", "MOVE 1 5 4", "MOVE 1 4 4", "DROP 1", "WAIT"]

    cand = record("bt06-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt06-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# 7 -- TRAIN-spend offset
# --------------------------------------------------------------------------

def fixture_07_train_offset():
    """Bite-test 7: identical gross deposits, one extra opponent TRAIN."""
    start_inv1 = C(plum=3, lemon=3, apple=3)
    after_drop = C(plum=3, lemon=3, apple=4)
    after_train = C(plum=1, lemon=1, apple=2)
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    ripe = P("APPLE", (7, 5), fruits=1)
    bare = P("APPLE", (7, 5))

    cand_blocks = [
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, OPP_BANK)], [ripe],
          inv1=start_inv1),
        B([U(0, 0, OWN_DOOR), U(9, 1, (7, 5))], [ripe, banana],
          inv1=start_inv1),
        B([U(0, 0, OWN_DOOR), U(9, 1, (7, 5), C(apple=1))], [bare, banana],
          inv1=start_inv1),
        B([U(0, 0, OWN_DOOR), U(9, 1, OPP_BANK, C(apple=1))], [bare, banana],
          inv1=start_inv1),
        B([U(0, 0, OWN_DOOR), U(9, 1, OPP_BANK)], [bare, banana],
          inv1=after_drop),
        B([U(0, 0, OWN_DOOR), U(9, 1, OPP_BANK),
           U(10, 1, OPP_SHACK, cap=1)], [bare, banana], inv1=after_train),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 5

    par_blocks = [
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, OPP_BANK)], [ripe],
          inv1=start_inv1),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, (7, 5))], [ripe],
          inv1=start_inv1),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, (7, 5), C(apple=1))],
          [bare], inv1=start_inv1),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, OPP_BANK, C(apple=1))],
          [bare], inv1=start_inv1),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, OPP_BANK)], [bare],
          inv1=after_drop),
        B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, OPP_BANK)], [bare],
          inv1=after_drop),
    ]
    par_cmds = ["WAIT"] * 6

    cand = record("bt07-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt07-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# 8 -- mixed cargo
# --------------------------------------------------------------------------

def fixture_08_mixed_cargo():
    """Bite-test 8: one DROP carrying ours + opponent + natural atoms."""
    ours_cell = (5, 4)                       # cheby((5,4),(4,3)) == 1
    banana_bare = P("BANANA", ours_cell, cooldown=6)
    banana_ripe = P("BANANA", ours_cell, fruits=1, cooldown=0)
    nat2 = P("APPLE", (7, 5), fruits=2)
    nat1 = P("APPLE", (7, 5), fruits=1)
    nat0 = P("APPLE", (7, 5))
    opp_bare = P("APPLE", (6, 5), cooldown=4)
    opp_ripe = P("APPLE", (6, 5), fruits=1, cooldown=0)
    own1 = U(1, 0, OWN_DOOR)

    cand_blocks = [
        B([U(0, 0, ours_cell, C(banana=1)), own1, U(9, 1, (7, 5))], [nat2]),
        B([U(0, 0, ours_cell), own1, U(9, 1, (7, 5), C(apple=1))],
          [nat1, banana_bare]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, (7, 5), C(apple=2))],
          [nat0, banana_bare]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, (6, 5), C(apple=2))],
          [nat0, banana_bare]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, (6, 5), C(apple=1))],
          [nat0, banana_bare, opp_bare]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, (6, 5), C(apple=1))],
          [nat0, banana_ripe, opp_ripe]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, (6, 5), C(apple=2))],
          [nat0, banana_ripe, P("APPLE", (6, 5), cooldown=0)]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, ours_cell, C(apple=2))],
          [nat0, banana_ripe, P("APPLE", (6, 5), cooldown=0)]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, ours_cell, C(apple=2, banana=1))],
          [nat0, P("BANANA", ours_cell, cooldown=0),
           P("APPLE", (6, 5), cooldown=0)]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, (6, 5), C(apple=2, banana=1))],
          [nat0, P("BANANA", ours_cell, cooldown=0),
           P("APPLE", (6, 5), cooldown=0)]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, OPP_BANK, C(apple=2, banana=1))],
          [nat0, P("BANANA", ours_cell, cooldown=0),
           P("APPLE", (6, 5), cooldown=0)]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, OPP_BANK)],
          [nat0, P("BANANA", ours_cell, cooldown=0),
           P("APPLE", (6, 5), cooldown=0)], inv1=C(apple=2, banana=1)),
    ]
    cand_cmds = [PLANT_BANANA, "MOVE 0 4 4"] + ["WAIT"] * 10

    par_blocks = [B([U(0, 0, ours_cell, C(banana=1)), own1, U(9, 1, (7, 5))],
                    [nat2]) for _ in range(12)]
    par_cmds = ["WAIT"] * 12

    cand = record("bt08-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt08-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# 9 -- longer-game schedule
# --------------------------------------------------------------------------

def fixture_09_longer_game():
    """Bite-test 9: candidate extends the game; extra opponent own cycle."""
    own1 = U(1, 0, (5, 3))
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    ripe = P("APPLE", (7, 5), fruits=1)
    bare = P("APPLE", (7, 5))
    opp_tree = P("APPLE", (6, 5), cooldown=4)

    own0 = U(0, 0, OWN_DOOR)
    cand_blocks = [
        B([U(0, 0, OWN_DOOR, C(banana=1)), own1, U(9, 1, (7, 5))], [ripe]),
        B([own0, own1, U(9, 1, (7, 5), C(apple=1))], [bare, banana]),
        B([own0, own1, U(9, 1, OPP_BANK, C(apple=1))], [bare, banana]),
        B([own0, own1, U(9, 1, OPP_BANK)], [bare, banana], inv1=C(apple=1)),
        B([own0, own1, U(9, 1, OPP_BANK, C(apple=1))], [bare, banana]),
        B([own0, own1, U(9, 1, (6, 5), C(apple=1))], [bare, banana]),
        B([own0, own1, U(9, 1, (6, 5))], [bare, banana, opp_tree]),
        B([own0, own1, U(9, 1, (6, 5))],
          [bare, banana, P("APPLE", (6, 5), fruits=2, cooldown=0)]),
        B([own0, own1, U(9, 1, (6, 5), C(apple=1))],
          [bare, banana, P("APPLE", (6, 5), fruits=1, cooldown=0)]),
        B([own0, own1, U(9, 1, (6, 5), C(apple=2))],
          [bare, banana, P("APPLE", (6, 5), cooldown=0)]),
        B([own0, own1, U(9, 1, OPP_BANK, C(apple=2))],
          [bare, banana, P("APPLE", (6, 5), cooldown=0)]),
        B([own0, own1, U(9, 1, OPP_BANK)],
          [bare, banana, P("APPLE", (6, 5), cooldown=0)], inv1=C(apple=2)),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 11

    seed0 = U(0, 0, OWN_DOOR, C(banana=1))
    par_blocks = [
        B([seed0, own1, U(9, 1, (7, 5))], [ripe]),
        B([seed0, own1, U(9, 1, (7, 5), C(apple=1))], [bare]),
        B([seed0, own1, U(9, 1, OPP_BANK, C(apple=1))], [bare]),
        B([seed0, own1, U(9, 1, OPP_BANK)], [bare], inv1=C(apple=1)),
        B([seed0, own1, U(9, 1, OPP_BANK)], [bare], inv1=C(apple=1)),
    ]
    par_cmds = ["WAIT"] * 5

    cand = record("bt09-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt09-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# 10 -- D89-like blind spot
# --------------------------------------------------------------------------

def fixture_10_blind_spot():
    """Bite-test 10: D-1..D-9 all PASS, D-6 zero, opponent own production up."""
    own1 = U(1, 0, (5, 3))
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    nat2 = P("APPLE", (7, 5), fruits=2)
    nat1 = P("APPLE", (7, 5), fruits=1)
    nat0 = P("APPLE", (7, 5))
    own0 = U(0, 0, OWN_DOOR)
    seed0 = U(0, 0, OWN_DOOR, C(banana=1))

    cand_blocks = [
        B([seed0, own1, U(9, 1, (7, 5))], [nat2]),
        B([own0, own1, U(9, 1, (7, 5), C(apple=1))], [nat1, banana]),
        B([own0, own1, U(9, 1, (7, 5), C(apple=2))], [nat0, banana]),
        B([own0, own1, U(9, 1, (6, 5), C(apple=2))], [nat0, banana]),
        B([own0, own1, U(9, 1, (6, 5), C(apple=1))],
          [nat0, banana, P("APPLE", (6, 5), cooldown=4)]),
        B([own0, own1, U(9, 1, (6, 5), C(apple=1))],
          [nat0, banana, P("APPLE", (6, 5), fruits=2, cooldown=0)]),
        B([own0, own1, U(9, 1, (6, 5), C(apple=2))],
          [nat0, banana, P("APPLE", (6, 5), fruits=1, cooldown=0)]),
        B([own0, own1, U(9, 1, (6, 5), C(apple=3))],
          [nat0, banana, P("APPLE", (6, 5), cooldown=0)]),
        B([own0, own1, U(9, 1, OPP_BANK, C(apple=3))],
          [nat0, banana, P("APPLE", (6, 5), cooldown=0)]),
        B([own0, own1, U(9, 1, OPP_BANK)],
          [nat0, banana, P("APPLE", (6, 5), cooldown=0)], inv1=C(apple=3)),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 9

    par_blocks = [
        B([seed0, own1, U(9, 1, (7, 5))], [nat2]),
        B([seed0, own1, U(9, 1, (7, 5), C(apple=1))], [nat1]),
        B([seed0, own1, U(9, 1, (7, 5), C(apple=2))], [nat0]),
        B([seed0, own1, U(9, 1, OPP_BANK, C(apple=2))], [nat0]),
        B([seed0, own1, U(9, 1, OPP_BANK)], [nat0], inv1=C(apple=2)),
    ]
    par_blocks, par_cmds = _pad(par_blocks, ["WAIT"] * 5, 10)

    cand = record("bt10-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt10-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# 11 / 12 / 13 -- fail-closed controls
# --------------------------------------------------------------------------

def fixture_11_hash_mismatch_self_pair():
    """Bite-test 11: declared self-pair whose bot source hash differs."""
    blocks = _quiet_blocks()
    cmds = ["WAIT"] * 4
    cand = record("bt11-a", blocks, cmds, bot=PARENT_BOT,
                  identity_overrides={"bot_source_sha256": "zz" + "0" * 62})
    par = record("bt11-b", blocks, cmds, bot=PARENT_BOT)
    return cand, par


def fixture_12_untagged_atom():
    """Bite-test 12: one score-bearing opponent atom with no provable source."""
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    own0 = U(0, 0, OWN_DOOR)
    seed0 = U(0, 0, OWN_DOOR, C(banana=1))
    cand_blocks = [
        B([seed0, U(9, 1, (5, 5))]),
        B([own0, U(9, 1, (5, 5), C(apple=1))], [banana]),
        B([own0, U(9, 1, (6, 5), C(apple=1))], [banana]),
        B([own0, U(9, 1, OPP_BANK, C(apple=1))], [banana]),
        B([own0, U(9, 1, OPP_BANK)], [banana], inv1=C(apple=1)),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 4
    par_blocks = [B([seed0, U(9, 1, (5, 5))]) for _ in range(5)]
    par_cmds = ["WAIT"] * 5

    cand = record("bt12-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt12-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


def fixture_13_nonzero_residual():
    """Bite-test 13: opponent bank gains score with no deposit and no TRAIN."""
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    own0 = U(0, 0, OWN_DOOR)
    seed0 = U(0, 0, OWN_DOOR, C(banana=1))
    cand_blocks = [
        B([seed0, U(9, 1, OPP_BANK)]),
        B([own0, U(9, 1, OPP_BANK)], [banana], inv1=C(apple=1)),
        B([own0, U(9, 1, OPP_BANK)], [banana], inv1=C(apple=1)),
    ]
    cand_cmds = [PLANT_BANANA, "WAIT", "WAIT"]
    par_blocks = [B([seed0, U(9, 1, OPP_BANK)]) for _ in range(3)]
    par_cmds = ["WAIT"] * 3

    cand = record("bt13-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("bt13-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# supplementary coverage fixture -- NOT one of the fifteen mandated
# bite-tests. The fifteen never deposit WOOD, so without this the frozen
# WOOD=4 score weight and the CHOP provenance rule of spec sec. 5.2 are live
# but unexercised code. See i30-implementation-2026-08-08.md.
# --------------------------------------------------------------------------

def fixture_s1_wood_chop():
    """Opponent chops one natural tree and one of ours, then banks the wood."""
    ours_cell = (5, 4)                       # cheby((5,4),(4,3)) == 1
    banana = P("BANANA", ours_cell, cooldown=6)
    nat = P("APPLE", (7, 5))
    own1 = U(1, 0, OWN_DOOR)

    cand_blocks = [
        B([U(0, 0, ours_cell, C(banana=1)), own1, U(9, 1, (7, 5))], [nat]),
        # the planter is still standing on the new asset here, which is what
        # makes its creator provable (spec sec. 5.2 / R4)
        B([U(0, 0, ours_cell), own1, U(9, 1, (7, 5))], [nat, banana]),
        # natural tree felled -> WOOD tagged natural
        B([U(0, 0, (4, 4)), own1, U(9, 1, (7, 5), C(wood=1))], [banana]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, (6, 5), C(wood=1))], [banana]),
        B([U(0, 0, (4, 4)), own1, U(9, 1, ours_cell, C(wood=1))], [banana]),
        # our banana felled -> WOOD tagged ours
        B([U(0, 0, (4, 4)), own1, U(9, 1, ours_cell, C(wood=2))], []),
        B([U(0, 0, (4, 4)), own1, U(9, 1, (6, 5), C(wood=2))], []),
        B([U(0, 0, (4, 4)), own1, U(9, 1, OPP_BANK, C(wood=2))], []),
        B([U(0, 0, (4, 4)), own1, U(9, 1, OPP_BANK)], [], inv1=C(wood=2)),
    ]
    cand_cmds = [PLANT_BANANA, "MOVE 0 4 4"] + ["WAIT"] * 7

    par_blocks = [B([U(0, 0, ours_cell, C(banana=1)), own1, U(9, 1, (7, 5))],
                    [nat]) for _ in range(9)]
    par_cmds = ["WAIT"] * 9

    cand = record("s01-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    par = record("s01-parent", par_blocks, par_cmds, bot=PARENT_BOT,
                 claimed=True)
    return cand, par


# --------------------------------------------------------------------------
# adversarial provenance-identifiability fixtures
#
# Required by the spec-author ruling
#   chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md, section "D5 ruling".
#
# Each one is constructed so that the OLD deterministic tie-break (FIFO atom
# order / greedy deposit-before-withdrawal / unit-id ordering) produces a
# CONFIDENT but non-identifiable source class, while terminal score, total net
# bank flow and the conservation residual all stay correct. Under the ruling
# every one of them must instead yield `unknown` and `GATE_UNREADY`:
#
#   "A deterministic tie-break is not proof of identifiability."
# --------------------------------------------------------------------------

def _static_parent(run_id, block, n_turns):
    """A parent that shares the candidate's exact turn-1 state and does nothing.

    Sharing turn 1 byte-for-byte is what keeps `initial_state_sha256` equal,
    so the pair identity check passes and the adversarial fixture is judged on
    provenance alone (spec sec. 3).
    """
    return record(run_id, [list(block) for _ in range(n_turns)],
                  ["WAIT"] * n_turns, bot=PARENT_BOT, claimed=True)


def fixture_a1_same_turn_deposit_withdrawal():
    """Ruling D5 fixture 1: same-resource deposit and withdrawal, zero net.

    Turn 6->7 one opponent unit's BANANA carry falls by one at a bank cell
    while another opponent unit's BANANA carry rises by one at a bank cell,
    and the opponent bank inventory is unchanged. Two integer allocations
    satisfy every observable:

        (deposit 1, withdraw 1)   -- the old tie-break's answer
        (deposit 0, withdraw 0)   -- one unit lost its cargo, the other
                                     acquired elsewhere

    The first moves one `ours` atom into the bank and one `natural` atom out;
    the second moves nothing. Terminal score, net bank flow and residual are
    identical either way, so no arithmetic check can separate them.
    """
    b1 = B([U(0, 0, (6, 5), C(banana=1)), U(9, 1, (6, 4)), U(10, 1, (8, 5))],
           [], inv1=C(banana=1))
    ripe = P("BANANA", (6, 5), fruits=1, cooldown=0)
    bare = P("BANANA", (6, 5), cooldown=0)
    cand_blocks = [
        b1,
        # our unit plants; it is the sole occupant, so the asset is `ours`
        B([U(0, 0, (6, 5)), U(9, 1, (6, 4)), U(10, 1, (8, 5))], [ripe],
          inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (6, 5)), U(10, 1, (8, 5))], [ripe],
          inv1=C(banana=1)),
        # opponent harvests our banana -> one atom of class `ours`
        B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=1)), U(10, 1, (8, 5))],
          [bare], inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (7, 5), C(banana=1)), U(10, 1, (8, 5))],
          [bare], inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6), C(banana=1)), U(10, 1, (8, 5))],
          [bare], inv1=C(banana=1)),
        # the ambiguous transition
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6)), U(10, 1, (8, 5), C(banana=1))],
          [bare], inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6)), U(10, 1, (8, 5), C(banana=1))],
          [bare], inv1=C(banana=1)),
    ]
    cand_cmds = [PLANT_BANANA, "MOVE 0 5 5"] + ["WAIT"] * 6
    cand = record("a1-candidate", cand_blocks, cand_cmds, bot=CANDIDATE_BOT,
                  claimed=True)
    return cand, _static_parent("a1-parent", b1, 8)


def fixture_a2_multi_source_deposit():
    """Ruling D5 fixture 2: two depositing units of different classes while a
    third withdraws.

    Turn 5->6: unit 9 (carrying an `ours` banana) and unit 11 (carrying a
    `natural` banana) both empty their carry at bank cells while unit 10's
    carry rises by one banana, and the bank inventory rises by exactly one.
    Feasible allocations include (deposit 2, withdraw 1) and
    (deposit 1, withdraw 0) -- and in the second, *which* of the two units
    deposited is itself undetermined.
    """
    nat_ripe = P("BANANA", (5, 6), fruits=1, cooldown=0)
    nat_bare = P("BANANA", (5, 6), cooldown=0)
    our_ripe = P("BANANA", (6, 5), fruits=1, cooldown=0)
    our_bare = P("BANANA", (6, 5), cooldown=0)
    b1 = B([U(0, 0, (6, 5), C(banana=1)), U(9, 1, (6, 4)), U(10, 1, (8, 5)),
            U(11, 1, (5, 6))], [nat_ripe], inv1=C(banana=1))
    cand_blocks = [
        b1,
        B([U(0, 0, (6, 5)), U(9, 1, (6, 4)), U(10, 1, (8, 5)),
           U(11, 1, (5, 6))], [nat_ripe, our_ripe], inv1=C(banana=1)),
        # unit 11 harvests the map-seeded (natural) banana
        B([U(0, 0, (5, 5)), U(9, 1, (6, 5)), U(10, 1, (8, 5)),
           U(11, 1, (5, 6), C(banana=1))], [nat_bare, our_ripe],
          inv1=C(banana=1)),
        # unit 9 harvests ours
        B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=1)), U(10, 1, (8, 5)),
           U(11, 1, (6, 6), C(banana=1))], [nat_bare, our_bare],
          inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6), C(banana=1)), U(10, 1, (8, 5)),
           U(11, 1, (8, 7), C(banana=1))], [nat_bare, our_bare],
          inv1=C(banana=1)),
        # the ambiguous transition
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6)), U(10, 1, (8, 5), C(banana=1)),
           U(11, 1, (8, 7))], [nat_bare, our_bare], inv1=C(banana=2)),
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6)), U(10, 1, (8, 5), C(banana=1)),
           U(11, 1, (8, 7))], [nat_bare, our_bare], inv1=C(banana=2)),
    ]
    cand_cmds = [PLANT_BANANA, "MOVE 0 5 5"] + ["WAIT"] * 5
    cand = record("a2-candidate", cand_blocks, cand_cmds, bot=CANDIDATE_BOT,
                  claimed=True)
    return cand, _static_parent("a2-parent", b1, 7)


def fixture_a2b_deposit_unit_assignment():
    """Ruling D5 fixture 2b: which of two units deposited is undetermined.

    Turn 5->6 two opponent units at bank cells each empty one banana from
    their carry, but the bank gains exactly one. The split itself is forced
    (one deposit, no withdrawal) -- what is not forced is WHICH unit's cargo
    was banked and which was lost, and the two units carry different source
    classes. Unit-id order is a tie-break, not an observation.
    """
    nat_ripe = P("BANANA", (5, 6), fruits=1, cooldown=0)
    nat_bare = P("BANANA", (5, 6), cooldown=0)
    our_ripe = P("BANANA", (6, 5), fruits=1, cooldown=0)
    our_bare = P("BANANA", (6, 5), cooldown=0)
    b1 = B([U(0, 0, (6, 5), C(banana=1)), U(9, 1, (6, 4)), U(10, 1, (8, 5)),
            U(11, 1, (5, 6))], [nat_ripe], inv1=C(banana=1))
    cand_blocks = [
        b1,
        B([U(0, 0, (6, 5)), U(9, 1, (6, 4)), U(10, 1, (8, 5)),
           U(11, 1, (5, 6))], [nat_ripe, our_ripe], inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (6, 5)), U(10, 1, (8, 5)),
           U(11, 1, (5, 6), C(banana=1))], [nat_bare, our_ripe],
          inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=1)), U(10, 1, (8, 5)),
           U(11, 1, (6, 6), C(banana=1))], [nat_bare, our_bare],
          inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6), C(banana=1)), U(10, 1, (8, 5)),
           U(11, 1, (8, 7), C(banana=1))], [nat_bare, our_bare],
          inv1=C(banana=1)),
        # two carries empty at bank cells, the bank gains one
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6)), U(10, 1, (8, 5)),
           U(11, 1, (8, 7))], [nat_bare, our_bare], inv1=C(banana=2)),
        B([U(0, 0, (5, 5)), U(9, 1, (7, 6)), U(10, 1, (8, 5)),
           U(11, 1, (8, 7))], [nat_bare, our_bare], inv1=C(banana=2)),
    ]
    cand_cmds = [PLANT_BANANA, "MOVE 0 5 5"] + ["WAIT"] * 5
    cand = record("a2b-candidate", cand_blocks, cand_cmds, bot=CANDIDATE_BOT,
                  claimed=True)
    return cand, _static_parent("a2b-parent", b1, 7)


def fixture_a6_cancelling_unknown_flow():
    """Ruling D1: unknown deposits and withdrawals that cancel numerically.

    One untagged score-bearing atom is banked and later withdrawn, so
    `NBF_unknown` -- and therefore `D_UNKNOWN_NET` -- is exactly zero while an
    unproved atom certainly crossed the tent threshold. Every allocation here
    IS uniquely derivable, so the identifiability gate stays silent and only
    the unknown-provenance gate can fail this pair closed:

      "I-30 still fails closed on any unproved score-bearing atom, even when
       unknown deposits and withdrawals happen to cancel numerically.
       `D_UNKNOWN_NET == 0` is not sufficient evidence of complete provenance."
    """
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    b1 = B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, (5, 5))], [])
    cand_blocks = [
        b1,
        # an apple with no asset on the cell and no iron: untagged
        B([U(0, 0, OWN_DOOR), U(9, 1, (5, 5), C(apple=1))], [banana]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5), C(apple=1))], [banana]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5))], [banana], inv1=C(apple=1)),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5), C(apple=1))], [banana]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5), C(apple=1))], [banana]),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 5
    cand = record("a6-candidate", cand_blocks, cand_cmds, bot=CANDIDATE_BOT,
                  claimed=True)
    return cand, _static_parent("a6-parent", b1, 6)


def fixture_a7_seed_and_deposit_at_one_bank_cell():
    """Control against the identifiability gate FIRING TOO OFTEN.

    Turn 5->6 one opponent unit banks a banana at (8,5) while another
    opponent unit, also on a bank cell, spends a banana as the seed of a
    successful own PLANT at (8,7). Two carries fall and the bank rises by
    one, which LOOKS like the ambiguous case -- but the PLANT explains the
    second decrease exactly, so the allocation is still unique and the pair
    must NOT be `unknown`.

    A fail-closed rule that cannot tell this apart from `a2b` would make the
    instrument useless rather than safe.
    """
    our_ripe = P("BANANA", (6, 5), fruits=1, cooldown=0)
    our_bare = P("BANANA", (6, 5), cooldown=0)
    seeded = P("BANANA", (8, 7), cooldown=6)
    b1 = B([U(0, 0, (6, 5), C(banana=1)), U(9, 1, (6, 4)),
            U(10, 1, (8, 7), C(banana=1))], [])
    cand_blocks = [
        b1,
        B([U(0, 0, (6, 5)), U(9, 1, (6, 4)),
           U(10, 1, (8, 7), C(banana=1))], [our_ripe]),
        B([U(0, 0, (5, 5)), U(9, 1, (6, 5)),
           U(10, 1, (8, 7), C(banana=1))], [our_ripe]),
        B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=1)),
           U(10, 1, (8, 7), C(banana=1))], [our_bare]),
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5), C(banana=1)),
           U(10, 1, (8, 7), C(banana=1))], [our_bare]),
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5)), U(10, 1, (8, 7))],
          [our_bare, seeded], inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5)), U(10, 1, (8, 7))],
          [our_bare, seeded], inv1=C(banana=1)),
    ]
    cand_cmds = [PLANT_BANANA, "MOVE 0 5 5"] + ["WAIT"] * 5
    cand = record("a7-candidate", cand_blocks, cand_cmds, bot=CANDIDATE_BOT,
                  claimed=True)
    return cand, _static_parent("a7-parent", b1, 7)


def fixture_a3_class_swap(order="ours_first"):
    """Ruling D5 fixture 3: the indistinguishable-pair / class-swap test.

    One opponent unit ends up carrying exactly two bananas, one of class
    `ours` and one of class `opponent`, and then banks exactly one of them.
    The two hidden histories -- "the `ours` atom was banked" and "the
    `opponent` atom was banked" -- produce the *same* observable transition
    (carry 2 -> 1, bank +1), the same `D_OPP`, the same net bank flow and the
    same residual, but require different `D_DIRECT` / `D_SCHEDULE` labels.

    `order` swaps only the acquisition order, i.e. only the FIFO tie-break's
    answer. Turns 7-9, which contain the ambiguous transition, are byte
    identical between the two variants.
    """
    assert order in ("ours_first", "opponent_first"), order
    ours_ripe = P("BANANA", (6, 5), fruits=1, cooldown=0)
    ours_bare = P("BANANA", (6, 5), cooldown=0)
    opp_ripe = P("BANANA", (6, 4), fruits=1, cooldown=0)
    opp_bare = P("BANANA", (6, 4), cooldown=0)

    b1 = B([U(0, 0, (6, 5), C(banana=1)), U(9, 1, (6, 4), C(banana=1))], [])
    # our unit plants at (6,5) (sole occupant -> `ours`); the opponent unit
    # plants at (6,4) using its own seed (sole occupant -> `opponent`)
    b2 = B([U(0, 0, (6, 5)), U(9, 1, (6, 4))], [ours_ripe, opp_ripe])

    if order == "ours_first":
        mid = [
            B([U(0, 0, (5, 5)), U(9, 1, (6, 5))], [ours_ripe, opp_ripe]),
            B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=1))],
              [ours_bare, opp_ripe]),
            B([U(0, 0, (5, 5)), U(9, 1, (6, 4), C(banana=1))],
              [ours_bare, opp_ripe]),
            B([U(0, 0, (5, 5)), U(9, 1, (6, 4), C(banana=2))],
              [ours_bare, opp_bare]),
        ]
    else:
        mid = [
            B([U(0, 0, (5, 5)), U(9, 1, (6, 4))], [ours_ripe, opp_ripe]),
            B([U(0, 0, (5, 5)), U(9, 1, (6, 4), C(banana=1))],
              [ours_ripe, opp_bare]),
            B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=1))],
              [ours_ripe, opp_bare]),
            B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=2))],
              [ours_bare, opp_bare]),
        ]

    tail = [
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5), C(banana=2))],
          [ours_bare, opp_bare]),
        # the ambiguous transition: exactly one of two indistinguishable
        # bananas is banked
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5), C(banana=1))],
          [ours_bare, opp_bare], inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5), C(banana=1))],
          [ours_bare, opp_bare], inv1=C(banana=1)),
    ]
    cand_blocks = [b1, b2] + mid + tail
    cand_cmds = [PLANT_BANANA, "MOVE 0 5 5"] + ["WAIT"] * 7
    cand = record("a3-%s-candidate" % order, cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    return cand, _static_parent("a3-%s-parent" % order, b1, len(cand_blocks))


def fixture_a4_dead_cell_acquisition():
    """Ruling D5 fixture 4: acquisition on a cell a long-dead asset occupied.

    A map-seeded APPLE stands at (7,5) on turn 1 and is gone by turn 2. On
    turn 3->4 an opponent unit standing on (7,5) gains an apple with no asset
    present. The provenance registry still remembers a `natural` asset at that
    cell, so consulting it alone would launder the atom into `natural`.
    """
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    b1 = B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, (6, 5))],
           [P("APPLE", (7, 5), fruits=1)])
    cand_blocks = [
        b1,
        B([U(0, 0, OWN_DOOR), U(9, 1, (6, 5))], [banana]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (7, 5))], [banana]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (7, 5), C(apple=1))], [banana]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5), C(apple=1))], [banana]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5))], [banana], inv1=C(apple=1)),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5))], [banana], inv1=C(apple=1)),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 6
    cand = record("a4-candidate", cand_blocks, cand_cmds, bot=CANDIDATE_BOT,
                  claimed=True)
    return cand, _static_parent("a4-parent", b1, 7)


def fixture_a5_planter_occupancy(mode="mixed"):
    """Ruling D5 fixture 5: absent or mixed planter occupancy.

    `mixed`  -- a new plant appears on a cell holding one unit of each player,
                so the creator is not determined.
    `absent` -- a new plant appears on a cell holding no unit at all.

    Either way the asset class is `unknown`, and so is every fruit the
    opponent harvests from it and banks.
    """
    assert mode in ("mixed", "absent"), mode
    ripe = P("BANANA", (6, 5), fruits=1, cooldown=0)
    bare = P("BANANA", (6, 5), cooldown=0)
    if mode == "mixed":
        b1 = B([U(0, 0, (6, 5), C(banana=1)), U(9, 1, (6, 5))], [])
        b2 = B([U(0, 0, (6, 5)), U(9, 1, (6, 5))], [ripe])
        b3 = B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=1))], [bare])
    else:
        b1 = B([U(0, 0, (6, 5), C(banana=1)), U(9, 1, (6, 4))], [])
        b2 = B([U(0, 0, (5, 5)), U(9, 1, (6, 4))], [ripe])
        b3 = B([U(0, 0, (5, 5)), U(9, 1, (6, 5))], [ripe])

    cand_blocks = [b1, b2, b3]
    if mode == "absent":
        cand_blocks.append(
            B([U(0, 0, (5, 5)), U(9, 1, (6, 5), C(banana=1))], [bare]))
    cand_blocks += [
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5), C(banana=1))], [bare]),
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5))], [bare], inv1=C(banana=1)),
        B([U(0, 0, (5, 5)), U(9, 1, (8, 5))], [bare], inv1=C(banana=1)),
    ]
    cand_cmds = [PLANT_BANANA, "MOVE 0 5 5"] + ["WAIT"] * (len(cand_blocks) - 2)
    cand = record("a5-%s-candidate" % mode, cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    return cand, _static_parent("a5-%s-parent" % mode, b1, len(cand_blocks))


def fixture_d1_gross_production_with_offsetting_withdrawal():
    """Ruling D1 fixture: gross opponent production rises, terminal score does
    not.

    The opponent plants its own APPLE tree, harvests one apple and banks it
    (gross opponent production `+1`), then withdraws one apple from the bank
    on a later turn and is still holding it at the terminal state (net bank
    flow `0`). Every step is uniquely derivable, so this fixture must NOT be
    `unknown`: it exists to prove that gross and net outputs cannot be
    substituted for one another.
    """
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    tree_bare = P("APPLE", (6, 5), cooldown=0)
    tree_ripe = P("APPLE", (6, 5), fruits=1, cooldown=0)
    b1 = B([U(0, 0, OWN_DOOR, C(banana=1)), U(9, 1, (6, 5), C(apple=1))], [])
    cand_blocks = [
        b1,
        # our BANANA at the tent door and the opponent's own APPLE tree, each
        # with a single occupant, so both creators are determined
        B([U(0, 0, OWN_DOOR), U(9, 1, (6, 5))], [banana, tree_bare]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (6, 5))], [banana, tree_ripe]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (6, 5), C(apple=1))],
          [banana, tree_bare]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5), C(apple=1))],
          [banana, tree_bare]),
        # gross deposit of one opponent-origin apple
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5))], [banana, tree_bare],
          inv1=C(apple=1)),
        # ... and an equal withdrawal on a later turn: terminal score is back
        # to zero while gross production stayed at +1
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5), C(apple=1))],
          [banana, tree_bare]),
        B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5), C(apple=1))],
          [banana, tree_bare]),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 7
    cand = record("d1-candidate", cand_blocks, cand_cmds, bot=CANDIDATE_BOT,
                  claimed=True)
    return cand, _static_parent("d1-parent", b1, 8)


# ==========================================================================
# Revision-3 fixtures -- one per blocking defect of
# chatgpt_1/i30-revision-2-review-2026-08-08.md
# ==========================================================================

def fixture_baseline_stock_recycling():
    """I30R2-5: the opponent recycles its OPENING BANK STOCK through the bank.

    The opponent starts holding one banana in its shack. The candidate's
    banana presence makes it withdraw that banana on one turn and re-deposit
    it on the next. Terminal score is unchanged and nothing was produced, so
    `D_PRODUCTION_GROSS` must stay exactly 0 -- revision 2 labelled the
    opening stock `natural` and reported a gross production of +1.

    Every step is uniquely derivable: on the withdrawal turn no unit drops
    (`drop_cand == 0`) and on the deposit turn none picks (`pick_cand == 0`),
    so each feasible withdrawal interval holds exactly one integer.
    """
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    own0 = U(0, 0, OWN_DOOR)
    seed0 = U(0, 0, OWN_DOOR, C(banana=1))
    b1 = B([seed0, U(9, 1, OPP_BANK)], [], inv1=C(banana=1))
    cand_blocks = [
        b1,
        # our banana is planted; the opponent withdraws its opening banana
        B([own0, U(9, 1, OPP_BANK, C(banana=1))], [banana]),
        # ... and banks it again, unchanged
        B([own0, U(9, 1, OPP_BANK)], [banana], inv1=C(banana=1)),
        B([own0, U(9, 1, OPP_BANK)], [banana], inv1=C(banana=1)),
    ]
    cand_cmds = [PLANT_BANANA] + ["WAIT"] * 3
    cand = record("baseline-candidate", cand_blocks, cand_cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    return cand, _static_parent("baseline-parent", b1, 4)


def fixture_lying_identity_pair():
    """I30R2-6: two different worlds, one declared identity.

    Both callers declare the PARENT's map/initial-state/transcript/command
    hashes. Revision 2's `setdefault` adopted the declaration, so the pair
    passed `check_pair_identity()` as an exact self-pair while the transcripts
    differed. The hashes are now derived from the bytes and the declaration is
    only a pin to check.
    """
    par_blocks = _quiet_blocks()
    cand_blocks = [list(b) for b in par_blocks]
    # one different observed state: the opponent never banks its apple
    cand_blocks[-1] = B([U(0, 0, OWN_DOOR), U(9, 1, (8, 5))],
                        [P("APPLE", (7, 5))])
    cmds = ["WAIT"] * 4
    par = record("lie-parent", par_blocks, cmds, bot=PARENT_BOT)
    cand = record("lie-candidate", cand_blocks, cmds, bot=PARENT_BOT,
                  identity_overrides=dict(par.derived_identity))
    return cand, par


def fixture_m040_discarded_train():
    """I30R2-8: the m040 signature -- emitted TRAIN, no spawn, no error.

    The pre-repair panel referee parsed `TRAIN` and dropped it on the floor.
    I-30 derives TRAIN spend from observed spawns, so this transcript is
    internally consistent: no spawn, no spend, residual zero. Only the
    harness's own execution declaration can expose it, and this one exposes it
    twice over -- the referee's verb manifest never implemented TRAIN, and the
    executed count is short of the emitted count.
    """
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    own0 = U(0, 0, OWN_DOOR)
    seed0 = U(0, 0, OWN_DOOR, C(banana=1))
    b1 = B([seed0, U(9, 1, OPP_BANK)])
    cand_blocks = [b1] + [B([own0, U(9, 1, OPP_BANK)], [banana])
                          for _ in range(3)]
    cand_cmds = [PLANT_BANANA] + ["TRAIN 1 1 1 1"] * 3
    commands_text = "\n".join(cand_cmds) + "\n"
    cand = record(
        "m040-candidate", cand_blocks, cand_cmds, bot=CANDIDATE_BOT,
        claimed=True,
        execution=execution_block(
            commands_text,
            verb_manifest=PRE_REPAIR_VERB_MANIFEST,
            # the referee reported success: the discard was silent
            execution_status=ledger.EXECUTION_OK,
            commands_executed=count_commands(commands_text) - 3,
            referee_sha256=PRE_REPAIR_REFEREE_SHA256,
            instrument_version="i30-fixture-referee/1"))
    return cand, _static_parent("m040-parent", b1, 4)


def fixture_unsupported_command_event():
    """I30R2-8: the REPAIRED referee's retained `unsupported_verb` error."""
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    own0 = U(0, 0, OWN_DOOR)
    seed0 = U(0, 0, OWN_DOOR, C(banana=1))
    b1 = B([seed0, U(9, 1, OPP_BANK)])
    blocks = [b1] + [B([own0, U(9, 1, OPP_BANK)], [banana]) for _ in range(2)]
    cmds = [PLANT_BANANA, "WAIT", "WAIT"]
    cand = record("unsupported-candidate", blocks, cmds, bot=CANDIDATE_BOT,
                  claimed=True,
                  execution=execution_block(
                      "\n".join(cmds) + "\n",
                      execution_status="unsupported_verb",
                      unsupported_command_events=1))
    return cand, _static_parent("unsupported-parent", b1, 3)


def fixture_referee_version_skew():
    """I30R2-8: the two sides of the pair were executed by different referees."""
    banana = P("BANANA", OWN_DOOR, cooldown=6)
    own0 = U(0, 0, OWN_DOOR)
    seed0 = U(0, 0, OWN_DOOR, C(banana=1))
    b1 = B([seed0, U(9, 1, OPP_BANK)])
    blocks = [b1] + [B([own0, U(9, 1, OPP_BANK)], [banana]) for _ in range(2)]
    cmds = [PLANT_BANANA, "WAIT", "WAIT"]
    cand = record("skew-candidate", blocks, cmds, bot=CANDIDATE_BOT,
                  claimed=True)
    par_cmds = ["WAIT"] * 3
    par = record("skew-parent", [list(b1) for _ in range(3)], par_cmds,
                 bot=PARENT_BOT, claimed=True,
                 execution=execution_block(
                     "\n".join(par_cmds) + "\n",
                     referee_sha256=PRE_REPAIR_REFEREE_SHA256))
    return cand, par


# --- I30R2-7: one fixture per frozen activation cause ----------------------

def _banana_asset_pair(run_prefix, cand_blocks, n_turns, cmds=None):
    b1 = cand_blocks[0]
    cmds = cmds or ["WAIT"] * len(cand_blocks)
    cand = record("%s-candidate" % run_prefix, cand_blocks, cmds,
                  bot=CANDIDATE_BOT, claimed=True)
    return cand, _static_parent("%s-parent" % run_prefix, b1, n_turns)


def fixture_activation_banana_harvest():
    """A candidate that changes only HARVEST timing emits no new command."""
    ripe = P("BANANA", (6, 5), fruits=1, cooldown=0)
    bare = P("BANANA", (6, 5), cooldown=0)
    own = U(0, 0, OWN_DOOR)
    blocks = [
        B([own, U(9, 1, (6, 5))], [ripe]),
        B([own, U(9, 1, (6, 5), C(banana=1))], [bare]),
        B([own, U(9, 1, (6, 5), C(banana=1))], [bare]),
    ]
    return _banana_asset_pair("act-harvest", blocks, 3)


def fixture_activation_banana_chop():
    """A candidate that chops an EXISTING banana plants nothing."""
    big = P("BANANA", (6, 5), size=2, health=3, cooldown=0)
    small = P("BANANA", (6, 5), size=1, health=3, cooldown=0)
    own = U(0, 0, OWN_DOOR)
    blocks = [
        B([own, U(9, 1, (6, 5))], [big]),
        B([own, U(9, 1, (6, 5), C(wood=1))], [small]),
        B([own, U(9, 1, (6, 5), C(wood=1))], [small]),
    ]
    return _banana_asset_pair("act-chop", blocks, 3)


def fixture_activation_controller_state():
    """Entering a Banana controller state without planting anything."""
    blocks = _quiet_blocks()
    cmds = ["WAIT"] * 4
    cand = record("act-ctrl-candidate", blocks, cmds, bot=CANDIDATE_BOT,
                  claimed=True, claimed_mechanisms=("controller_state",),
                  activation_telemetry={"controller_states":
                                        [[2, "BANANA_RING_HOLD"]]})
    par = record("act-ctrl-parent", blocks, cmds, bot=PARENT_BOT,
                 activation_telemetry={"controller_states": []})
    return cand, par


def fixture_activation_integration_seam():
    """A declared integration-seam divergence."""
    blocks = _quiet_blocks()
    cmds = ["WAIT"] * 4
    cand = record("act-seam-candidate", blocks, cmds, bot=CANDIDATE_BOT,
                  claimed=True, claimed_mechanisms=("integration_seam",),
                  activation_telemetry={"seam_signature": "banana-seam-v2"})
    par = record("act-seam-parent", blocks, cmds, bot=PARENT_BOT,
                 activation_telemetry={"seam_signature": "banana-seam-v1"})
    return cand, par


def fixture_claimed_controller_state_without_telemetry():
    """A claimed telemetry mechanism with no telemetry bound to it.

    Revision 2 would answer NOT_APPLICABLE, which is exactly the fabricated
    negative the review forbids.
    """
    blocks = _quiet_blocks()
    cmds = ["WAIT"] * 4
    cand = record("act-unbound-candidate", blocks, cmds, bot=CANDIDATE_BOT,
                  claimed=True, claimed_mechanisms=("controller_state",))
    par = record("act-unbound-parent", blocks, cmds, bot=PARENT_BOT)
    return cand, par


# cause -> the fixture that exercises it (review I30R2-7 requires one each)
ACTIVATION_CAUSE_FIXTURES = {
    "banana_command": "fixture_04_direct_theft",
    "own_banana_plant": "fixture_04_direct_theft",
    "banana_harvest": "fixture_activation_banana_harvest",
    "banana_chop": "fixture_activation_banana_chop",
    "banana_banking": "fixture_baseline_stock_recycling",
    "controller_state": "fixture_activation_controller_state",
    "integration_seam": "fixture_activation_integration_seam",
}


# --------------------------------------------------------------------------
# bound objects (spec sec. 11)
# --------------------------------------------------------------------------

# Fixture ids for the parameterised fixtures whose non-default variants the
# bare `dir(fx)` sweep would otherwise miss.
PARAMETERISED_VARIANTS = (
    ("fixture_a3_class_swap[opponent_first]", "fixture_a3_class_swap",
     ("opponent_first",)),
    ("fixture_a5_planter_occupancy[absent]", "fixture_a5_planter_occupancy",
     ("absent",)),
)


# NOT an owner decision. No `OwnerAuthority` can resolve
# `owner_decision_path`, so this object can never produce a PASS and -- since
# revision 3 -- can never produce a production FAIL either: it is measured and
# reported as NON_PRODUCTION_MEASUREMENT (review I30R2-3).
TEST_BOUND_WINDFALL = {
    "schema_version": ledger.SCHEMA_VERSION,
    "population": "banana_active",
    # ruling D1 change 4: the metric name states net, not just "windfall"
    "metric": "mean_schedule_windfall_net",
    "operator": "<=",
    "threshold": 0,
    "family_constraints": [],
    "tail_constraints": [],
    "owner_decision_path": "UNRESOLVED/no-owner-decision-exists",
    "owner_decision_blob": "0" * 64,
    "provenance": "test_fixture",
}
# revision-2 name, kept so the r2 bite-tests still address the same object
TEST_BOUND_ZERO_WINDFALL = TEST_BOUND_WINDFALL

# `I30_REPO_ROOT` lets the mutation runner point a scratch copy of these
# modules at the real repository, whose git refs are an INPUT to the
# provenance manifest and to the owner authority.
REPO_ROOT = os.environ.get("I30_REPO_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# The instant the fixture corpus was observed. An owner decision frozen after
# this instant is not a bound (review I30R2-3).
OBSERVED_UTC = "2026-08-09T00:00:00Z"
TEST_AUTHORITY_ID = "i30-test-owner"
TEST_AUTHORITY_REF = "refs/i30-test/owner-decisions"
TEST_DECISION_PREFIX = "coordination/decisions/i30-test-bound-"
TEST_DECISION_FROZEN_UTC = "2026-08-08T12:00:00Z"

_OWNER_FIELDS = ("owner_decision_path", "owner_decision_blob")


def _bound_body_sha(spec):
    """sha256 over the bound MINUS its own decision pointer.

    The decision names the body and the body names the decision, so one of the
    two links must be over a projection; the decision pointer is the natural
    one to drop.
    """
    body = {k: v for k, v in spec.items() if k not in _OWNER_FIELDS}
    return ledger.sha256_text(ledger.canonical_json(body))


def _decision_bytes(body_sha, authority_id=TEST_AUTHORITY_ID,
                    frozen_utc=TEST_DECISION_FROZEN_UTC):
    return (ledger.canonical_json({
        "decision_id": "i30-test-bound-%s" % body_sha[:12],
        "invariant": "I-30",
        "authority": authority_id,
        "bound_body_sha256": body_sha,
        "frozen_utc": frozen_utc,
        "statement": "TEST authority only. Not an owner decision on the real "
                     "I-30 bound; it exists so the verification chain itself "
                     "can be exercised.",
    }) + "\n").encode("utf-8")


def owner_verified_bound(**overrides):
    """A bound that a (test) authority really did freeze, first.

    Used to prove that the aggregate CAN reach PASS and FAIL once the chain is
    complete -- the production authority resolves nothing, so the real corpus
    stays GATE_UNREADY.
    """
    import i30_analyzer as an

    spec = dict(TEST_BOUND_WINDFALL)
    spec.update(overrides)
    spec["provenance"] = "owner_decision_ref"
    body_sha = _bound_body_sha(spec)
    spec["owner_decision_path"] = TEST_DECISION_PREFIX + body_sha + ".json"
    spec["owner_decision_blob"] = ledger.sha256_bytes(
        _decision_bytes(body_sha))
    return an.Bound(spec)


def tampered_bound(**overrides):
    """A bound EDITED after its decision was frozen.

    The decision pointer still resolves and the blob still matches; what no
    longer matches is the bound the owner actually named.
    """
    import i30_analyzer as an

    original = owner_verified_bound()
    spec = dict(original.spec)
    spec.update(overrides)          # decision pointer deliberately untouched
    return an.Bound(spec)


def test_authority(corrupt=False, authority_id=TEST_AUTHORITY_ID,
                   frozen_utc=TEST_DECISION_FROZEN_UTC):
    """An `OwnerAuthority` standing in for a real owner ref.

    It serves the decision for whichever bound body is asked for, so a test
    can vary the bound without hand-maintaining blobs. `corrupt=True` serves
    bytes that are not the ones the bound pinned.
    """
    import i30_analyzer as an

    def loader(path):
        if not path or not path.startswith(TEST_DECISION_PREFIX):
            return None
        body_sha = path[len(TEST_DECISION_PREFIX):-len(".json")]
        blob = _decision_bytes(body_sha, authority_id=TEST_AUTHORITY_ID,
                               frozen_utc=frozen_utc)
        return blob + b"tampered\n" if corrupt else blob

    return an.OwnerAuthority(loader, TEST_AUTHORITY_REF, authority_id)
