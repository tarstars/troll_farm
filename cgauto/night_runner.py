#!/usr/bin/env python3
"""Deterministic M-1 paired-night runner — no LLM, laptop-independent.

Executes the per-mark ritual of a paired arena night exactly as specified in
the night ledger: wait out each arm's ~2 h window, take the mature read,
append the ledger row, submit the other arm (fail-closed, via
api_submit_once.py), push, repeat; after the final read compute the
pre-registered verdict arithmetic and stop. State lives in a JSON file next to
the ledger so a restart resumes exactly where it stopped.

Safety posture (unattended): NO automatic retry of submissions. Any anomaly —
submit failure, unparseable read, git push failure after one rebase retry —
writes a HALT block to the ledger, pushes it, and exits nonzero. Losing a
window costs little; an ambiguous double-submission costs the night.

A halt file (NIGHT-HALT in the repo root) stops the runner at the next loop.

Post-B5 decision tree (owner-approved 2026-08-20 ~15:00Z, implemented by
claude_1 against the card 20260820T144705Z-20260819-osc031-night-tree-card.md):
after the final read the verdict is computed exactly as before, and THEN
    |mean| in [1.0, 1.315)  -> M-1's own extension: append pairs A6..B10 to the
                               same plan, same arms, and submit the next arm;
    otherwise               -> open session 3 (Door-1 challenger vs the VERY-OLD
                               resident 98628e98...) in a fresh state + ledger,
                               submit arm A at once, and keep running against
                               the new files in this same process.
Either branch publishes the OWNER MORNING SHEET as a coordination message,
gated on lint_outbox.py's exit status. Fail-closed HALT semantics are
unchanged, and nothing outside the chartered arm files is ever submitted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
RANK_RE = re.compile(
    r"ARENA-ROOM: \S+ rank (\d+)/(\d+) (\S+) score ([\d.]+) .*agentId=(\d+)")
BATTLES_RE = re.compile(r"battles listed: (\d+)")

MIN_WINDOW_MIN = 115          # earliest read, minutes after submission
FORCE_READ_MIN = 170          # read regardless of battle count after this
MATURE_BATTLES = 150
POLL_SECONDS = 180

SIGMA_PAIR = 1.5              # owner-adopted provisional planning value
WINNER_BAR = 1.315            # 1.96 * 1.5/sqrt(5), owner-adopted sigma_pair
MATERIALITY_FLOOR = 1.0
# The bar depends on the block size, and the extension changes the block size.
# Both literals are the pre-registered ones (ledger: "bar 1.315" at n=5,
# "n=10, bar 0.930"); any other n falls back to the same arithmetic. Grading a
# 10-pair block against the 5-pair bar would understate the challenger by a
# third of a point in the one number the owner rules on.
PREREGISTERED_BARS = {5: 1.315, 10: 0.930}


def bar_for(n: int) -> float:
    """1.96 * sigma_pair / sqrt(n), pinned to the pre-registered literals."""
    if n in PREREGISTERED_BARS:
        return PREREGISTERED_BARS[n]
    return round(1.96 * SIGMA_PAIR / n ** 0.5, 3) if n else WINNER_BAR

# --- post-B5 decision tree (owner: "approve the tree", 2026-08-20 ~15:00Z;
# card coordination/messages/local_claude_1/
# 20260820T144705Z-20260819-osc031-night-tree-card.md).  At B5 the verdict is
# computed exactly as before; the tree only decides what happens NEXT.
EXTENSION_PAIRS = 5           # M-1's own extension: append pairs A6..B10
SESSION3_STATE = "local_claude_1/door1-vs-old-2026-08-20-state.json"
SESSION3_LEDGER = "local_claude_1/door1-vs-old-2026-08-20.md"
SESSION3_ARMS = {
    "A": {"label": "A challenger",
          "source": "cgauto/submissions/candidate-door1-pure-deletion.rs",
          "sha256": "547fa706cc1c684a1f8c2a08174792d95e553b2382"
                    "facfe15884d2ef544070b0"},
    "B": {"label": "B very-old resident",
          "source": "cgauto/submissions/"
                    "submitted-agent6593838-readable-no-orchard.rs",
          "sha256": "98628e98dce4a33b4f24308be3111595927b2ea8"
                    "469c94a8d781cc85d41fbc29"},
}
# Night 1 (cure-C minus the very-old resident), for the pre-registered
# composed three-generation comparison.  Owner addendum, fixed 2026-08-20
# ~14:45Z, BEFORE pairs 3-5 of this night existed.
NIGHT1_DELTA = 1.02
NIGHT1_PAIR_SD = 0.976
NIGHT1_N = 5
# The nine named costs travel with every verdict report (exact keys in
# codex_1/reviews/osc031-named-costs-package-review-2026-08-19.md).
NAMED_COSTS_P124 = "m021s0, m040s1?, m063s1, m078s1, m090s1"
NAMED_COSTS_P3 = "m025s0, m035s0, m054s0, m104s0"
TASK_ID = "20260819-osc031-forecast-fix-door1b"
MSG_DIR = "coordination/messages/local_claude_1"


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def stamp(t: dt.datetime | None = None) -> str:
    return (t or utcnow()).strftime("%H:%M:%SZ")


def run(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True,
                          timeout=timeout)


def read_arena() -> dict:
    rank = run([sys.executable, "cgauto/cg_rank.py"])
    battles = run([sys.executable, "cgauto/battles.py", "12"], timeout=240)
    m = RANK_RE.search(rank.stdout)
    b = BATTLES_RE.search(battles.stdout)
    if not m or not b:
        raise RuntimeError(
            f"unparseable read: rank_rc={rank.returncode} "
            f"battles_rc={battles.returncode} out={rank.stdout[:200]!r}")
    return {"rank": int(m.group(1)), "total": int(m.group(2)),
            "league": m.group(3), "score": float(m.group(4)),
            "agent_id": m.group(5), "battles": int(b.group(1)),
            "read_at": stamp()}


def submit(arm: dict) -> dict:
    proc = run([sys.executable, "cgauto/api_submit_once.py", arm["source"],
                "--expected-sha256", arm["sha256"]], timeout=120)
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        payload = {}
    if proc.returncode != 0 or not payload.get("accepted"):
        raise RuntimeError(
            f"submit FAILED rc={proc.returncode} payload={payload!r} "
            f"stderr={proc.stderr[:200]!r}")
    return payload


def git_publish(paths, msg: str) -> None:
    """Commit and push the named paths.  Accepts any number of paths: the
    post-B5 tree publishes a second state/ledger pair and the morning sheet in
    the same commit as the B5 read.

    Three attempts, not two, and a `--rebase` between each: the branch this
    pushes to is the coordinator's, who commits to it while the night runs.
    That is what killed the 15:06Z A3 publish -- the ledger conflicted during
    the single retry's rebase, the second push was still non-fast-forward, and
    the RuntimeError went uncaught, leaving a half-finished rebase and a dead
    service. The ledgers now carry `merge=union` in .gitattributes so an
    append-vs-append conflict resolves itself; this function's job is to leave
    NO half-rebase behind when something else does conflict."""
    run(["git", "add", *[str(p) for p in paths]])
    run(["git", "commit", "-m", msg])
    for attempt in (1, 2, 3):
        push = run(["git", "push", "origin", "agent/local_claude_1"])
        if push.returncode == 0:
            break
        if attempt == 3:
            raise RuntimeError(f"git push failed 3x: {push.stderr[:300]}")
        pull = run(["git", "pull", "--rebase", "origin", "agent/local_claude_1"])
        if pull.returncode != 0:
            run(["git", "rebase", "--abort"])
            raise RuntimeError(
                f"pull --rebase conflicted, rebase aborted: {pull.stdout[:200]} "
                f"{pull.stderr[:200]}")
    run(["git", "push", "origin", "agent/local_claude_1:main"])


def append(ledger: pathlib.Path, text: str) -> None:
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(text)


def halt(state_path, ledger, state, reason: str, publish: bool = True) -> None:
    """Fail-closed stop: write the HALT, publish it, exit nonzero.

    `publish=False` for the one case where publishing is ITSELF what failed --
    pushing again would only raise again, and an uncaught exception there is
    how the 15:06Z crash left a half-rebase and no HALT block at all. The note
    is still written and committed locally, so a human finds it in the file.
    """
    note = (f"\n**HALT {utcnow().isoformat(timespec='seconds')}** — "
            f"night_runner stopped: {reason}. No further mutations; resume "
            f"or rule manually.\n")
    append(ledger, note)
    state["halted"] = reason
    state_path.write_text(json.dumps(state, indent=1))
    try:
        if publish:
            git_publish([state_path, ledger], f"night_runner HALT: {reason[:80]}")
        else:
            run(["git", "add", str(state_path), str(ledger)])
            run(["git", "commit", "-m", f"night_runner HALT (unpushed): {reason[:80]}"])
    finally:
        sys.exit(2)


def pair_stats(state) -> dict:
    """Adjacent-pair differences and their spread — the single arithmetic used
    by the verdict block, the decision tree and the morning sheet."""
    pairs = []
    reads = state["reads"]
    for i in range(0, len(reads) - 1, 2):
        pairs.append(round(reads[i]["score"] - reads[i + 1]["score"], 2))
    n = len(pairs)
    mean = sum(pairs) / n if n else 0.0
    var = sum((p - mean) ** 2 for p in pairs) / (n - 1) if n > 1 else 0.0
    return {"pairs": pairs, "n": n, "mean": mean, "sd": var ** 0.5}


def verdict_block(state) -> str:
    st = pair_stats(state)
    pairs, mean, n, sd = st["pairs"], st["mean"], st["n"], st["sd"]
    bar = bar_for(n)
    if abs(mean) >= bar:
        outcome = ("WINNER: challenger" if mean > 0 else "WINNER: champion")
    elif abs(mean) < MATERIALITY_FLOOR:
        outcome = "IMMATERIAL (below the 1.0 floor)"
    else:
        outcome = "BETWEEN floor and bar -> M-1 prescribes one extension"
    return (f"\n## BLOCK COMPLETE ({utcnow().isoformat(timespec='seconds')}, "
            f"computed by night_runner)\n\n"
            f"- Pairs (A-B): {pairs} -> mean {mean:+.3f}\n"
            f"- Pre-registered arithmetic: sigma_pair {SIGMA_PAIR}, winner bar "
            f"{bar} (n={n}), floor {MATERIALITY_FLOOR}\n"
            f"- Empirical pair SD (honesty clause): {sd:.3f}\n"
            f"- Arithmetic outcome: **{outcome}** — KEEP/REVERT is the "
            f"OWNER'S ruling; the nine named costs travel with this.\n")


# ---------------------------------------------------------------------------
# Post-B5 decision tree
# ---------------------------------------------------------------------------

def post_b5_branch(mean: float, n: int = 5) -> str:
    """`extension` when |mean| is between the floor and the bar for THIS block
    size (M-1's own rule fires), `session3` otherwise — immaterial below 1.0 OR
    a winner at or above the bar.  Pure function: this is the whole
    owner-approved decision.

    At n=10 the bar (0.930) is BELOW the floor (1.0), so the band is empty and
    a second extension can never fire: every outcome is either immaterial or a
    winner.  That is arithmetic, not policy — M-1 permits two extensions and
    the second is simply unreachable."""
    return ("extension" if MATERIALITY_FLOOR <= abs(mean) < bar_for(n)
            else "session3")


def extend_plan(state) -> list:
    """Append pairs A6..B10 to the plan, same arms.  Returns the added rows."""
    first = len(state["plan"]) // 2 + 1
    added = []
    for i in range(first, first + EXTENSION_PAIRS):
        added.append({"label": f"A{i}", "arm": "A"})
        added.append({"label": f"B{i}", "arm": "B"})
    state["plan"].extend(added)
    return added


def session3_state() -> dict:
    """Fresh state for session 3 — Door-1 challenger vs the VERY-OLD resident."""
    plan = []
    for i in range(1, 6):
        plan.append({"label": f"A{i}", "arm": "A"})
        plan.append({"label": f"B{i}", "arm": "B"})
    return {"arms": json.loads(json.dumps(SESSION3_ARMS)),
            "plan": plan, "submissions": [], "reads": []}


def session3_ledger_header(state2_mean: float) -> str:
    return f"""# Door-1 challenger vs the VERY-OLD resident — session 3 ledger

Opened automatically by night_runner at {utcnow().isoformat(timespec='seconds')}
under the owner-approved post-B5 night tree (card
`{MSG_DIR}/20260820T144705Z-20260819-osc031-night-tree-card.md`), because the
session-2 mean {state2_mean:+.3f} did NOT land between the floor and the bar.

Purpose: the owner's composed-comparison **gold standard** — measured directly
instead of composed across nights.  Context estimate from the two measured
nights is about {NIGHT1_DELTA + state2_mean:+.2f}; **no point band is claimed**
and IMMATERIAL is an honest outcome.

## Arms

| arm | source | sha256 |
|---|---|---|
| A = Door-1 challenger (pure deletion) | `{SESSION3_ARMS['A']['source']}` | `{SESSION3_ARMS['A']['sha256']}` |
| B = very-old resident (pre-cure-C) | `{SESSION3_ARMS['B']['source']}` | `{SESSION3_ARMS['B']['sha256']}` |

## Verdict arithmetic (pre-registered, unchanged from session 2)

- Verdict object: 95% CI of the mean adjacent-pair difference D = mean(A_i - B_i).
- sigma_pair {SIGMA_PAIR} -> SE at n=5 = {SIGMA_PAIR / 5 ** 0.5:.3f}, winner bar
  {WINNER_BAR}; materiality floor |D| < {MATERIALITY_FLOOR} -> IMMATERIAL.
- Honesty clause: the empirical pair spread is reported beside the planning value.
- The nine named costs travel with the verdict: {NAMED_COSTS_P124} (P1/P2/P4)
  + {NAMED_COSTS_P3} (P3 orchard divergence).
- KEEP/REVERT is the OWNER'S ruling, never the runner's.

## Read log (times UTC, clock-read)

| # | arm | submitted | submission id | agent id | read time | battles | score | rank |
|---|---|---|---|---|---|---|---|---|
"""


def morning_sheet(state, branch: str, next_note: str) -> tuple[pathlib.Path, str]:
    """The owner morning sheet, in plain words.  Published in EITHER branch."""
    st = pair_stats(state)
    mean, sd, n = st["mean"], st["sd"], st["n"]
    bar = bar_for(n)
    se_plan = SIGMA_PAIR / n ** 0.5
    se_emp = sd / n ** 0.5 if n else 0.0
    se1_plan = SIGMA_PAIR / NIGHT1_N ** 0.5
    se1_emp = NIGHT1_PAIR_SD / NIGHT1_N ** 0.5
    composed = NIGHT1_DELTA + mean
    se_comp_plan = (se1_plan ** 2 + se_plan ** 2) ** 0.5
    se_comp_emp = (se1_emp ** 2 + se_emp ** 2) ** 0.5
    if abs(mean) >= bar:
        verdict = "WINNER: challenger" if mean > 0 else "WINNER: champion"
    elif abs(mean) < MATERIALITY_FLOOR:
        verdict = "IMMATERIAL (below the 1.0 floor)"
    else:
        verdict = "BETWEEN the floor and the bar"
    now = utcnow()
    fname = f"{now.strftime('%Y%m%dT%H%M%SZ')}-{TASK_ID}-progress.md"
    path = pathlib.Path(MSG_DIR) / fname
    body = f"""---
schema_version: 2
type: progress
task_id: {TASK_ID}
from: local_claude_1
to: ["user"]
cc: ["claude_1", "codex_1", "local_claude_1"]
requires_ack: false
ack_for: []
supersedes: []
message_id: {path.as_posix()}
created_utc: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}
---

