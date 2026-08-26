#!/usr/bin/env python3
"""Kept-goal episodes over the whole Candidate 3 panel — read-only.

An EPISODE is a maximal run of consecutive turns on which one own unit reports `k>0`, i.e.
holds a valid kept goal. Its length is exactly what the wire's `ka` counts (`ka` is the
per-turn maximum over units; an episode is the per-unit object). The episode's END CAUSE is
read from the release census on the first turn the unit reports `k=0`: `rd` done, `rf`/`rt`/`ro`
gone, `ri` impossible, `rx` unit dead, `xc` contested. When more than one release lands on the
same turn the cause is recorded as `ambiguous` rather than guessed.
"""
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "narrate6"))
import narrate6  # noqa: E402

CAUSES = ("rd", "rf", "rt", "ro", "ri", "rx", "xc")


def episodes_for_game(commands_text):
    rows = []
    for index, line in enumerate(commands_text.strip("\n").split("\n"), 1):
        payload = narrate6.msg_fragments(line)[0].strip()
        turn, units, order, banner, meta = narrate6.decode(payload)
        assert turn == index
        rows.append((units, meta))
    live, out = {}, []
    for turn, (units, meta) in enumerate(rows, 1):
        fired = [c for c in CAUSES if meta[c]]
        total = sum(meta[c] for c in CAUSES)
        cause = fired[0] if (len(fired) == 1 and total == 1) else ("none" if total == 0
                                                                  else "ambiguous")
        for uid in list(live):
            if units.get(uid, ("", "", "", 0, "0"))[4] == "0":
                start = live.pop(uid)
                out.append({"unit": uid, "start": start, "end": turn - 1,
                            "length": turn - start, "end_cause": cause, "end_turn": turn})
        for uid, u in units.items():
            if u[4] != "0" and uid not in live:
                live[uid] = turn
    for uid, start in live.items():
        out.append({"unit": uid, "start": start, "end": len(rows), "length": len(rows) - start + 1,
                    "end_cause": "game_end", "end_turn": None})
    return out, rows


def main(archive, out_path):
    games = []
    for line in gzip.open(archive, "rt"):
        d = json.loads(line)
        eps, rows = episodes_for_game(d["artifacts"]["candidate_commands"])
        games.append({"map_id": d["map_id"], "seat": d["seat"], "turns": d["turns"],
                      "class": d["class"], "profile": d["profile"],
                      "own_candidate": d["candidate"]["score"], "own_parent": d["parent"]["score"],
                      "ka_max": max(r[1]["ka"] for r in rows),
                      "episodes": eps})
    json.dump({"archive": archive, "games": games}, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"{len(games)} games -> {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
