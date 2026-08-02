# E7a half-size opening and scheduler attribution

- Task: `20260802-e7a-half-size-logical-simplification`
- UTC checkpoint: `2026-08-02T22:34:10Z`
- Evidence boundary: development attribution on the already-consumed seeds
  9,854,000--9,854,042 only
- Untouched qualification range: 9,854,043--9,854,127
- Arena action: none

## Result

The first focused-Yamo/exact-Moisan arm was 33,167 bytes and lost 27.4535 mean
paired margin. Two independent logical effects explain most of that residual loss:

| Arm | Bytes | Tasks | Mean delta | Bootstrap lower | Catastrophes | Negative mass |
|---|---:|---:|---:|---:|---:|---:|
| exact E7a baseline | 62,820 | 516 | 0 | -- | 19 | 4,138 |
| focused Yamo, exact Moisan | 33,167 | 516 | -27.4535 | -38.9961 | 31 | 8,259 |
| delete forced current-tree commitment | 32,819 | 516 | -20.6298 | -31.3605 | 33 | 7,514 |
| same deletion plus exact tuned opening | 36,059 | 516 | -9.8101 | -18.7132 | 25 | 5,961 |
| policy-free exact initial selection | 33,641 | 516 | -9.8101 | -18.7132 | 25 | 5,961 |
| size-qualified two-worker core plus bank wait | 31,401 | 516 | -6.9574 | -13.0213 | 22 | 5,012 |

Deleting the simplified scheduler's unconditional 10,000-point preference for
chopping the tree under the worker both removes 348 bytes and recovers 6.8236 mean
margin. Restoring the exact opening objective, full 27-profile search, and turn-35
strongest-affordable fallback recovers a further 10.8198 mean margin, but costs 3,240
bytes relative to that arm. The exact-opening arm is still 4,649 bytes above the
31,410-byte ceiling and fails the frozen value gates, so it cannot qualify.

Specializing the exact initial decision into one method removes the general policy and
deadline state while reproducing the exact-opening panel result. Specializing movement for
the always-empty priority sets, removing unreachable N-worker and trait scaffolding, and
deleting unused protocol computation reaches the size ceiling. A 23-byte `WAIT` offer in
bank candidate sets then makes single-door two-carrier selection total and improves the
full-panel mean by 3.4554. The resulting 31,401-byte source is 50.014% smaller than the
62,820-byte baseline, but it remains a development rejection: the value gates, catastrophe
count (19 -> 22), negative mass (4,138 -> 5,012), and period-2 liveness evidence do not pass.

## Rejected small hypotheses

The following 96-task probes used seeds 9,854,000--9,854,007 and were stopped before
the full panel:

| Change | Bytes | Mean delta | Observation |
|---|---:|---:|---|
| bank partial wood only when full/adjacent/late | 33,372 | -22.7188 | no improvement over the matching -22.6875 slice |
| expand the approximate chooser to all 27 profiles | 33,245 | -31.4583 | profile breadth without the exact objective is harmful |
| replace the general movement router with the two-worker guard | 32,826 | -32.1146 | period-2 cases fall from 39 to 1, but value collapses |
| fixed movement-2/carry-2/chop-2 second worker | 30,287 | -37.2500 | size passes, adaptive opening value does not |
| exact score-aware endgame threshold | 32,948 | -22.8750 | worse than the no-forced-chop arm |

The movement probe is especially diagnostic: liveness can be repaired mechanically, but
the tested guard changes routes too aggressively. It should not be combined with the
opening result.

## Consequence

The next successor should start from the 31,401-byte bank-wait arm, which already retains
exact Moisan economics and exact initial tuned-opening decisions. The opening attribution
shows that three decisions matter separately:

1. exact resource collection ETA for plum, lemon, and optional iron;
2. the tuned preferred-carry selection against the baseline ETA allowance;
3. strongest-affordable fallback at turn 35.

The initial objective is now preserved; the turn-35 strongest-affordable fallback had no
effect on the 96-task probe. Remaining work is value and liveness recovery within the
nine-byte headroom, so additional behavior requires an offsetting named deletion. No
untouched map may be opened until a distinct source passes the frozen consumed-development
gates and is locked.

## Reproducibility

- development builder SHA-256:
  `46063226b6966703515fa6d29ed5ade76adfec740b92c2af4f7eea1335d7e733`
- no-forced-current-chop source SHA-256:
  `782d7c865fe8ffc24b3dad6924677ee15c7435f0c87886059a8b39a7ced390fc`
- exact-opening source SHA-256:
  `e2b391f886d741b1991c127a92888f1778aa8dd94bd551c4989b8efaf09b171b`
- policy-free exact-initial source SHA-256:
  `c17cb1f396ff2a9260aab3470e7f9da176007a49798d957f69822cf3608c1ca1`
- size-qualified bank-wait source SHA-256:
  `923395d8101aa2925e3ba4c237f0e0c80250afd289ca06629d16563acd67082d`

Both retained sources pass strict optimized standalone compilation. Their panel JSON and
TSV records contain the complete paired task results and latency footer.
