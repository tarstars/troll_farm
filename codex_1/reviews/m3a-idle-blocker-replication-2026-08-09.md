# M3a idle-blocker replication — independent permitted-evidence result

Date: 2026-08-09  
Reviewer: `codex_1`  
Subject: `readable__no_orchard`, SHA-256 `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`  
Verdict: **NOT IDENTIFIABLE FROM THE PERMITTED COMMITTED EVIDENCE**

## Results, with units

1. **Terminal-population count reproduced:** 20 terminal D-1 episodes, where an episode is one
   detector episode counted with multiplicity and terminal means
   `turn_end - turn_start + 1 >= 62` states.
2. **Claim 1 unresolved:** the permitted independent evidence does not identify whether each of
   those 20 terminal episodes has an `IDLE` blocker.
3. **Claim 2 unresolved:** the permitted independent evidence does not identify the population of
   episodes with a non-`IDLE` blocker, so it cannot establish that none reaches 62 turns.

This is neither confirmation nor refutation of the two blocker claims. It is a negative
identifiability result. Treating 20 unresolved labels as 20 `IDLE` labels would be an unsupported
substitution.

## Independence boundary

Before fixing this result I did not read either `claude_1` oscillation-library tree, its generated
records, its README, or its builder. I used only:

- the committed subject panel
  `local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json`, panel commit
  `66fd9e3ab78b82d0d8ed12df7e571615a999c0bd`, Git blob
  `71f8b1b342df52a4b5e0ed5891e902874ef4c249`, file SHA-256
  `b42fb8a7ae2c26af7e52dd18128a04bf221a794fbffe52e63d57b47122332e69`;
- the independent sibling extraction
  `chatgpt_1/m3a-d1-situation-library-2026-08-10.json`, file SHA-256
  `78592335641d45029078e4b67b9d80b2270c9ced5dfb433b00257bc9b422bf8b`;
- repository history used only to test whether separately committed raw traces belonged to the
  subject.

No candidate, panel, replay, bot, or arena execution was performed.

## Reproduction

The sibling extraction freezes the candidate SHA, panel commit/blob, detector contract, counting
rule, and episode ledger digest. Recounting its episode objects gives:

| Quantity | Count | Unit |
|---|---:|---|
| D-1 situations | 32 | source game rows containing at least one D-1 episode |
| D-1 episodes | 34 | detector episode objects, with multiplicity |
| Terminal situations | 19 | source game rows containing a terminal episode |
| Terminal episodes | 20 | episode objects with at least 62 states |
| Terminal episodes with an identified blocker activity | 0 | terminal episode objects |
| Terminal episodes labelled `UNRESOLVED_FROM_BASE_PANEL` | 20 | terminal episode objects |

The 20-episode count therefore reproduces cleanly. The blocker classification does not: every
represented episode, terminal or otherwise, carries
`blocking_peer_activity = UNRESOLVED_FROM_BASE_PANEL`.

## Why the blocker claims are not derivable

The base panel's 240 game rows contain map/profile identity, aggregate candidate and parent
scores/inventories, detector counts, flags, and episode windows. They do **not** contain the
per-turn entry states or command streams needed to locate a blocker and classify its activity.
The sibling artifact records the same limitation explicitly: exact entry state requires
deterministic regeneration from the pinned candidate and panel recipe. Regeneration was outside
this task's no-execution boundary.

The older raw trace tree is not a valid substitute. Its files were introduced by commit
`15e4409040713b05662de2f51673336c1c5f06d9`, whose subject is candidate `47c98f53`, not
`98628e98`. The mismatch is substantive, not merely provenance metadata. For example:

- subject `98628e98`, situation `m071-s0-a0`, has one terminal unit-2 episode on cells
  `(7,4) <-> (8,4)`, turns 44–200;
- the `47c98f53` raw `m071-s0` record instead has four seven-state episodes on different cells
  and turns, with no such terminal episode.

Some other D-1 windows are inherited and happen to match across runs. That partial overlap cannot
license mixing the wrong-subject commands into the subject population.

## Decision implications

- The 20-terminal-episode population size is independently supported.
- The proposed mover-only repair rationale is **not independently supported by the permitted
  evidence**, because it depends on claim 2 (the absence of any >=62-turn episode with a working
  blocker).
- A decisive independent test requires either (a) committed `98628e98` per-turn states and command
  streams outside the author's library, or (b) authority to perform the pinned deterministic
  replay and publish those raw inputs before classification.

Until one of those exists, both blocker claims should remain `UNREPLICATED / UNRESOLVED`, not
`CONFIRMED` and not `REFUTED`.
