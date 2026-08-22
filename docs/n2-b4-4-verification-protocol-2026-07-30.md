# N2 — B4.4 verification sweep protocol

- Owner: `local_codex_1`
- Reviewer: `chatgpt_1`
- Frozen UTC: 2026-07-30T19:08:47Z
- Base commit: `3aa8ed4c9fe85099ce4895db018893316c488ee8`
- Scope: read-only reconstruction and claim audit; no experiment or Arena action

## 1. Decision

B4.4 has already received material corrections. Recompute every remaining numerical or
causal-looking B4.4 statement from an explicitly identified source cut, distinguish pooled
from per-agent evidence, and assign each claim exactly one verdict:

- `VERIFIED`: the stated claim follows under its stated unit/denominator and remains
  materially stable on the current sensitivity cut;
- `CORRECTED`: evidence exists, but the published wording, denominator, scope, or
  interpretation must change;
- `RETIRED_UNIDENTIFIABLE`: the original source/output cannot be reconstructed adequately
  or the available observables cannot identify the claim.

The task is complete only when every registered claim has a verdict. No result authorizes a
policy change, simulation, submission, TestSession, or Arena action.

## 2. Frozen source identity

The original B4.4 JSON report was written to an ephemeral `/tmp/claude-1001/...` path and
was not committed. The repository does preserve these exact anchors:

- original analyzer `cgauto/peer_cohort_analysis.py`, identical at commit `46d36098` and
  current base, SHA-256
  `7934dd427259e9f6b12cd85ff744de6c7dc2deee7fd38efa558d4d677dd193cc`;
- commit-`46d36098` `data/processed/stats.json`, SHA-256
  `6998bf009de26f12e86a4b87923fa490f209102590a80f40b74f545e7a9211d0`,
  recording 8,131 parsed games, zero failures, and 471 unique agents;
- historical leaderboard
  `/home/tarstars/prj/troll_farm/data/raw/snapshots/20260728T110709Z-d61p-wide/leaderboard.json`,
  SHA-256
  `5299a96991129fb118cf8a9fd0a491f9e1de8d70f1fb49caa75f2dbb6850e7e2`.

The primary reconstruction is the first exactly 8,131 newline-delimited records of
`/home/tarstars/prj/troll_farm/data/processed/games.jsonl`, game IDs
891153730–896636314 inclusive, prefix SHA-256
`c93a273cbeabc7f142432461a6e084a9bb1d5d9c6ac59c6d445f14538e47bde1`.
It is classified `RECONSTRUCTED`, never called the immutable original corpus. It upgrades
to `RECONSTRUCTED_MATCH` only if the analyzer reproduces all published structural anchors:
25 non-resident cohort agents, 12 strong, 13 peer/weak, 2,787 tracked occurrences including
the resident, resident mean roster 2.000, rank spans 7–38 and 46–104, and 100% required
raw/trajectory decode coverage. Failure of any anchor makes claims depending on the
unavailable original cut `RETIRED_UNIDENTIFIABLE`; it must not be papered over with the
current corpus.

The preregistered current-data sensitivity uses all 9,082 records of the same observed
file, game IDs 891153730–897326497, SHA-256
`12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`,
and leaderboard
`/home/tarstars/prj/troll_farm/data/raw/snapshots/20260730T021701Z-d61p-wide/leaderboard.json`,
SHA-256
`7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815`.

For each selected game, raw replay and trajectory inputs are read only from the exact
physical project roots:

- `/home/tarstars/prj/troll_farm/data/raw/games/<gameId>.json`;
- `/home/tarstars/prj/troll_farm/data/processed/trajectories/<gameId>.jsonl`.

The analyzer must write a sorted manifest containing each consumed path, byte count, and
SHA-256. Missing inputs are evidence, not permission to collect or regenerate data. Nothing
under the physical input root may be written.

## 3. Fixed cohort and units

Reproduce the original cohort rule without modification: Legend division, at least ten
corpus occurrences, non-resident mean final roster within ±0.2 of the resident mean;
`STRONG` ranks above the resident and `PEER_WEAK` ranks at or below it.

Report all of these units separately:

