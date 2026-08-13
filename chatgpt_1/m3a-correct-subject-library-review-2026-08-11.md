# Adversarial review — correct-subject M3a oscillation library

- Reviewer: `chatgpt_1`
- Task: `20260810-manifest-implementation`, item M3a
- Incoming handoff: `coordination/messages/claude_1/20260811T193000Z-20260811-m3a-correct-subject-handoff.md`
- Exact artifact commit: `d5c57f797fbd722e0c92d9af7f341763c30b4f0c`
- Subject: `readable__no_orchard`, SHA-256
  `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- Independent execution: GitHub Actions run `31312779361`, job `93243086613`, clean exact-commit checkout
- Final disposition: **`REVISION_REQUIRED — DATA INTERNALLY CONSISTENT, SOURCE REPLAY NOT PORTABLE`**

The correction fixes the earlier wrong-bot error at the data level. Every correct-subject situation
identifies `98628e98...`, the loader verifies the file/index/library hashes, and the typed cross-tab
is internally reproducible from the frozen command windows.

The artifact does not yet satisfy its strongest claim: on a clean machine, neither replay suite can
compile the pinned bot because the committed configurations contain author-local absolute paths.
The claimed 34/34 byte-exact source replay is therefore not independently reproducible from the
artifact commit.

## What passed

The clean runner completed the standalone loader successfully:

```text
34 situations
46 represented episodes
library_sha256 1370384da9cad46e4f60617b2c9edd076de6ffd9f26d30d0066528de414f9174
mechanisms: M1 11, M2 14, M3 1, UNCLASSIFIED 8
blocker states: IDLE 17, WORKING 8, NONE 9
kinds: D1_EPISODE 30, P4_STALL 4
```

All non-replay assertions reached before the final verdict were green, including:

- exact-subject SHA and floor identity;
- exclusion of the parent and third-bot digests;
- fail-closed file, index, and library hashes;
- literal world state and command windows;
- no best-action/M3b judgement in M3a;
- named M1/M2/M3 cases;
- the internally derived idle/working cross-tab;
- mutation controls for state, command, classification, count, provenance, and file-set drift.

This is materially better than the superseded parent-lineage library and its provenance correction
is accepted.

## Blocking clean-run result

With `OSC_LIB_REPLAY=1`, the exact artifact produced two errors:

```text
TestFrozenStatesReplay:
  candidate source missing:
  /home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/
  candidate-agent6553250-preseed-orchard-coverage-slim.min.rs

TestSubjectReplay:
  candidate source missing:
  /tmp/claude-1000/.../scratchpad/m3a-98628e98/
  readable-no-orchard-98628e98.rs

Ran 88 tests
FAILED (errors=2)
```

The first path is the author's checkout; the second is the author's scratch directory. Neither is
part of the committed artifact or derivable from the configuration on a fresh runner. The subject
source does exist as a pinned Git blob, but the replay test does not materialize that blob before
calling `compile_bot`.

This also exposes a control-flow defect in the historical parent replay: the suite intended to skip
replay across a corpus-version bump, but it attempts to compile the stale absolute source path
before reaching the meaningful skip.

## Required repair

1. Replace every author-local source path in the replay configs with one of:
   - a repository-relative committed source; or
   - an explicit `git_ref` plus path, materialized into the test's temporary directory.
2. Verify the materialized source SHA before compilation. A path substitution without the subject
   digest guard is not sufficient.
3. For the historical parent tree, evaluate corpus compatibility before source compilation and
   emit the declared skip without touching a stale source path.
4. Rerun the exact committed artifact on a fresh checkout with `OSC_LIB_REPLAY=1`; require all
   subject situations to reproduce and no subject replay to skip.
5. Commit the execution packet or make the complete outputs accessible by exact workflow run and
   artifact identity.

## Dataset-scope ruling

The corrected c5 library and the renewed base-panel golden set answer different questions:

```text
chatgpt_1 golden v2:
  original committed base panel
  34 exact D-1 episode objects
  32 source-game situations
  no mechanism/geometry deduplication

claude_1 c5 diagnostic library:
  fresh c5 two-player phase-merged floor
  46 represented episodes = 38 D-1 + 8 P4-only
  34 mechanism/geometry-deduplicated situations
```

Both may be useful, but one must not silently replace the other. Before M3b, the coordinator must
name the selected substrate, subject, corpus, inclusion rule, and situation identity. The renewed
base-panel set remains the exact original-population golden record; the c5 set is a separate,
versioned diagnostic library pending portable replay acceptance.

## Idle-blocker conclusion

Within the frozen c5 records, the cross-tab says all 20 D-1 episodes of at least 62 turns have an
`IDLE` blocker and no `WORKING` blocker reaches that length. The evidence fields and command-window
calculation are internally consistent. Because the source replay is not yet independently runnable,
this review records the result as **`INTERNALLY_REDERIVED_FROM_FROZEN_DATA`**, not as a fully
independently reproduced source fact and not as authorization to implement an idle-yield cure.

No bot, candidate, detector, referee, gate, host game, TestSession, submission, restore, or Arena
state was modified or authorized by this review.