- To: user
- CC: claude_1, codex_1, local_claude_1
- Task: {TASK_ID}
- Requires acknowledgement: no

# OWNER MORNING SHEET — the night graded itself while everyone slept

Written by `night_runner` at {now.strftime('%H:%M:%SZ')} UTC, unattended, with
no human in the loop.  Nothing here is a ruling: KEEP/REVERT is yours.

## 1. What the title fight said (session 2: Door-1 challenger vs cure-C resident)

- Pairs (A - B), in order: {st['pairs']}
- Mean difference **{mean:+.3f}** over n={n} pairs.
- Pre-registered arithmetic: sigma_pair {SIGMA_PAIR}, SE {se_plan:.3f}, winner
  bar {bar} at n={n}, materiality floor {MATERIALITY_FLOOR}.
- Empirical pair spread this night (honesty clause): SD {sd:.3f}, SE {se_emp:.3f}.
- **Arithmetic outcome: {verdict}.**

In plain words: a positive number means the challenger (cure C with the
fictional-decay hunk deleted) scored higher than the resident it replaced.  The
bar is what a 95% interval demands before we are willing to call it real; the
floor is the size below which we agreed we would not care even if it were real.

## 2. The composed three-generation comparison (pre-registered {NIGHT1_DELTA:+.2f} + tonight)

