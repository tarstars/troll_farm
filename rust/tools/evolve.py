#!/usr/bin/env python3
"""Parallel Monte-Carlo weight evolution for the schedbot market policy.

(mu+lambda) evolution: each generation screens a POPULATION of mutants
CONCURRENTLY at low seed count, then confirms the best at high seed count
before acceptance (screen noise ~±4, confirm noise ~±2). Robustness floor:
must hold >=55% vs mybot (contested-strength archetype).
"""
import random, subprocess, os, json, time
from concurrent.futures import ThreadPoolExecutor

BIN = os.path.join(os.path.dirname(__file__), "..", "target", "release")
SCREEN_SEEDS = 120
CONFIRM_SEEDS = 400
POP = 6
FLOOR_MYBOT = 0.55

SPACE = {
    "SB_FB":       (0.4, 1.6, False),
    "SB_PRINT":    (4.0, 18.0, False),
    "SB_ORCH_V":   (4.0, 18.0, False),
    "SB_NEED_W":   (0.0, 2.5, False),
    "SB_RETW":     (0.0, 1.0, False),
    "SB_LIQ_T":    (60, 300, True),
    "SB_WF_MAX":   (6, 16, True),
    "SB_MOW_R":    (3, 6, True),
    "SB_CROP_RES": (4, 12, True),
    "SB_LATE_FREE":(40, 140, True),
}
BASE = {"SB_FB":0.8,"SB_PRINT":9.0,"SB_ORCH_V":10.0,"SB_NEED_W":1.0,"SB_RETW":0.5,
        "SB_LIQ_T":280,"SB_WF_MAX":10,"SB_MOW_R":4,"SB_CROP_RES":8,"SB_LATE_FREE":80}

def envof(cfg):
    e = os.environ.copy()
    for k, v in cfg.items():
        e[k] = str(int(v)) if SPACE[k][2] else f"{v:.3f}"
    return e

def density(cfg, seeds):
    out = subprocess.run([os.path.join(BIN,"diag"),"schedbot","printerbot",str(seeds)],
                         env=envof(cfg), capture_output=True, text=True, timeout=900).stdout
    for line in out.splitlines():
        if line.startswith("schedbot"):
            return float(line.split()[1])
    return 0.0

def mybot_wr(cfg):
    out = subprocess.run([os.path.join(BIN,"bench"),"schedbot","mybot","250"],
                         env=envof(cfg), capture_output=True, text=True, timeout=900).stdout
    for line in out.splitlines():
        if "schedbot:" in line and "wins" in line:
            return float(line.split("(")[1].split("%")[0]) / 100.0
    return 0.0

def mutate(cfg, scale):
    c = dict(cfg)
    for k in random.sample(list(SPACE), k=random.randint(1, 3)):
        lo, hi, isint = SPACE[k]
        v = c[k] + random.uniform(-1, 1) * (hi - lo) * scale
        v = max(lo, min(hi, v))
        c[k] = int(round(v)) if isint else v
    return c

def main():
    random.seed(int(time.time()))
    best = dict(BASE)
    best_d = density(best, CONFIRM_SEEDS)
    print(f"base confirmed density={best_d:.1f}", flush=True)
    gen = 0
    t0 = time.time()
    logpath = os.path.join(os.path.dirname(__file__), "evolve_log.json")
    while time.time() - t0 < 3600 * 3:
        gen += 1
        scale = 0.5 if gen % 5 == 0 else 0.2
        pop = [mutate(best, scale) for _ in range(POP)]
        with ThreadPoolExecutor(max_workers=3) as ex:
            scores = list(ex.map(lambda c: density(c, SCREEN_SEEDS), pop))
        top_i = max(range(POP), key=lambda i: scores[i])
        note = f"screen best {scores[top_i]:.1f}"
        if scores[top_i] > best_d + 1.0:
            conf = density(pop[top_i], CONFIRM_SEEDS)
            note += f" -> confirm {conf:.1f}"
            if conf > best_d + 0.5:
                wr = mybot_wr(pop[top_i])
                if wr >= FLOOR_MYBOT:
                    best, best_d = pop[top_i], conf
                    note += f" ACCEPT (mybot {wr:.0%})"
                else:
                    note += f" reject floor ({wr:.0%})"
        print(f"gen {gen}: {note} | best={best_d:.1f}", flush=True)
        with open(logpath, "w") as f:
            json.dump({"best": best, "best_density": best_d, "gen": gen}, f, indent=1)
    print(f"FINAL best={best_d:.1f}\n{json.dumps(best, indent=1)}", flush=True)

if __name__ == "__main__":
    main()
