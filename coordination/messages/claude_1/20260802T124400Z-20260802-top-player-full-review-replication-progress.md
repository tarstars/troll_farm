# progress: 20260802-top-player-full-review-replication

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T12:44:00Z
- Task: 20260802-top-player-full-review-replication
- Branch: agent/claude_1
- Requires acknowledgement: no
- Platform mutation performed: no

## Step 1 — cohort verified independently

153 current-new games, both sides present in all 153, our agent `6589709` in every row.
Rank bands **1 / 73 / 52 / 27** exactly as frozen. Durations 96 full-300 / 57 short.
95W/2T/56L, seats 68/85.

| opponent band | n | W-T-L | mean margin | win rate |
|---|---:|---|---:|---:|
| 1–20 | 1 | 0-0-1 | −70.00 | 0.0% |
| 21–50 | 73 | 42-1-30 | +13.55 | 57.5% |
| 51–100 | 52 | 33-1-18 | +34.21 | 63.5% |
| 101+ | 27 | 20-0-7 | +34.74 | 74.1% |

## Step 4 — the loss mechanism, decomposed by phase

This is my main independent result and it is not in the local report in this form. Over the
96 full games I decomposed **points scored per 50-turn window** for both sides, then split by
the opponent's final roster.

**Against ≤2-worker opponents (n=60): they never accelerate.**

| window | ours | theirs | net |
|---|---:|---:|---:|
| t50→t100 | 33.30 | 21.47 | +11.83 |
| t100→t150 | 30.82 | 24.77 | +6.05 |
| t150→t200 | 29.37 | 22.82 | +6.55 |
| t200→t250 | 30.87 | 21.17 | +9.70 |
| t250→t300 | 36.02 | 25.60 | +10.42 |

Terminal +59.07, 41/60 wins. We are net positive in **every** window.

**Against ≥3-worker opponents (n=36): they multiply by 12×.**

| window | ours | theirs | net |
|---|---:|---:|---:|
| t50→t100 | 36.92 | 8.64 | +28.28 |
| t100→t150 | 37.64 | 16.47 | +21.17 |
| t150→t200 | 39.75 | 46.06 | **−6.31** |
| t200→t250 | 40.83 | 79.81 | −38.97 |
| t250→t300 | 42.56 | 102.19 | −59.64 |

Terminal −38.19, 11/36 wins.

## What this rules out, which matters more than what it suggests

**Our own production never declines — it is higher in the games we lose.** Our per-window
scoring is 36.92 → 42.56 against scaling opponents versus 33.30 → 36.02 against
non-scaling ones, and our mean final score is **234.28** in the games we lose to scaled
opponents against **198.58** in the games we win. We are not playing worse when we lose. We
are playing better and losing anyway.

Therefore **any candidate that improves our own economy, harvest, banking or conversion is
attacking the wrong variable.** It cannot close a gap that opens entirely on the other side
of the board. That is a whole-corpus statement over 96 games, not an inference from the one
direct game, and it disposes of more candidate families than any single positive finding I
have.

The crossover is sharp and locatable: the net flips negative in **t150→t200**, one window
after the cohort's worker-three appearances. There is a real activation window before the
damage compounds.

## Step 2 — action profile versus the top-20 benchmark, per 100 turns

| action | ours | top20 | our opponents |
|---|---:|---:|---:|
| chop | **65.28** | 50.85 | 34.17 |
| harvest | **3.18** | 19.55 | 14.48 |
| plant | 4.74 | 10.19 | 9.10 |
| mine | 0.25 | 2.10 | 1.19 |
| wait | 8.42 | 2.31 | 11.45 |
| move | 94.54 | 126.08 | 117.00 |

We are a wood/denial bot in a field of fruit-economy bots. Two of these gaps are **already
closed and must not be reopened**: mining at workforce ≥2 is closed as harmful
(`docs/CONSTRAINTS.md:344`, D174a −10.76) and the resident deliberately stops mining at
worker two (`:348`). Our roster is **exactly 2.00 in all 153 games** — we train once, always
— against top-20's 2.83 and our opponents' 2.33; worker-three scaling is closed by A2-1's
K1 failure (`:133`) and by "opportunistic, never a dedicated funding detour" (`:355`).

So the single largest structural gap in the package sits on closed ground. I will report it
as measurement-only with its citations rather than dress it up as a candidate.

## Package caveat worth flagging now

`planted_ok_*` is **not** a subset of `plant_cmd_*`: aggregated over top-20 sides it exceeds
commands issued (86,023 vs 81,280, 105.8%), and over our opponents 107.1%. Any "plant success
rate" computed from these two columns is therefore unsound, including for us. I will not
publish one, and I would not accept one in cross-review without a stated definition.

## Next

Step 3, the exact `897780884` postmortem from the committed replay/trajectory, then closure
checks and the ranked list. Handoff or further progress inside the lease.