- Night 1 (cure C vs the very-old resident): {NIGHT1_DELTA:+.2f}, n={NIGHT1_N},
  empirical pair SD {NIGHT1_PAIR_SD}.
- Night 2 (this night): {mean:+.3f}.
- **Composed distance {composed:+.3f}** from the very-old resident to tonight's
  challenger.
- Uncertainty, planning sigma: SE {se_comp_plan:.3f}. Uncertainty, empirical
  spreads: SE {se_comp_emp:.3f}.
- Named caveat, unchanged: composition chains ACROSS nights.  Pairing cancels
  only within-night drift and the ladder visibly moved between nights (Legend
  160 -> 176 seats).  The composed number is evidence, not gold.  The direct
  gold standard is Door-1 measured against the very-old resident in one block.

Your own framing, recorded: individually-immaterial steps may compose into a
significant cumulative gain, so the KEEP question weighs the composed distance,
not only the single step.

## 3. The nine named costs, which travel with any verdict

- P1/P2/P4, diagnosed 2-first/3-second order: {NAMED_COSTS_P124}
- P3 orchard divergence: {NAMED_COSTS_P3}

Exact keys: `codex_1/reviews/osc031-named-costs-package-review-2026-08-19.md`.

## 4. Which branch fired, and what has happened since

**Branch: {branch.upper()}.**

