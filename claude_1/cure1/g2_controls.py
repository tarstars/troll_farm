#!/usr/bin/env python3
"""Controls on the G-2 grade — the checks that would catch me if the grade were wrong.

Task `20260825-dance-cure-candidate-1-hold`, G-2.  `g2_grade.py` produces the numbers; this
produces the reasons to believe them, and each control is reported with its own number rather
than as a word.

  K-DET  determinism — the grade re-run is byte-identical to the published one.
  K-IND  independent recomputation of the branch census by a DIFFERENT path: a regex over each
         replay frame's raw stdout, joined to the seat from the replay's `agents` array, with no
         adapter, no trace, no join and no roster check.  It must reproduce H/L/P/R/W/N exactly.
  K-X    the structure of the `R_pos` vs `r=R` disagreement: are the R_pos-only rows the rows
         where the BFS map has no entry for a cell and the arm's own Manhattan fallback decides?
         A disagreement with a known mechanism is a different object from an unexplained one.
  K-CH   the champion corpus under the identical long-stall function, so the kill rule's
         comparison is measured rather than asserted.
  K-PW   clause (a)'s power: the exact binomial interval on 11/25 and Fisher's exact test against
         the v3 instrument's 52/80.  This does NOT move the grade — the bar was pre-committed and
         the read is under it — it states whether the read could have distinguished the two.

    python3 claude_1/cure1/g2_controls.py
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import re
import subprocess
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (HERE, REPO / "claude_1" / "dance1", REPO / "claude_1" / "adapter1",
           REPO / "claude_1" / "narrate1", REPO / "claude_1" / "narrate4",
           REPO / "claude_1" / "pipeline", REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import g2_grade as g2                      # noqa: E402
import narrate4_join as n4j                # noqa: E402
import regressive_baseline as rb           # noqa: E402
import replay_to_trace as rt               # noqa: E402
import trace_detectors as td               # noqa: E402

GAMES = g2.DEFAULT_GAMES
AGENT = g2.DEFAULT_AGENT
GRADE = g2.OUT
OUT = HERE / "results" / "g2-controls.json"
UNIT_TOKEN = re.compile(r"u(\d+)=([^/\s]+)/([^/\s]+)/r=([PLHRWN])/b=(\d+)")


def load_games():
    with gzip.open(GAMES, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


# --- K-DET ----------------------------------------------------------------

def k_det():
    before = GRADE.read_bytes()
    digest_before = hashlib.sha256(before).hexdigest()
    tmp = GRADE.with_suffix(".rerun.json")
    subprocess.run([sys.executable, str(HERE / "g2_grade.py"), "--out", str(tmp)],
                   check=True, stdout=subprocess.DEVNULL)
    digest_after = hashlib.sha256(tmp.read_bytes()).hexdigest()
    tmp.unlink()
    return {"sha256_published": digest_before, "sha256_rerun": digest_after,
            "result": "PASS" if digest_before == digest_after else "FAIL",
            "criterion": "the grade carries no clock and is written sort_keys=True, so a second "
                         "run is byte-identical or something is reading the environment"}


# --- K-IND ----------------------------------------------------------------

def k_ind():
    """Branch census with no adapter, no trace, no join: regex over raw frame stdout."""
    branches = collections.Counter()
    turns = 0
    for game in load_games():
        agents = game.get("agents") or []
        seat = None
        for index, row in enumerate(agents):
            if int(row.get("agentId", -1)) == AGENT:
                seat = index
        if seat is None:
            raise SystemExit("agent %d absent from a replay's agents array" % AGENT)
        for index, frame in enumerate(game.get("frames") or []):
            if index == 0 or frame.get("agentId") != seat:
                continue
            out = frame.get("stdout") or ""
            if "NARRATE" not in out:
                continue
            turns += 1
            for m in UNIT_TOKEN.finditer(out):
                branches[m.group(4)] += 1
    published = json.loads(GRADE.read_text())["totals"]["branches"]
    ok = dict(branches) == published
    return {"branches_independent": dict(branches), "branches_published": published,
            "narrate_turns_independent": turns,
            "result": "PASS" if ok else "FAIL",
            "criterion": "a second reading of the same wire by a path that shares no code with "
                         "the graded one must produce the identical census"}


# --- K-X ------------------------------------------------------------------

def k_x():
    """Every row where R_pos and r=R disagree, with the reason the measure can see."""
    disagreements = []
    for game in load_games():
        gid = game.get("gameId")
        rows, _jmeta = n4j.decode_game(game, AGENT)
        trace, _ = rt.adapt_to_trace(game, agent_id=AGENT)
        cells = {(r["turn"], r["unit"]): tuple(r["unit_cell"])
                 for r in rows if r["unit_cell"] is not None}
        branch = {(r["turn"], r["unit"]): r["branch"] for r in rows}
        chosen = {(r["turn"], r["unit"]): r["chosen"] for r in rows}
        verdicts = {}
        rb.measure_game(game, AGENT, poison_shift=0, decode=n4j.decode_game,
                        row_sink=lambda t, u, v: verdicts.__setitem__((t, u), v))
        for key, verdict in verdicts.items():
            rp = verdict == "MOVED_REGRESSIVE"
            rr = branch[key] == "R"
            if rp == rr:
                continue
            target = rb.target_cell(chosen[key], trace.tent)
            dmap = td.bfs_distances(trace.smap.walkable, [target])
            here, there = cells.get(key), cells.get((key[0] + 1, key[1]))
            disagreements.append({
                "game": gid, "turn": key[0], "unit": key[1], "branch": branch[key],
                "r_pos": verdict, "chosen": chosen[key],
                "off_bfs_map": bool(here not in dmap or there not in dmap),
                "target_on_bfs_map": bool(target in dmap),
            })
    off_map = sum(1 for d in disagreements if d["off_bfs_map"])
    return {"disagreeing_rows": len(disagreements),
            "r_pos_only": sum(1 for d in disagreements if d["r_pos"] == "MOVED_REGRESSIVE"),
            "r_eq_R_only": sum(1 for d in disagreements if d["branch"] == "R"),
            "explained_by_the_manhattan_fallback": off_map,
            "unexplained": len(disagreements) - off_map,
            "rows": sorted(disagreements, key=lambda d: (d["game"], d["turn"], d["unit"])),
            "criterion": "reported, not gated: a disagreement whose every row sits off the BFS "
                         "map is the fallback's, and says the two labels differ where the "
                         "instrument itself is approximating"}


# --- K-CH -----------------------------------------------------------------

def k_ch(champion_games, champion_manifest):
    if not (champion_games and champion_manifest):
        return {"result": "NOT MEASURED", "reason": "champion package not supplied"}
    row = g2.champion_stalls(Path(champion_games), Path(champion_manifest))
    read = json.loads(GRADE.read_text())["long_stall"]
    row["read_share_pct"] = read["share_pct"]
    row["result"] = ("PASS" if read["share_pct"] <= row["long_stall_share_pct"] else "KILL")
    row["criterion"] = ("the same function on both corpora; the kill rule fires only if the "
                        "read's share is ABOVE the champion's")
    return row


# --- K-PW -----------------------------------------------------------------

def _binom_cdf(k, n, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _clopper_pearson(k, n, alpha=0.05):
    lo, hi = 0.0, 1.0
    for _ in range(200):                      # lower bound: P(X >= k) = alpha/2
        mid = (lo + hi) / 2
        if k == 0 or 1 - _binom_cdf(k - 1, n, mid) < alpha / 2:
            lo = mid
        else:
            hi = mid
    low = lo
    lo, hi = 0.0, 1.0
    for _ in range(200):                      # upper bound: P(X <= k) = alpha/2
        mid = (lo + hi) / 2
        if _binom_cdf(k, n, mid) > alpha / 2:
            lo = mid
        else:
            hi = mid
    return low, lo


def _fisher_two_sided(a, b, c, d):
    """Two-sided Fisher exact p for [[a,b],[c,d]]."""
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def prob(x):
        return (comb(r1, x) * comb(n - r1, c1 - x)) / comb(n, c1)

    p0 = prob(a)
    lo = max(0, c1 - (n - r1))
    hi = min(r1, c1)
    return sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= p0 * (1 + 1e-9))


def k_pw():
    grade = json.loads(GRADE.read_text())
    k, n = grade["clause_a"]["f7_dancer_progress"], grade["clause_a"]["episodes"]
    lo, hi = _clopper_pearson(k, n)
    p = _fisher_two_sided(k, n - k, 52, 80 - 52)
    return {"read": "%d of %d" % (k, n), "share_pct": round(100.0 * k / n, 4),
            "clopper_pearson_95_pct": [round(100 * lo, 2), round(100 * hi, 2)],
            "v3_reference": "52 of 80", "fisher_two_sided_p": round(p, 4),
            "bar_pct": grade["clause_a"]["bar_pct"],
            "bar_inside_the_interval": bool(lo * 100 <= grade["clause_a"]["bar_pct"] <= hi * 100),
            "criterion": "does NOT move the grade — the bar was pre-committed and the read is "
                         "under it. It states what the read can and cannot distinguish."}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--champion-games", default=None)
    ap.add_argument("--champion-manifest", default=None)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)

    report = {"task": "20260825-dance-cure-candidate-1-hold", "gate": "G-2 controls",
              "K-DET determinism": k_det(),
              "K-IND independent branch census": k_ind(),
              "K-X crosswalk structure": k_x(),
              "K-CH champion long-stall": k_ch(args.champion_games, args.champion_manifest),
              "K-PW clause (a) power": k_pw()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    for name, row in report.items():
        if isinstance(row, dict):
            print("%-34s %s" % (name, row.get("result", "reported")))
    x = report["K-X crosswalk structure"]
    print("  crosswalk: %d disagreeing rows, %d explained by the fallback, %d unexplained"
          % (x["disagreeing_rows"], x["explained_by_the_manhattan_fallback"], x["unexplained"]))
    pw = report["K-PW clause (a) power"]
    print("  clause (a): %s = %.2f %%, 95 %% CI %s, Fisher vs 52/80 p = %s"
          % (pw["read"], pw["share_pct"], pw["clopper_pearson_95_pct"],
             pw["fisher_two_sided_p"]))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
