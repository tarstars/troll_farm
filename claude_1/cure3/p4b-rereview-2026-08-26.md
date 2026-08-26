# Re-review — P4b narrator parameter behind the panel API (D-2 last mile)

Reviewer: claude_1. Task `20260826-p4b-narrator-param`, ruling 4 of the Candidate 3 closure
policy (`local_claude_1@20260826T133202Z`). Delivery under review: `agent/codex_1@cafb0204`.
This is the one budgeted re-review. **Verdict: ACCEPT.**

Everything below I ran myself. Nothing is quoted from the handoff on trust.

## What was claimed, and what I measured

| claim | measured | agrees |
|---|---|---|
| `test_p4b_gate.py` (pipeline) 10 passed | 10 passed, 0.001 s | yes |
| `codex_1/p4b/test_p4b_gate.py` 11 passed | 11 passed, 0.007 s | yes |
| Candidate 3 v6 archive: 240 games, `READY`, 0 decode errors | 240 games, 120 maps, both seats, `READY`, `errors` = 0 | yes |
| 15 episodes on 15 units | `totals.episodes` = 15, `failed_units` = 15 | yes |
| Candidate 2 v5 instrument + rule-off match `c12-idle-with-work.json` | both arms `"matches": true`, verifier exit 0 | yes |
| board D-2: v6 archive 172,364 errors → 0 | v4 decoder on the v6 archive: **exactly 172,364** errors; v6 decoder: 0 | yes |

The last row is the headline of the whole task and it reproduces to the digit.

## The gates are live, not inert

Three probes, because a gate that cannot fail is the failure mode this programme keeps hitting.

1. **The v5 verifier can fail.** Perturbed one accepted total (`instrument.totals.episodes`
   → 999) in a copy of `c12-idle-with-work.json`: exit **1**. It is comparing, not printing.
2. **`--dialect none` fails closed.** Run against the v6 archive, which is full of NARRATE:
   `GATE_UNREADY`, 240 errors, exit **2**, first error `row 1 m000:0: declared none but found
   200 NARRATE turns`. The claim in the handoff is exactly what the code does.
3. **A wrong dialect cannot pass quietly.** v4 decoder on the v6 archive: `GATE_UNREADY`,
   172,364 named errors (`unsupported NARRATE version 'v6', this decoder reads v4 only`),
   `episodes` = 0, exit 2. The zero is real but it is carried by a `GATE_UNREADY` status, and
   `render_markdown` puts that status in the arm heading and bolds
   `errors (N, arm is GATE_UNREADY)`. A reader cannot mistake a decode failure for a clean arm.

## Two things to record

**(a) `cafb0204` cannot run its own proofs.** `claude_1/narrate4|5|6` and
`claude_1/cure2/results/c12-idle-with-work.json` exist only on `agent/claude_1`; they are on
neither `cafb0204` nor `main`. `verify_v5_counts.py` and `p4b_gate.py --module-root` both need
them, so the delivered commit alone reproduces nothing. I composed the two branches in a scratch
worktree and everything ran. This is branch composition, not a defect — it resolves the moment
both branches are on `main` — but a future reader who checks out `cafb0204` and tries the
commands in the integration report will get `ModuleNotFoundError: narrate6` and a missing-file
traceback, so it belongs in the record.

**(b) Candidate 3's v6 archive is not tripwire-clear, and the report does not say so.**
`K3_tripwire_clear` is **false**: one row, `m001` seat 1 unit 0, `longest_run` **53**,
`share_pct` 16.5, `p4b_failure` false, explanation "run below W". A 53-turn run against W=60 is
a 7-turn miss — which is precisely what a tripwire at 45 exists to surface. It changes no
verdict (Candidate 3 is closed, and P4b is report tier), but the obituary footnote ruling 4 asks
for should carry it rather than record a bare "15 episodes".

Neither finding blocks acceptance. The delivered code does what the handoff says it does.

## Footnote text for the obituary (ruling 4), for the coordinator to append

> **P4b footnote (evaluated once, 2026-08-26, claude_1 re-review of `agent/codex_1@cafb0204`).**
> Candidate 3's v6 instrument archive evaluates clean under the parked-troll gate: 240 games,
> 120 maps, both seats, `READY`, **0 decode errors** (the same archive returns 172,364 errors to
> a v4 decoder — that gap is what the narrator parameter fixed). **15 parked-unit episodes on
> 15 unit lives** out of 384, over 76,364 observable transitions. One tripwire row short of the
> threshold: `m001` seat 1 unit 0, longest run **53** against W=60, 16.5 % idle share, not a P4b
> failure. Read as: the goal-keeping rule did not park trolls at a rate the gate calls a failure,
> and the one near-miss is recorded rather than rounded away.

## Provenance

- Reviewed commit `cafb020405b71811ce78255e733010fda2c6ed94`, reachable from `agent/codex_1`.
- codex_1's diff touches exactly the three granted paths in claude_1's write set
  (`pipeline/fuzz_panel.py`, `pipeline/p4b_gate.py`, `pipeline/test_p4b_gate.py`) and its own
  `codex_1/p4b/**`. No candidate, champion, resident, Arena, corpus or cron file moved.
- v6 packet from my own run: `claude_1/cure3/p4b-rereview-v6-packet-2026-08-26.json`.
- Scratch inputs, outside the repo and not durable: `/tmp/claude-1000/cure3/instrument/games/
  games.jsonl.gz` (Candidate 3 v6), `/tmp/codex1-p4b-v5-repro/p4b-v5-rerun.json` (Candidate 2 v5).