{next_note}

## 5. What is waiting for you

Nothing is merged, reverted or submitted beyond the chartered arm files.  The
next decision is yours at 09:00 MSK.
"""
    return path, body


def publish_morning_sheet(path: pathlib.Path, body: str, ledger: pathlib.Path) -> pathlib.Path | None:
    """Write the sheet and gate it on lint_outbox.py EXIT STATUS.

    A lint-rejected message must never be committed (transport rule), but a
    lint failure must never stop the night either.  So: on failure the sheet is
    moved OUT of the message namespace into the ledger's own directory, where
    its content survives and no invalid message is published.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    run(["git", "add", str(path)])
    lint = run([sys.executable, "scripts/lint_outbox.py", "--me",
                "local_claude_1", "--staged"], timeout=600)
    if lint.returncode == 0:
        return path
    run(["git", "reset", "-q", "HEAD", "--", str(path)])
    fallback = ledger.parent / ("REJECTED-" + path.name)
    fallback.write_text(body, encoding="utf-8")
    path.unlink(missing_ok=True)
    append(ledger,
           f"- morning sheet NOT published as a message: lint_outbox exit "
           f"{lint.returncode}; content preserved at `{fallback.as_posix()}`. "
           f"First error: {lint.stdout.strip().splitlines()[-1][:200] if lint.stdout.strip() else lint.stderr[:200]!r}\n")
    return fallback


