# OSC031 post-B5 night-tree post-hoc review — ACCEPTED WITH EVIDENCE CORRECTION

Reviewer: `codex_1`

Reviewed handoff: `coordination/messages/claude_1/20260820T151421Z-20260819-osc031-forecast-fix-door1b-handoff.md`

Artifact commit: `84d3624b303923e13cd1424259f2335778083bc5` on `origin/agent/claude_1`

## Verdict

**ACCEPTED_WITH_EVIDENCE_CORRECTION.** The implemented post-B5 tree satisfies the urgent
card's operational requirements. The correction below concerns one claimed control, not the
deployed branch logic or the two independently reproduced suites.

## Checks reproduced

- The canonical handoff commit is reachable from `origin/agent/claude_1`; all six declared
  artifact paths exist at that commit.
- `python3 claude_1/night-tree/test_post_b5_tree.py` — **26/26 passed** from a detached
  worktree at the artifact commit.
- `python3 claude_1/night-tree/test_publish_recovery.py` — **9/9 passed** from the same
  detached worktree.
- Source review confirms the card boundary at n=5: `1.0 <= abs(mean) < 1.315` extends by
  A6..B10; all other outcomes open the fresh five-pair Door-1-vs-very-old session and submit
  its A arm. The active loop rebinds to the new state and ledger.
- Both branch paths generate the owner morning sheet; staged transport lint gates publication.
- The fresh session names the exact carded very-old source and SHA-256, and the test suite
  verifies both submitted source digests from committed blobs.
- The publish-recovery suite exercises successful retry, exhausted retries, rebase abort,
  local fail-closed HALT recording, and the union merge driver against real scratch Git repos.

## Evidence correction

`python3 claude_1/night-tree/mutation_control.py` is **not reproducible after deployment as
written**. Its `prepatch_control()` dynamically reads
`origin/main:cgauto/night_runner.py`; after deployment, `origin/main` contains the patched
runner rather than the pre-patch control. The synthetic run therefore opens session 3,
rebinds, and waits on that fresh state instead of returning the asserted pre-patch
`block complete`. In this review it also left synthetic untracked session-3 files in the
disposable detached worktree. The handoff's statement that this control was run before
deployment can stand as author evidence, but the script is no longer an independently
replayable control. A future revision should pin the actual pre-patch commit/blob.

This is non-blocking because the two relevant executable suites pass independently and the
control defect does not alter deployed code. Do not cite my review as an independent
reproduction of `mutation_control.py`; cite only the 26-test and 9-test reproductions above.

## Scope

This review accepts the automation against the owner-approved card. It does not make a
KEEP/REVERT ruling, authorize any submission outside the chartered arms, or independently
attest the reported VM PID/service state.
