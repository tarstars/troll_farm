#!/usr/bin/env python3
"""v1.61.0-chopharvest paired-gate analysis: win rate, wood, train-turn, chopper
opportunistic-harvest count (@TFHARVEST grep by chopper id), ring longevity
(last turn with any ring cell planted, from @TFFARM's ring_planted field, sampled
every 5 turns).
Usage: chopharvest_gate_analyze.py <label> <opp_dir> <game_id> [<game_id> ...]
Reads data/boss5_games/<opp_dir>/game_<id>.raw for each id.
"""
import re, sys, statistics

BOSS5 = "/home/tarstars/prj/troll_farm/data/boss5_games"


def analyze_one(opp_dir, gid):
    try:
        raw = open(f"{BOSS5}/{opp_dir}/game_{gid}.raw").read()
    except FileNotFoundError:
        return None
    # chopper/starter id: NOT in the turn-1 @TFI dump (the chopper trains later) -- read the
    # first @TFSUM mybuilds= entry showing >=2 trolls ("id:ms.cc.hp.chop" per troll, comma-
    # joined) and classify each by its chop field (>=2 -> chopper).
    train_t = None
    chopper_id = starter_id = chopper_hp = None
    for m in re.finditer(r"@TFSUM t=(\d+) .*? mybuilds=(\S*)", raw):
        entries = [e for e in m[2].split(",") if e]
        if len(entries) >= 2:
            train_t = int(m[1])
            for e in entries:
                tid_s, stats = e.split(":")
                ms, cc, hp, chop = (int(x) for x in stats.split("."))
                if chop >= 2:
                    chopper_id, chopper_hp = int(tid_s), hp
                else:
                    starter_id = int(tid_s)
            break
    # harvest counts by actor
    harvest_ids = re.findall(r"@TFHARVEST t=\d+ \[(.*?)\]", raw)
    chopper_harvests = sum(cmds.count(f"HARVEST {chopper_id}") for cmds in harvest_ids) if chopper_id is not None else 0
    starter_harvests = sum(cmds.count(f"HARVEST {starter_id}") for cmds in harvest_ids) if starter_id is not None else 0
    # ring longevity: last turn (of the @TFFARM t%5==0 samples) with ring_planted > 0
    ring_samples = [(int(t), int(rp)) for t, rp in re.findall(r"@TFFARM t=(\d+) .*?ring_planted=(\d+)", raw)]
    last_ring_alive = max((t for t, rp in ring_samples if rp > 0), default=0)
    final_ring_planted = ring_samples[-1][1] if ring_samples else None
    # final wood (last @TFSUM line's myinv[5])
    wood_matches = re.findall(r"@TFSUM t=\d+ .*? myinv=\[([\d,]+)\]", raw)
    final_wood = int(wood_matches[-1].split(",")[5]) if wood_matches else None
    return dict(
        chopper_id=chopper_id, chopper_hp=chopper_hp, train_t=train_t,
        chopper_harvests=chopper_harvests, starter_harvests=starter_harvests,
        last_ring_alive=last_ring_alive, final_ring_planted=final_ring_planted,
        final_wood=final_wood,
    )


def main():
    label, opp_dir = sys.argv[1], sys.argv[2]
    gids = sys.argv[3:]
    rows = []
    for gid in gids:
        r = analyze_one(opp_dir, gid)
        if r is None:
            print(f"  {gid}: MISSING .raw")
            continue
        rows.append(r)
        print(f"  {gid}: chopper#{r['chopper_id']}(hp={r['chopper_hp']}) train_t={r['train_t']} "
              f"chopper_harvests={r['chopper_harvests']} starter_harvests={r['starter_harvests']} "
              f"last_ring_alive_t={r['last_ring_alive']} final_ring_planted={r['final_ring_planted']} "
              f"final_wood={r['final_wood']}")
    if not rows:
        print(f"{label}: NO GAMES PARSED")
        return
    train_ts = [r["train_t"] for r in rows if r["train_t"] is not None]
    chopper_harvests = [r["chopper_harvests"] for r in rows]
    last_ring = [r["last_ring_alive"] for r in rows]
    wood = [r["final_wood"] for r in rows if r["final_wood"] is not None]
    print(f"\n== {label} (n={len(rows)}) ==")
    print(f"   train_turn avg: {statistics.mean(train_ts):.1f}" if train_ts else "   train_turn: NONE")
    print(f"   chopper_harvests avg: {statistics.mean(chopper_harvests):.2f} (total {sum(chopper_harvests)})")
    print(f"   last_ring_alive_t avg: {statistics.mean(last_ring):.1f}")
    print(f"   final_wood avg: {statistics.mean(wood):.1f}" if wood else "   wood: NONE")


if __name__ == "__main__":
    main()