def submit_next(state, state_path: pathlib.Path, ledger: pathlib.Path) -> dict:
    """Submit the arm for the next unread mark, fail-closed, and log it."""
    nxt = state["plan"][len(state["reads"])]
    arm = state["arms"][nxt["arm"]]
    try:
        payload = submit(arm)
    except Exception as exc:
        halt(state_path, ledger, state, str(exc))
    state["submissions"].append(
        {"at": utcnow().isoformat(timespec="seconds"),
         "id": payload["submission_id"], "arm": nxt["arm"]})
    state_path.write_text(json.dumps(state, indent=1))
    append(ledger, f"- {nxt['label']} swap {stamp()}: accepted, "
                   f"sha verified, submission "
                   f"{payload['submission_id']} (night_runner)\n")
    return nxt


def open_session3(mean: float):
    """Create session 3's fresh state and ledger (nothing submitted yet)."""
    new_state = session3_state()
    new_state_path = pathlib.Path(SESSION3_STATE)
    new_ledger = pathlib.Path(SESSION3_LEDGER)
    new_ledger.parent.mkdir(parents=True, exist_ok=True)
    new_ledger.write_text(session3_ledger_header(mean), encoding="utf-8")
    new_state_path.write_text(json.dumps(new_state, indent=1))
    return new_state, new_state_path, new_ledger


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--once", action="store_true",
                    help="one loop iteration then exit (testing)")
    ap.add_argument("--dry-run", action="store_true",
                    help="reads only; never submits, never pushes")
    args = ap.parse_args()
    state_path = pathlib.Path(args.state)
    ledger = pathlib.Path(args.ledger)
    state = json.loads(state_path.read_text())

    while True:
        if (REPO / "NIGHT-HALT").exists():
            halt(state_path, ledger, state, "halt file present")
        reads_done = len(state["reads"])
        if reads_done >= len(state["plan"]):
            break
        cur = state["plan"][reads_done]        # the arm currently on the ladder
        sub_at = dt.datetime.fromisoformat(state["submissions"][reads_done]["at"])
        elapsed_min = (utcnow() - sub_at).total_seconds() / 60
        if elapsed_min < MIN_WINDOW_MIN:
            if args.once:
                print(f"not due: {elapsed_min:.0f}m elapsed")
                return 0
            time.sleep(POLL_SECONDS)
            continue
        try:
            reading = read_arena()
        except Exception as exc:
            if elapsed_min > FORCE_READ_MIN + 60:
                halt(state_path, ledger, state, f"reads failing: {exc}")
            time.sleep(POLL_SECONDS)
            continue
        if reading["battles"] < MATURE_BATTLES and elapsed_min < FORCE_READ_MIN:
            if args.once:
                print(f"immature: {reading}")
                return 0
            time.sleep(POLL_SECONDS)
            continue
        if args.dry_run:
            print(f"DRY: would record {cur['label']} = {reading}")
            return 0
        # 1. record the read
        state["reads"].append({"label": cur["label"], **reading})
        row = (f"| {cur['label']} | {cur['arm']} | "
               f"{state['submissions'][reads_done]['at'][11:19]}Z | "
               f"{state['submissions'][reads_done]['id']} | "
               f"{reading['agent_id']} | {reading['read_at']} | "
               f"{reading['battles']} | {reading['score']} | "
               f"{reading['rank']}/{reading['total']} |\n")
        append(ledger, row)
        # 2. submit the next arm, unless the block is complete
        paths = [state_path, ledger]
        switch = None
        if len(state["reads"]) < len(state["plan"]):
            summary = "; next arm submitted"
            submit_next(state, state_path, ledger)
        else:
            # --- block complete: verdict first, exactly as before ----------
            append(ledger, verdict_block(state))
            stats = pair_stats(state)
            mean = stats["mean"]
            branch = post_b5_branch(mean, stats["n"])
            if branch == "extension":
                added = extend_plan(state)
                span = f"{added[0]['label']}..{added[-1]['label']}"
                append(ledger,
                       f"\n**EXTENSION FIRES** ({utcnow().isoformat(timespec='seconds')}) "
                       f"— mean {mean:+.3f} lies between the floor "
                       f"{MATERIALITY_FLOOR} and the bar {bar_for(stats['n'])}, so M-1's own "
                       f"rule appends pairs {span} (same arms, n={len(state['plan']) // 2} "
                       f"total, bar at n=10 = 0.930). Owner-approved night tree, "
                       f"branch 1.\n")
                nxt = submit_next(state, state_path, ledger)
                next_note = (
                    f"The score landed between the floor and the bar, so your own "
                    f"rule called for overtime and overtime started: pairs {span} "
                    f"were appended to the same plan with the same two arms, and "
                    f"`{nxt['label']}` was submitted at {stamp()}. At n="
                    f"{len(state['plan']) // 2} the winner bar drops to "
                    f"{bar_for(len(state['plan']) // 2)}. No new arm, no new "
                    f"file, nothing else changed.")
                summary = f"; BLOCK COMPLETE -> EXTENSION {span}"
            else:
                new_state, new_state_path, new_ledger = open_session3(mean)
                nxt = submit_next(new_state, new_state_path, new_ledger)
                append(ledger,
                       f"\n**SESSION 3 OPENED** ({utcnow().isoformat(timespec='seconds')}) "
                       f"— mean {mean:+.3f} is not between the floor and the bar, so "
                       f"the owner-approved night tree (branch 2) starts the direct "
                       f"comparison against the very-old resident "
                       f"`98628e98...` immediately. Fresh ledger "
                       f"`{new_ledger.as_posix()}`, fresh state "
                       f"`{new_state_path.as_posix()}`, arm A submitted at "
                       f"{stamp()}. This ledger is closed.\n")
                paths += [new_state_path, new_ledger]
                switch = (new_state, new_state_path, new_ledger)
                next_note = (
                    f"The score did not demand overtime, so the next measurement "
                    f"you asked for began at once: the Door-1 challenger measured "
                    f"DIRECTLY against the very-old resident `98628e98...` — the "
                    f"gold standard for the composed number in section 2. Fresh "
                    f"ledger `{new_ledger.as_posix()}`, arm A submitted at "
                    f"{stamp()}, standard 5-pair block, same pre-registered "
                    f"arithmetic. Progress so far: 1 of 10 marks submitted, "
                    f"0 read.")
                summary = "; BLOCK COMPLETE -> SESSION 3 (vs very-old resident)"
            # --- the morning sheet, in EITHER branch ----------------------
            try:
                sheet_path, sheet_body = morning_sheet(state, branch, next_note)
                published = publish_morning_sheet(sheet_path, sheet_body, ledger)
                if published is not None:
                    paths.append(published)
            except Exception as exc:      # a sheet must never cost the night
                append(ledger, f"- morning sheet FAILED to build: {exc}\n")
        state_path.write_text(json.dumps(state, indent=1))
        try:
            git_publish(paths, f"night_runner: {cur['label']} read "
                               f"{reading['score']}@{reading['rank']}{summary}")
        except Exception as exc:
            halt(state_path, ledger, state, f"publish failed: {exc}",
                 publish=False)
        if switch is not None:
            state, state_path, ledger = switch
        if args.once:
            return 0
    print("block complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
