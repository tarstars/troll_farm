# Replay-conditioned continuation retrieval — result, 2026-07-19

## Verdict

**Reject cross-agent trajectory retrieval.**  Recent action history does not predict the next
50-turn rich-opponent production vector better than the current aggregate state on held-out named
opponents.  The experiment passes only integrity; all five material gates fail.

This is a representation result on 21 consumed games.  It creates no candidate and does not
support replaying recorded commands under a changed resident policy.

## Frozen selection and confirmation

Discovery leave-one-opponent-out selected `k=3` for map, state, and history retrieval.  The exact
dataset contains 21 games and 42 cutoff examples: 24 discovery and 18 confirmation.

| Confirmation comparison | Required | Observed | Pass |
|---|---:|---:|:---:|
| History vs split mean, both cutoffs | >=10% lower error | 6.88% | no |
| History vs state | >=5% lower error | **3.82% higher** | no |
| History vs split mean at turn 100 | >=10% lower error | 5.31% | no |
| History vs mean, leave-opponent-out | >=5% lower error | 4.53% | no |
| Paired history wins over state | >=55% | 4/18 = 22.2% | no |

Normalized confirmation MAE is 1.274 for the split mean, 1.407 for map, 1.143 for state, and
1.187 for history.  State is the strongest representation.  History beats the population mean on
13/18 examples, but adds noisy, non-transferable detail and beats state on only four.

At turn 100, where v2 begins to diverge, history reduces mean-baseline error from 1.675 to 1.586
but state alone reaches 1.556.  Across all 42 leave-one-opponent-out examples, history (1.1603)
and state (1.1582) are effectively tied.

Artifacts: `replay-conditioned-continuation-protocol-2026-07-19.md`,
`replay-conditioned-continuation-2026-07-19.json`,
`cgauto/replay_conditioned_continuation.py`, and
`tests/test_replay_conditioned_continuation.py`.

## Multilevel interpretation

- **Observable state:** current production counters contain useful momentum; they improve 10.3%
  over the population mean on confirmation.
- **Action history:** recent verb rates and first-worker stats do not identify a transferable
  latent scheduler across agents.
- **Trajectory atoms:** selecting another agent's future is too coarse even when its prefix looks
  similar.  Recorded commands would be still more brittle under counterfactual interaction.
- **Population:** opponent identity is now the leading omitted variable.  The rich family contains
  stable but different submitted agents, not interchangeable realizations of one policy.

## Next experiment

Collect a result-blind, hash-selected completed-history panel for the six rich agents with repeated
Phase 21 occurrences: Bondo416, MSz, Meruem, celeria, gaha, and viewlagoon.  Each endpoint currently
offers at least 156 completed exact-agent battles, so freeze 24 eligible 150+-turn games per agent
(16 discovery, 8 confirmation).  Compare population and identity-conditioned mean/state/history
continuations.  Do not tune the failed cross-agent representation on these 21 games.

