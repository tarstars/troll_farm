# Arena opponent-opening calibration — known 60, 2026-07-18

## Verdict

**Do not calibrate rollout weights from the current continuation zoo.  Retire turn-one Monte
Carlo with this option/model library.**

The eight local models do not span the arena field's turn-one training behavior, and their
coarse action agreement cannot identify a trustworthy terminal-value mixture.  The known 60
arena replays remain diagnosis data.  No map holdout, live source, submit default, or arena state
was touched.

## Protocol

For each preserved game, the actual arena opponent's first command was extracted from the
immutable replay.  Every local continuation received the identical candidate-relative initial
state as seat 1 and produced a first command in three fresh processes.  Messages, trailing empty
commands, eager later output lines, and duplicate per-unit commands after the referee-effective
first command were normalized away.

Agreement was measured at four levels:

1. whether TRAIN is present and its four-stat spec;
2. starter action verb;
3. complete starter command including target;
4. complete effective opening command set.

This is behavioral support analysis, not a terminal outcome estimate.

## Field coverage

Arena opponents trained immediately in **22/60 games**.  They used 11 distinct specs:

| Spec | Games |
|---|---:|
| `2/2/0/2` | 6 |
| `2/2/1/1` | 5 |
| `2/2/1/2` | 2 |
| `2/2/2/0` | 2 |
| seven other specs | 1 each |

The starter moved in 49 games and picked a seed in 11.

Seven models—GoldElite, adaptive Gold, SchedBot, MyBot, SilverBoss, ScriptBoss, and PrinterBot—
never trained on turn one in these states.  Their apparent 63.3% exact TRAIN rate is entirely the
38 games where both arena opponent and model did not train.  They match none of the 22 actual
immediate trains.

BossReal always trained when the arena opponent did, but matched **0/22 specs**; mean talent L1
distance was 4.27.  Thus the zoo has a binary always-train scenario and seven no-train scenarios,
not coverage of the field's conditional worker-rich openings.

## Action agreement

All model openings were stable in 60/60 games across all three processes.  The terminal
instability found in Phase 7 begins later and does not affect this result.

| Model | Opening signature | Exact starter command | Exact full opening |
|---|---:|---:|---:|
| adaptive Gold | 28/60 | 10/60 | 8/60 |
| GoldElite | 28/60 | 8/60 | 6/60 |
| PrinterBot | 28/60 | 6/60 | 4/60 |
| ScriptBoss | 28/60 | 4/60 | 4/60 |
| SilverBoss | 28/60 | 2/60 | 2/60 |
| MyBot | 28/60 | 0/60 | 0/60 |
| SchedBot | 28/60 | 0/60 | 0/60 |
| BossReal | 0/60 | 1/60 | 0/60 |

For the seven no-train models, the identical 28/60 signature score is simply the arena subset
with no TRAIN and starter MOVE.  It does not distinguish their continuation quality.  Exact
targets are sparse, and the best coarse match is the same Gold family whose terminal rollouts
overconfidently selected the rejected arena candidate.

## The three failed rollout activations

FreZzz, daaskare, and a76a44 all chose **no turn-one TRAIN**, so the missing immediate-train branch
does not alone explain those losses.  However:

- no local model reproduced FreZzz's or daaskare's first MOVE target;
- a76a44 issued `PICK`, while all eight models issued `MOVE`;
- GoldElite got only the coarse no-TRAIN/MOVE signature on the first two and missed the third
  action family entirely.

The arena failure therefore reflects target-policy and later-continuation mismatch even inside
the nominally covered no-train branch.

## Why weights are not defensible

A global similarity weight would favor adaptive Gold/GoldElite, reproducing the already-rejected
single-family bias.  It would also assign zero structural support to 22/60 worker-rich openings.
Per-game calibration is unavailable to a turn-one controller because both players choose their
first command simultaneously; the opponent's command is visible only afterward.  Later-turn
agreement could support a later checkpoint controller, but cannot validate the tested turn-one
worker decision.

Consequently no ambiguity set or weighted option-grid rerun is warranted.  More arithmetic on
these models would create precision without coverage.

## Decision

1. Close Phase 8 calibration-as-weighting after its first discriminator.
2. Retire turn-one Monte Carlo for the isolated first-worker library.
3. Preserve the untouched map holdout and exact resident agent `6559583`.
4. Do not add forced TRAIN wrappers and call them calibrated opponents; training spec without the
   accompanying supply, targeting, and later role policy is the transplant already disproved.
5. Move the research unit to complete-policy continuation learning: replay-derived high-level
   objectives and role transitions, validated by held game and held agent before local league
   evaluation.

Machine-readable evidence:
`arena-opponent-opening-calibration-known60-2026-07-18.json`.

Implementation:

- `cgauto/arena_opponent_opening_calibration.py`;
- `yamo_option_rollout_time opening-command-grid`;
- three focused Python tests and the existing Rust option-grid tests.

Final repository validation passes: 318 Python tests and the full release Rust suite; formatting
and `git diff --check` are clean.  Only pre-existing warnings and ignored tests remain.
