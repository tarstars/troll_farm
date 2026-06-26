from bot.main import decide, PARAMS, State, Troll, Tree


def _bronze_state(inv, turn=1):
    walkable = {(x, 0) for x in range(8)} | {(x, 1) for x in range(8)}
    troll = Troll(id=0, x=0, y=1, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carry=[0]*6, chop_power=1)
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(7, 0),
                 my_inventory=list(inv), opp_inventory=[0]*6,
                 trees=[Tree("PLUM", 3, 1, 1, 6, 0, 0),
                        Tree("APPLE", 5, 1, 1, 6, 0, 0)],
                 my_trolls=[troll], opp_trolls=[], turn=turn,
                 iron_cells=frozenset({(2, 0)}))


def test_decide_runs_and_emits_commands_without_forced_policy():
    cmds = decide(_bronze_state([5, 5, 5, 0, 5, 0]), PARAMS)
    assert isinstance(cmds, list) and cmds            # non-empty, no crash


def test_no_planting_command_by_default():
    # v1 core: planning replaces the orchard churn -> no PLANT emitted.
    cmds = decide(_bronze_state([5, 5, 5, 5, 5, 0]), PARAMS)
    assert not any(c.startswith("PLANT") for c in cmds)


def test_late_game_emits_no_train():
    cmds = decide(_bronze_state([30, 30, 30, 0, 30, 0], turn=296), PARAMS)
    assert not any(c.startswith("TRAIN") for c in cmds)


def test_opening_trains_chopper_first_in_bronze():
    # Wood is the dominant economy, so the opening floor builds a CHOPPER first
    # (chop>0) when iron terrain is present and one is affordable now.
    cmds = decide(_bronze_state([5, 5, 5, 0, 5, 0]), PARAMS)
    train = [c for c in cmds if c.startswith("TRAIN")]
    assert train and train[0].split()[-1] != "0"   # chop > 0


def test_opening_falls_back_to_gatherer_when_chopper_unaffordable():
    # Some iron (>=1 for a gatherer) but < the chopper's IRON cost (5): the
    # opening trains the cheap gatherer instead of stalling.
    cmds = decide(_bronze_state([5, 5, 5, 0, 2, 0]), PARAMS)
    assert "TRAIN 1 1 1 0" in cmds


def test_opening_floor_skipped_under_forced_policy():
    # The correlation gate forces a build order; the opening floor must NOT
    # override it, or the sim would stop following the forced policy.
    p = dict(PARAMS)
    p["forced_policy"] = [(1, 3, 0, 2)]      # expensive chopper, unaffordable now
    cmds = decide(_bronze_state([5, 5, 5, 0, 5, 0]), p)
    assert not any(c == "TRAIN 1 1 1 0" for c in cmds)
