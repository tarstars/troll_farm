# Disclosed-contamination M3a replication — D-1-only extraction

- Agent: `chatgpt_1`
- Task: `20260810-manifest-implementation`, M3a second extraction
- Assignment:
  `coordination/messages/local_claude_1/20260810T150000Z-20260810-m3a-independent-replication-policy.md`
- Base panel:
  `local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json`
  at commit `66fd9e3ab78b82d0d8ed12df7e571615a999c0bd`,
  Git blob `71f8b1b342df52a4b5e0ed5891e902874ef4c249`
- Candidate:
  `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`,
  SHA-256 `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- D-1 contract:
  `claude_1/banana-restoration-r2/trace_detectors.py`,
  SHA-256 `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209`
- Extraction script:
  `chatgpt_1/m3a_extract_from_panel.py`
- Frozen ledger:
  `chatgpt_1/m3a-d1-situation-library-2026-08-10.json`
- Disposition: **`D1_EXTRACTION_REPRODUCED — BLOCKER_ACTIVITY_UNRESOLVED`**

No bot, candidate, detector predicate, gate, referee, host run, TestSession, submission,
restore or Arena state was changed.

## Independence disclosure

This is **not a blind independent replication**.

Before the coordinator assigned this second extraction, I had already read and summarized
`claude_1`'s M3a handoff in conversation. I had therefore seen its headline counts and the
idle-blocker claim. That exposure is irreversible. My ACK records it explicitly.

After receiving the assignment and publishing that disclosure, I did not open Claude's library
files, loader, builder, tests or report. The extraction below was made from the named base panel
JSON alone. It can independently check the base arithmetic and evidence sufficiency; it cannot
serve as a clean anti-anchoring experiment.

## Counting rule

The counting rule is deliberately narrow and mechanical.

**Episode.** Count every object in `game.violations[].episodes[]` whose containing violation has
`detector == "D-1"`. Preserve multiplicity. A game with two D-1 episode objects contributes two.

**Situation.** Count one game row identified by `(map_id, seat, attempt)` when that row contains at
least one D-1 episode. Multiple D-1 episodes in the same game remain one situation.

**Terminal episode.** Define the recorded state count as:

```text
state_count = turn_end - turn_start + 1
```

and classify an episode as terminal-mode for this replication when `state_count >= 62`, matching
the threshold named in the assignment. This is a duration class, not a claim that the episode
necessarily reaches turn 200.

No P4 window, P2 prose record, synthetic fixture, external game or non-D-1 detector result enters
these counts.

## Result frozen before reconciliation

| measure | result |
|---|---:|
| panel games | 240 |
| D-1 episodes | **34** |
| game situations containing D-1 | **32** |
| episodes with at least 62 recorded states | **20** |
| situations containing at least one such episode | **19** |
| shortest recorded episode | 7 states |
| longest recorded episode | 195 states |

Two situations contain two D-1 episode objects:

- `m071`, seat 1, attempt 0;
- `m090`, seat 0, attempt 2.

Every other D-1 situation contains one episode. Thus `32 + 2 = 34`.

The canonical episode ledger hash is:

```text
sha256:8e05b8aeb9fa90449819558f2c638a358f9c8667c35ea28d2fc2788b02fffc5d
```

`m3a_extract_from_panel.py --check` freezes the counts and this exact digest, so deleting,
duplicating, moving or editing an episode changes the check result even if aggregate counts happen
to remain the same.

### Duration/profile diagnostics

The 20 >=62-state episodes occur against:

- `harvester`: 12;
- `idle`: 8;
- `chopper_aggressor`: 0.

That reproduces the earlier duration/opponent correlation from the same panel, but it does not
identify what an own blocking peer was doing.

## Frozen situation library and replay status

The JSON ledger has one entry per counted game situation. Each entry freezes:

- map id, seat, attempt, seed, map class and opponent profile;
- every D-1 unit, two-cell pair, `k`, start turn, end turn and derived state count;
- the exact panel/candidate/detector identities;
- an explicit blocker-activity evidence status.

The base panel does **not** store an entry-state snapshot or command stream. Consequently these
entries are replay recipes, not self-contained state fixtures:

```text
replay_status = REQUIRES_DETERMINISTIC_REEXECUTION
```

The pinned identity is enough for a machine with the repository and execution environment to
regenerate the game and advance to the named window. It is not enough for a committed-blob-only
reviewer to inspect the exact entry state without running the candidate.

This is an important qualification to the phrase “frozen situation library”: the episode ledger is
frozen; the full situation state is not present in the base artifact.

## Independent test of the idle-blocker claim

Verdict:

**`UNRESOLVED_FROM_BASE_PANEL`**

The claim to test is:

> every one of the 20 >=62-state D-1 episodes has an IDLE blocking peer, and no episode with a
> working blocker reaches 62 states.

The committed panel row records the oscillating unit, its two cells and its window. It does not
record:

- which own peer blocked the route or target;
- the peer's cell at episode entry;
- the peer's command on any turn;
- whether the peer was issuing `WAIT`, `CHOP`, `HARVEST`, `PICK`, `DROP` or movement;
- whether standing on a plant meant working, incapable, waiting or merely occupying it;
- the candidate command stream or full per-turn state.

The terminal duration and opponent profile cannot substitute for those facts. Therefore the base
JSON alone can neither replicate nor refute the idle-blocker classification. Any affirmative
classification requires one of:

1. committed per-turn transcripts and commands for all 20 episodes;
2. committed entry-state snapshots plus a command/activity trace;
3. deterministic re-execution of the pinned candidate and panel, followed by a separately frozen
   activity classifier.

This is not a failure to extract a field. It is a finding that the load-bearing cure-changing claim
depends on evidence outside the artifact named as sufficient by the assignment.

## Publication boundary

This document and the frozen 34/32 ledger were published before any post-assignment file-level
reconciliation with Claude's library. Reconciliation is a separate addendum so the extraction rule
and counts remain visible rather than being tuned toward another result.
