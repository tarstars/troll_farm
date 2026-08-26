"""Four-verb vs five-verb work set: what changes if HARVEST is dropped (archive read, no re-run)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath("idleprobe.py")))
import idleprobe as IP
from fixprobe import unit_command

res = {}
for name, work in (("five", ("CHOP","HARVEST","DROP","PLANT","PICK")),
                   ("four", ("CHOP","DROP","PLANT","PICK"))):
    IP.WORK = work
    import fixprobe; fixprobe.WORK = work
    IP.WINDOWS = (20,)
    out = IP.analyse(sys.argv[1])
    fired = [e for e in out if e["fires"]["idle20"] is not None]
    games = sorted({(e["map_id"], e["seat"]) for e in fired})
    removed = sum(sum(t["work"].values()) for e in fired
                  if e["tails"]["idle20"] for t in [e["tails"]["idle20"]])
    m061 = sorted((e["seat"], e["fires"]["idle20"]) for e in fired if e["map_id"] == "m061")
    res[name] = {"runs_cut": len(fired), "games": [f"{m}:{s}" for m, s in games],
                 "n_games": len(games), "work_commands_removed": removed, "m061_fires": m061}
json.dump(res, open(sys.argv[2], "w"), indent=1, sort_keys=True)
print(json.dumps(res, indent=1, sort_keys=True))
