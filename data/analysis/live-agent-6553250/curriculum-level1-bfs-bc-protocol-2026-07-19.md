# Curriculum Level 1 BFS + behavior-cloning protocol — frozen 2026-07-19

## Motivation

PPO-from-scratch preflight is closed before prospective data.  Its faithful 250k debug run learns
HARVEST and DROP locally but solves only 3/876 nonzero-deficit maps, waits on the current cell
106,558 times, and reaches 12.7% overall versus 10.9% random.  The deterministic teacher solves
99.8% on the frozen prospective control.  The next experiment attacks the measured destination
selection failure, not the PPO coefficients.

The exact resident source, checksum, Arena agent, and submission remain unchanged.  This protocol
does not authorize a submission.

## Frozen changes

The observation and network dimensions remain 104x11x22 and 34,926 parameters.  Two redundant
channels change semantics:

- channel 2 is selected-troll-to-cell BFS proximity; and
- channel 103 is cell-to-own-home BFS proximity.

Both are normalized unsigned-byte maps, high when near.  This makes the teacher's all-pairs
distance rule representable by the shallow spatial head without increasing runtime, source-weight
count, or the 100,000-character deployment burden.

Before PPO, the actor imitates the deterministic teacher on 100,000 training-only state/action
pairs.  Data are generated online under the teacher policy, in chunks of 1,000, and are never
written as a multi-gigabyte observation corpus.  The optimizer is Adam at `1e-3` with cosine decay
to `1e-4`, two shuffled cross-entropy epochs per chunk, minibatches of 1,000, and 14 Torch threads.
The critic receives no supervised target and is reinitialized only by the model seed; later PPO
owns value learning.

## Part D — debug functional gate

- teacher-label stream: generated from seeds beginning at 0;
- functional evaluation: seeds 5,000--5,999, 1,000 episodes;
- teacher control on that bank is frozen before learned evaluation;
- model seed: 41;
- exactly 100,000 teacher labels; no budget extension.

The bootstrap passes only if deterministic functional play achieves all of:

- at least 80% overall success;
- at least 75% success among initial LEMON deficit 1--8;
- no map-height bucket below 65%;
- paired median completion no more than 15 turns slower than the teacher; and
- at least 80% selection on legal HARVEST and DROP opportunities in a deterministic action audit.

Failure closes this BFS/BC instance.  Do not open the official training or evaluation streams.

## Part P — prospective PPO gate, conditional on Part D

If Part D passes, train a fresh model seed 43 on 100,000 teacher labels from the official training
stream beginning at 1,000,000.  Continue from that checkpoint with the already frozen PPO reward,
network, and optimizer settings.  The first learned evaluation of seeds 2,000,000--2,000,999 occurs
at 250,000 PPO transitions.

The prospective Stage A gate is strengthened for a teacher-initialized model:

- at least 70% overall success;
- at least 65% nonzero-deficit success;
- no height bucket below 55%; and
- paired median completion no more than 25 turns slower than the teacher.

If Stage A passes, continue to one million PPO transitions.  Final run-one thresholds are 85%
overall, 80% nonzero-deficit, 75% height floor, and teacher median +15 turns.  Only then open the
replicate training stream at 3,000,000 and evaluation bank at 2,001,000.  A Level 1 success still
authorizes only randomized-worker Level 2, not a live candidate.

## Stop and interpretation rules

- High imitation accuracy but low functional success means observation/receptive-field aliasing;
  next test is factorized verb/destination heads, not more labels.
- Low direct-verb accuracy means class/phase imbalance; one online teacher auxiliary-loss test is
  allowed.
- High debug success followed by PPO regression authorizes that auxiliary-loss test; it does not
  authorize selecting the behavior-cloned checkpoint as a game agent.
- No local result overrides the known 91% position drift or the layered field-transfer gate.

