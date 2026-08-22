# M3 — resident seat-asymmetry audit protocol

- Owner: `local_codex_1`
- Reviewer: `chatgpt_1`
- Frozen UTC: 2026-07-30T19:48:51Z
- Base commit: `b9aec2b00ac8ba1a12bac390bf3292e491c151c5`
- Scope: current-corpus read-only seat audit; no replay mechanism work or Arena action

## 1. Decision

Determine whether the exact resident systematically underperforms in player seat 0 or
seat 1 after comparing its games against the same exact opponent identity at comparable
pre-game strength and map conditions. Return exactly one verdict:

- `ACTIONABLE_SEAT_ASYMMETRY`: one seat is materially worse and every frozen support,
  uncertainty, outcome, and stability gate below passes;
- `NO_ACTIONABLE_SEAT_ASYMMETRY`: the matched exact-identity panel clears support but the
  full actionability gate does not;
- `UNIDENTIFIABLE`: source integrity or primary overlap is inadequate.

An actionable result authorizes only a new read-only replay/mechanism task. It does not
authorize a seat branch, policy change, simulation, submission, TestSession, or Arena
action.

## 2. Frozen sources and identity

Primary corpus:
`/home/tarstars/prj/troll_farm/data/processed/games.jsonl`, exactly 9,082
newline-delimited records, game IDs 891153730–897326497, SHA-256
`12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`.

The exact resident is `agentId=6561795`. The source preflight must reproduce 9,018 clean
games, 241 clean resident occurrences, 72 exact resident opponents, 126 resident-seat-0
games, and 115 resident-seat-1 games. Any mismatch stops the audit.

Use each processed game's contemporaneous `players[].arenaScore`; no later leaderboard
score or recovered rating formula is used. `agentId` is the primary opponent key.
`pseudo` is a lineage sensitivity only.

## 3. Outcomes and matching

Include every clean exact-resident occurrence; no outcome, duration, roster, opponent, or
map filter is allowed before matching.

Primary estimand is **seat-1 minus seat-0 resident terminal margin**. Secondary estimand
is the corresponding win-indicator difference (1 win, 0.5 tie, 0 loss).

For each resident seat-1 target game, eligible seat-0 controls satisfy all:

- the same exact opponent `agentId`;
- exact same map width and height;
- absolute opponent contemporaneous `arenaScore` difference ≤1.0;
- absolute resident contemporaneous `arenaScore` difference ≤0.25;
- absolute initial-tree-count difference ≤4.

The target residual is its outcome minus the unweighted mean of eligible controls. The
primary estimate is the unweighted mean across supported seat-1 target games. A target
with no control is excluded from the matched estimand but reported. No terminal or
trajectory field other than the outcome may enter matching.

Primary support requires at least 30 supported seat-1 target games from at least 15 exact
opponent identities, at least 15 supported targets in each chronological half, and at
least 100 total resident games in each raw seat. Preflight before outcome inspection found
37 supported seat-1 targets from 23 identities and 126/115 total raw seat counts.

## 4. Uncertainty and null

Use deterministic seed `20260730`.

- Percentile 95% confidence interval: 20,000 cluster bootstraps resampling exact opponent
  identities, retaining all supported target residuals in each sampled cluster.
- Two-sided matched randomization p-value: 50,000 replicates. Within every exact-opponent
  cluster independently sign-flip its mean target residual, then compare the absolute
  cluster-size-weighted mean with the observed absolute estimate. Use the finite-sample
  `(1 + exceedances)/(B + 1)` correction.
- Report leave-one-exact-opponent-out estimates and the opponent-cluster influence table.

This is an observational matched association. Random seat assignment is not assumed or
claimed; an actionable association still requires a replay audit before mechanism work.

## 5. Frozen sensitivities

All sensitivities report seat-1 minus seat-0 orientation:

1. reverse orientation: seat-0 targets matched to seat-1 controls, then sign-reverse;
2. same-`pseudo` lineage instead of exact `agentId`;
3. opponent-score bands ±0.5 and ±1.5;
4. early and late chronological halves of supported primary targets;
5. raw unadjusted seat difference;
6. exact-identity fixed-effect contrast: for every opponent with both seats, compute
   seat-1 mean minus seat-0 mean, then report game-weighted and identity-equal means.

Final score components and game duration may be reported descriptively for mechanism
triage but are forbidden as controls or actionability substitutes.

## 6. Actionability gates

A seat direction is actionable only if all are true:

1. primary support passes;
2. absolute primary margin difference is at least **20 points**;
3. the bootstrap 95% confidence interval excludes zero;
4. the two-sided matched randomization p-value is at most **0.05**;
5. the win-indicator difference has the same sign and absolute magnitude at least
   **0.10**;
6. reverse-oriented matching has the same sign;
7. same-pseudo matching has the same sign;
8. both identified ±0.5 and ±1.5 score-band sensitivities have the same sign;
9. early and late halves have the same sign;
10. every leave-one-exact-opponent-out estimate has the same sign.

Name every failed gate. There is no relaxed post-hoc threshold. If a gate fails, the
verdict is `NO_ACTIONABLE_SEAT_ASYMMETRY`, not a weaker policy recommendation.

## 7. Outputs and acceptance

Exclusive compact outputs:

- `cgauto/seat_asymmetry.py`;
- `tests/test_seat_asymmetry.py`;
- machine result, cluster table, and report under
  `local_codex_1/m3-seat-asymmetry/`;
- canonical result under
  `data/analysis/live-agent-6553250/m3-seat-asymmetry-result-2026-07-30.md`.

Acceptance commands:

```text
python3 -m py_compile cgauto/seat_asymmetry.py
python3 cgauto/seat_asymmetry.py --self-test
python3 -m pytest -q tests/test_seat_asymmetry.py
python3 cgauto/seat_asymmetry.py <recorded exact arguments>
```

The analyzer must verify the source hash and counts, sort outputs deterministically,
record every support/actionability gate, and reproduce output hashes on a second full
run. The reviewer checks seat orientation, outcome-free matching, cluster dependence,
sensitivities, and the follow-up boundary.
