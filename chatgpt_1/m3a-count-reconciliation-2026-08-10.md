# M3a count reconciliation — 34 and 47 are different universes

- Agent: `chatgpt_1`
- Task: `20260810-manifest-implementation`
- Own extraction published first:
  - `chatgpt_1/m3a_extract_from_panel.py`
  - `chatgpt_1/m3a-d1-situation-library-2026-08-10.json`
  - `chatgpt_1/m3a-independent-replication-2026-08-10.md`
- Claude artifact reconciled afterward:
  `claude_1/banana-restoration-r2/oscillation-library-2026-08-10.md`
  at artifact commit `a6d5de6f750cafbd8d6d51795903d7e3192dcbc6`
- Disposition: **`COUNTS_RECONCILED — NOT TWO EXTRACTIONS OF THE SAME PANEL`**

## Result

There is no unexplained `34 -> 47` over-count.

The two numbers count different candidates, corpus versions, instruments and event kinds.

| component | my base-panel extraction | Claude M3a library |
|---|---:|---:|
| exact bot | `readable__no_orchard`, `98628e98...` | slim arena parent, `a8eb3b2b...` |
| source execution | already-committed panel JSON | fresh c3 rerun plus extra sources |
| corpus/instrument | panel artifact named in assignment | `c3-train-engine-authority-2026-08-09` |
| D-1 episodes | **34** | **36** |
| P4-only stall windows added | 0 | **10** |
| real-corpus partial added | 0 | **1** |
| total episode multiplicity | **34** | **47** |

The arithmetic is exact:

```text
47 - 34 = (36 - 34) + 10 + 1 = 2 + 10 + 1 = 13
```

Thus the apparent thirteen-episode discrepancy consists of:

1. **two additional D-1 episodes** produced by a different bot/corpus/referee run;
2. **ten P4 stall windows** that are not D-1 alternation episodes at all;
3. **one partial real-corpus record** outside the 240-game panel.

Claude's report states this directly under `kind and completeness`:

```text
D1_EPISODE  27 situations  36 episodes
P4_STALL     5 situations  10 episodes
REAL_CORPUS  1 situation    1 episode
total       33 situations  47 episodes
```

## Why 32 and 33 situations are not directly comparable

My situation rule is game-row identity:

```text
(map_id, seat, attempt)
```

It keeps all 34 D-1 episode objects and produces 32 game situations; only `m071-s1-a0` and
`m090-s0-a2` contain two episodes.

Claude applies a different, cross-game dedupe:

```text
kind | mechanism | blocker_state | canonical local-geometry stencil
```

Its 47 mixed-source episodes collapse to 33 representative files. Its 27 D1 files represent 36
D-1 episodes by multiplicity, and its remaining six files represent five P4 classes plus one
real-corpus record.

Therefore the one-situation difference is not evidence that one extractor lost or invented a game.
The term “situation” has two incompatible definitions.

## Correction to the assignment premise

The policy states:

> two extractions of the same 240-game panel already disagree

That premise is false for the published Claude artifact.

My 34/32 result is an extraction from the exact committed panel named in the policy:
`readable__no_orchard` against itself.

Claude's 47/33 result is a new library assembled from:

- a fresh c3 floor rerun of a different slim parent;
- D-1 episodes and P4-only stalls;
- an additional partial real-corpus source;
- a mechanism/geometry dedupe rather than game-row identity.

Both artifacts may be useful, but they are not independent implementations of one population and
cannot validate each other by count equality.

## Idle-blocker claim after reconciliation

Claude's report supplies a concrete operational classifier:

```text
IDLE iff peer wait fraction >= 0.95 and peer cell changes == 0 over the window
```

It reports the following cross-tab over its **36 c3/slim-parent D-1 episodes**:

| blocker class | >=62 states | <62 states |
|---|---:|---:|
| IDLE | 20 | 3 |
| WORKING | 0 | 7 |
| no blocker established | 0 | 6 |

This is execution-derived evidence carried by Claude's frozen states and command windows. It is
not present in the committed `readable__no_orchard` panel summary that my assignment named as
sufficient.

My replication result therefore remains:

**`UNRESOLVED_FROM_BASE_PANEL`**

I neither replicate nor refute the classifier's 20/20 result for Claude's different c3 population.
A proper second test requires replaying the original 34 episodes—or independently checking
Claude's 36 full traces—with the activity rule frozen before seeing the output.

## Consequence for M3b and the oscillation cure

Before M3b starts, the owner must choose and name its subject universe.

### Option A — original readable subject

Use the 34 D-1 episodes / 32 game situations from the exact `98628e98` committed panel. Regenerate
and freeze entry states and command windows for those identities. This directly answers the
manifest's named subject.

### Option B — current broader c3 diagnostic library

Use Claude's 47 mixed-source episodes / 33 geometry-mechanism representatives. This has richer
state and replay evidence and deliberately includes P4 stalls, but it is not the original
readable-only D-1 corpus.

Mixing A's subject statement with B's evidence would reproduce the project's recurring
wrong-artifact problem.

The idle-yield rule may still be a strong hypothesis. This reconciliation removes the claim that it
has already been independently replicated. The load-bearing 20/20 result currently rests on one
execution-derived extraction and should retain that evidence status until a second trace-level
review lands.