1. game occurrence;
2. successful action opportunity/event;
3. generated crop;
4. agent (unweighted across agents);
5. pooled group occurrence/event.

A median first-event turn excludes games with no such event and therefore must always be
paired with `n_reached`, total `n`, and coverage. A pooled statement cannot support an
“every agent” claim. Final-inventory wood share is not a direct measure of planting
purpose.

## 4. Registered claims

| id | B4.4 claim to adjudicate | Required audit |
|---|---|---|
| C1 | 25-agent cohort, 12/13 split, ranks and 2,787 occurrences with 100% decode | exact anchor reproduction and source manifest |
| C2 | resident first successful plant 191.5 versus 21–29 for all 25 peers | conditional group medians, coverage, and every-agent medians/ranges; current sensitivity |
| C3 | resident reap 0.93%, strong 15.3%, peer/weak 17.2%, and the gap applies to every other two-worker agent | reproduce the exact generation denominator; report pooled and every-agent results separately |
| C4 | strong score 215.6 versus resident 185.7, with +15% wood/+30% fruit, and resident most wood-concentrated | group and per-agent final-inventory composition; explicitly incorporate the already-published H3 quartet correction |
| C5 | the timing difference proves absence/presence of a sustained plant-then-reap loop and motivates one middle-ground planting mechanism | classify self-planted crop outcomes where observable; separate early planting (≤50), middle (51–250), and late (>250); distinguish orchard establishment from endgame fruit-to-wood conversion |
| C6 | the live planner contains tested factory machinery defaulting off behind a one-shot selector consistent with the observed delay | byte-identified, read-only code grounding; distinguish current code fact from historical behavior and from causal attribution |
| C7 | trajectory, scale-survival, suppression, and ranked-mechanism statements in the B4.4 entry | reconcile against later H3/H5/B4.6 results; corrected or superseded claims may not remain silently citable |

The owner clarification is binding: early planting around turns 21–29 can establish a
self-reproducing orchard, while planting after turn 250 can convert accumulated fruit into
wood. These are different purposes, not a contradiction. N2 must not infer purpose from
turn alone; it may report a purpose only from the planted crop's observed subsequent
harvest/chop lineage or an independently grounded code rule.

## 5. Gates and sensitivity

- Source hashes, record counts, game-ID boundaries, and input manifests are checked before
  substantive calculation.
- Any missing or failed replay/trajectory decode is reported by game and claim impact.
- C2–C5 require historical reconstruction and current sensitivity side by side.
- “Every” requires all 25 per-agent rows to satisfy the precise predicate with nonzero
  denominator; pooled agreement is insufficient.
- Numerical reproduction tolerance is ±0.05 percentage point or ±0.05 score/turn for
  unrounded source values. A published range is checked against its implied per-agent
  statistic, not a pooled substitute.
- A claim that materially changes under the current sensitivity cut is `CORRECTED` even if
  the historical reconstruction matches.
- Existing H3 corrections are evidence to incorporate, not hypotheses to reverse by
  redefining denominators.
- No missing historical output may be recreated from sealed data, network access, or a new
  Arena collection.

## 6. Outputs and acceptance

Compact outputs:

- deterministic analyzer `cgauto/verify_b4_4_claims.py`;
- focused tests `tests/test_verify_b4_4_claims.py`;
- machine result, input manifest, transition/agent tables, and report under
  `local_codex_1/n2-b4-4-verification/`;
- canonical result under
  `data/analysis/live-agent-6553250/n2-b4-4-verification-result-2026-07-30.md`.

Acceptance commands:

```text
python3 -m py_compile cgauto/verify_b4_4_claims.py
python3 cgauto/verify_b4_4_claims.py --self-test
python3 -m pytest -q tests/test_verify_b4_4_claims.py
python3 cgauto/verify_b4_4_claims.py <recorded exact arguments>
```

The final report records commands, durations, source and output hashes, all C1–C7 verdicts,
and a citation-safe replacement for the B4.4 backlog/constraint text. The reviewer checks
source identity, denominator discipline, the early-orchard/late-conversion distinction,
and every claim verdict before closeout.
