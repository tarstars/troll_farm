#!/usr/bin/env python3
"""Parse raw Troll Farm replays (data/raw/games/*.json) into the processed dataset.

Outputs (relative to data/):
    processed/games.jsonl           one line per game (metadata + per-player features)
    processed/maps.jsonl            unique maps (deduped by terrain-row hash)
    processed/trajectories/<id>.jsonl  one record per turn {t, inv0, inv1, commands0, commands1}
    processed/parse_failures.json   games that failed to parse and why
    processed/stats.json            dataset-level counts (used by README)

Replay format knowledge (reverse-engineered + cross-checked against sim/, see README):
  * frames[0].view = " 0\n" + JSON {global:{inputmodule:"W H\nrow0\n..."}, frame:{...}}
    - global.inputmodule: terrain grid. '0'/'1' shacks, '.' walkable, '+' iron,
      '~' water, '#' rock.
    - frame.diff: initial entities: "ID W <id><x><y><player><ms><cc><hp><chop>" trolls,
      "ID P <x><y><type><stage><cur_cd><health><cd_eff>" trees (base-36 chars).
      type: 0=PLUM 1=LEMON 2=APPLE 3=BANANA; stage=size+fruits (MAX_SIZE=4,
      MAX_FRUITS=3 -> size=min(stage,4), fruits=max(0,stage-4)); cd_eff = growth
      cooldown after water adjustment.
    - frame.inputmodule: "<inv player0>\n<inv player1>" at game start.
  * frames[i>0]: agentId = acting player index (0/1); stdout = that player's raw
    commands for the turn; keyframe frames carry view JSON whose inputmodule has
    both players' inventories AFTER the turn resolved.
  * inventory order: PLUM LEMON APPLE BANANA IRON WOOD.
    game score = PLUM+LEMON+APPLE+BANANA + 4*WOOD (verified vs scores[]).
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent
RAW = DATA / "raw"
PROC = DATA / "processed"
TRAJ = PROC / "trajectories"

TYPES = {0: "PLUM", 1: "LEMON", 2: "APPLE", 3: "BANANA"}
ITEMS = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"]
MAX_SIZE, MAX_FRUITS = 4, 3
VERBS = ("MOVE", "HARVEST", "CHOP", "DROP", "MINE", "PLANT", "PICK", "TRAIN",
         "WAIT", "MSG")


def b36(c: str) -> int:
    return int(c, 36)


def score_of(inv) -> int:
    return sum(inv[:4]) + 4 * inv[5]


# ── frame-0 decoding ─────────────────────────────────────────────────────────

def parse_frame0(view: str):
    j = json.loads(view.split("\n", 1)[1])
    grid = j["global"]["inputmodule"].split("\n")
    w, h = (int(v) for v in grid[0].split())
    rows = grid[1:]
    assert len(rows) == h and all(len(r) == w for r in rows), "grid shape mismatch"
    shacks, iron, water = {}, [], []
    counts = Counter()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            counts[ch] += 1
            if ch == "0":
                shacks["p0"] = [x, y]
            elif ch == "1":
                shacks["p1"] = [x, y]
            elif ch == "+":
                iron.append([x, y])
            elif ch == "~":
                water.append([x, y])
    trees, trolls = [], []
    for ent in j["frame"].get("diff", "").split(";"):
        p = ent.split()
        if len(p) != 3:
            continue
        _eid, kind, val = p
        if kind == "P" and len(val) == 7:
            x, y, t, stage, cur_cd, health, cd_eff = (b36(c) for c in val)
            trees.append({
                "type": TYPES.get(t, str(t)), "x": x, "y": y,
                "size": min(stage, MAX_SIZE), "fruits": max(0, stage - MAX_SIZE),
                "stage": stage, "health": health, "cur_cd": cur_cd, "cd_eff": cd_eff,
            })
        elif kind == "W" and len(val) == 8:
            uid, x, y, pl, ms, cc, hp, chop = (b36(c) for c in val)
            trolls.append({"id": uid, "player": pl, "x": x, "y": y,
                           "ms": ms, "cc": cc, "hp": hp, "chop": chop})
    inv_lines = j["frame"].get("inputmodule", "").split("\n")
    inv0 = [int(v) for v in inv_lines[0].split()] if len(inv_lines) == 2 else None
    inv1 = [int(v) for v in inv_lines[1].split()] if len(inv_lines) == 2 else None
    map_obj = {
        "w": w, "h": h, "rows": rows, "shacks": shacks,
        "iron": iron, "water": water,
        "counts": {"walkable": counts["."], "rock": counts["#"],
                   "iron": counts["+"], "water": counts["~"]},
        "trees0": trees,
    }
    return map_obj, trolls, inv0, inv1


# ── per-turn extraction ──────────────────────────────────────────────────────

def extract_turns(frames, inv0_init, inv1_init):
    """Return list of {t, inv0, inv1, commands0, commands1}.

    inv = inventories at the START of the turn (what the players saw);
    commands = the raw stdout each player emitted that turn (None if silent).
    Also returns final inventories (after the last resolved turn).
    """
    turns = []
    cur = {0: [], 1: []}
    inv_before = (inv0_init, inv1_init)
    t = 1
    final_inv = (inv0_init, inv1_init)
    for f in frames[1:]:
        a = f.get("agentId")
        so = f.get("stdout")
        if so is not None and a in (0, 1):
            cur[a].append(so.rstrip("\n"))
        view = f.get("view") or ""
        if f.get("keyframe") and "{" in view:
            j = json.loads(view.split("\n", 1)[1])
            lines = (j.get("inputmodule") or "").split("\n")
            if len(lines) == 2:
                inv_after = tuple([int(v) for v in ln.split()] for ln in lines)
            else:  # keyframe without inventories (shouldn't happen)
                inv_after = final_inv
            turns.append({
                "t": t,
                "inv0": inv_before[0], "inv1": inv_before[1],
                "commands0": "\n".join(cur[0]) if cur[0] else None,
                "commands1": "\n".join(cur[1]) if cur[1] else None,
            })
            final_inv = inv_after
            inv_before = inv_after
            cur = {0: [], 1: []}
            t += 1
    return turns, final_inv


# ── per-player features ──────────────────────────────────────────────────────

def player_features(turns, frames, final_inv):
    feats = {}
    for p in (0, 1):
        verb_counts = Counter()
        trains = []
        plants_cmd = Counter()
        for rec in turns:
            cmds = rec[f"commands{p}"]
            if not cmds:
                continue
            for cmd in re.split(r"[;\n]", cmds):
                cmd = cmd.strip()
                if not cmd:
                    continue
                verb = cmd.split()[0].upper()
                verb_counts[verb if verb in VERBS else "OTHER"] += 1
                if verb == "TRAIN":
                    m = re.match(r"TRAIN\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", cmd)
                    if m:
                        trains.append([rec["t"], [int(g) for g in m.groups()]])
                elif verb == "PLANT":
                    m = re.match(r"PLANT\s+\S+\s+(\w+)", cmd)
                    if m:
                        plants_cmd[m.group(1).upper()] += 1
        feats[str(p)] = {
            "commands_summary": dict(verb_counts),
            "trains": trains,
            "plants_by_type": dict(plants_cmd),
        }

    # effected actions, from referee summaries ($0:/$1: prefixed lines)
    eff = {0: Counter(), 1: Counter()}
    planted = {0: Counter(), 1: Counter()}
    harvested = {0: Counter(), 1: Counter()}
    for f in frames:
        s = f.get("summary")
        if not s:
            continue
        for line in s.split("\n"):
            m = re.match(r"\$([01]): (.*)", line)
            if not m:
                continue
            p, msg = int(m.group(1)), m.group(2)
            if msg.startswith("[failed]"):
                eff[p]["failed"] += 1
                continue
            mm = re.search(r"planted a (\w+)", msg)
            if mm:
                planted[p][mm.group(1)] += 1
                continue
            mm = re.search(r"harvested (\d+) (\w+)", msg)
            if mm:
                harvested[p][mm.group(2)] += int(mm.group(1))
                continue
            mm = re.search(r"(collected|picked|mined|dropped) (\d+) (\w+)", msg)
            if mm:
                eff[p][f"{mm.group(1)}_{mm.group(3)}"] += int(mm.group(2))
                continue
            if "trained a troll" in msg:
                eff[p]["trained"] += 1
            elif "damaged a tree" in msg:
                eff[p]["chops_landed"] += 1

    # curves (end-of-turn state; entry is None if the game ended before that turn)
    def at_turn(tt, p):
        # inventory AFTER turn tt == inv at start of turn tt+1, or final_inv
        if tt < len(turns):
            return turns[tt]["inv0" if p == 0 else "inv1"]
        if tt == len(turns):
            return final_inv[p]
        return None

    for p in (0, 1):
        inv_c = [at_turn(tt, p) for tt in (100, 200, 300)]
        feats[str(p)]["wood_curve"] = [iv[5] if iv else None for iv in inv_c]
        feats[str(p)]["score_curve"] = [
            (score_of(iv) if (iv := at_turn(tt, p)) else None)
            for tt in (50, 100, 150, 200, 250, 300)
        ]
        feats[str(p)]["effects"] = dict(eff[p])
        feats[str(p)]["planted_ok"] = dict(planted[p])
        feats[str(p)]["harvested"] = dict(harvested[p])
        feats[str(p)]["final_inv"] = list(final_inv[p]) if final_inv[p] else None
    return feats


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    TRAJ.mkdir(parents=True, exist_ok=True)
    # league lookup for every leaderboard user (userId -> league info)
    lb = json.loads((RAW / "leaderboard.json").read_text())
    by_user = {}
    for u in lb["users"]:
        uid = u.get("codingamer", {}).get("userId")
        if uid:
            by_user[uid] = {"leagueIndex": u.get("league", {}).get("divisionIndex"),
                            "globalRank": u.get("rank"), "arenaScore": u.get("score")}
    league_names = {0: "Wood2", 1: "Wood1", 2: "Bronze", 3: "Silver", 4: "Gold",
                    5: "Legend"}

    maps = {}          # hash -> map record
    failures = {}
    games_out = []
    files = sorted((RAW / "games").glob("*.json"))
    for fp in files:
        gid = fp.stem
        try:
            r = json.loads(fp.read_text())
            frames = r["frames"]
            map_obj, trolls0, inv0, inv1 = parse_frame0(frames[0]["view"])
            turns, final_inv = extract_turns(frames, inv0, inv1)
            feats = player_features(turns, frames, final_inv)

            players = []
            for a in r.get("agents", []):
                cg = a.get("codingamer") or {}
                uid = cg.get("userId")
                lg = by_user.get(uid, {})
                boss = a.get("arenaboss")
                players.append({
                    "index": a.get("index"),
                    "agentId": a.get("agentId"),
                    "name": cg.get("pseudo") or (boss or {}).get("nickname")
                            or ("BOSS" if boss else "?"),
                    "isBoss": boss is not None,
                    "league": league_names.get(lg.get("leagueIndex")),
                    "leagueIndex": lg.get("leagueIndex"),
                    "arenaScore": lg.get("arenaScore"),
                })

            mh = hashlib.sha1("\n".join(map_obj["rows"]).encode()).hexdigest()[:16]
            if mh not in maps:
                tc = Counter(t["type"] for t in map_obj["trees0"])
                maps[mh] = {
                    "map_hash": mh, "w": map_obj["w"], "h": map_obj["h"],
                    "rows": map_obj["rows"], "shacks": map_obj["shacks"],
                    "counts": map_obj["counts"],
                    "iron_cells": map_obj["iron"], "water_cells": map_obj["water"],
                    "tree_total": len(map_obj["trees0"]),
                    "tree_counts": dict(tc),
                    "trees0": map_obj["trees0"],
                    "n_games": 0, "gameIds": [],
                }
            maps[mh]["n_games"] += 1
            if len(maps[mh]["gameIds"]) < 10:
                maps[mh]["gameIds"].append(int(gid))

            game_rec = {
                "gameId": int(gid),
                "players": players,
                "scores": r.get("scores"),
                "ranks": r.get("ranks"),
                "n_turns": len(turns),
                "map_hash": mh,
                "map": {**{k: map_obj[k] for k in
                           ("w", "h", "rows", "shacks", "iron", "water", "trees0")}},
                "trolls0": trolls0,
                "per_player": feats,
            }
            games_out.append(game_rec)

            with open(TRAJ / f"{gid}.jsonl", "w") as tf:
                for rec in turns:
                    tf.write(json.dumps(rec, separators=(",", ":")) + "\n")
        except Exception as e:  # noqa: BLE001
            failures[gid] = f"{type(e).__name__}: {e}"

    games_out.sort(key=lambda g: g["gameId"])
    with open(PROC / "games.jsonl", "w") as f:
        for g in games_out:
            f.write(json.dumps(g, separators=(",", ":")) + "\n")
    with open(PROC / "maps.jsonl", "w") as f:
        for m in sorted(maps.values(), key=lambda m: -m["n_games"]):
            f.write(json.dumps(m, separators=(",", ":")) + "\n")
    (PROC / "parse_failures.json").write_text(json.dumps(failures, indent=1))

    # dataset stats for the README
    n_players = len({p["agentId"] for g in games_out for p in g["players"]})
    pseudos = sorted({p["name"] for g in games_out for p in g["players"]})
    boss_games = sum(any(p["isBoss"] for p in g["players"]) for g in games_out)
    stats = {
        "games_raw": len(files),
        "games_parsed": len(games_out),
        "parse_failures": len(failures),
        "unique_maps": len(maps),
        "unique_agents": n_players,
        "unique_names": len(pseudos),
        "names": pseudos,
        "boss_games": boss_games,
        "turn_hist": dict(Counter(g["n_turns"] for g in games_out)),
        "map_dims": dict(Counter(f'{m["w"]}x{m["h"]}' for m in maps.values())),
    }
    (PROC / "stats.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps({k: v for k, v in stats.items() if k != "names"}, indent=1))


if __name__ == "__main__":
    main()
