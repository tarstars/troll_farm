# Collector v2 independent review — 2026-08-11

Task: `20260811-s3-collector-v2`  
Reviewed artifact: `406b67bb125546ad956aa410d3f336d8f293537d` on `agent/claude_1`  
Reviewer: `codex_1`  
Verdict: **REVISION_REQUIRED**

## Scope and execution

I reviewed the binding Part B B1-B6 plan, all five reports, `s3client.py`, `packer.py`,
`collector.py`, `compare.py`, the two systemd units, and the offline tests. I did not mutate the
bucket, platform, VM service, credentials, or Arena.

Independent execution from a detached worktree at the pinned commit:

- `uvx --with boto3 pytest claude_1/collector-v2/tests -q`: **70 passed**.
- B2 mutation drive: **10/10 caught**, zero survivors, exit 0.
- B3 mutation drive: **12/12 caught**, zero survivors, exit 0.
- B4 mutation drive: **14/14 caught**, zero survivors, exit 0.
- Read-only B5 run against the coordinator's pinned 361-id export: bucket 600, reference 361,
  overlap 9, missing 352, extra 591, verdict `GAPS`. This reproduces the coordinator's warning:
  the current top-10/cap-300 collector and the frozen wider cohort are not cut-over-equivalent.

The implementation is strong on deterministic packing, conditional uploads, cursor durability,
post-upload verification, staging retention, pagination, credential permissions, and end-marker
survival. One binding failure remains.

## Finding F1 — permanent replay failures incorrectly produce a successful run

Severity: high for monitoring correctness.  
Location: `claude_1/collector-v2/collector.py:355-356` at the reviewed commit.

The coordinator's binding B4 ruling says a same-day replay fetch failure is a real error in the
`exit=N` marker; the collector must finish the remaining sweep and then exit nonzero. The code
does that only when `fetch_failures` exists **and none are permanent**:

```python
if exit_code == 0 and fetch_failures and not permanent:
    exit_code = 3
```

Consequently, one or more HTTP 422 replay failures with every other operation successful return
`exit=0`. The current test explicitly pins this incorrect behavior in
`test_permanently_gone_game_does_not_fail_the_run`.

This is not merely a naming disagreement. Journald/health automation reads the end marker as the
run's completion signal. `exit=0` states the day completed cleanly even though a discovered replay
was not archived, and a mixed permanent+transient failure also returns 0 because `permanent` is
non-empty. The run report contains the failures, but the binding observability channel suppresses
them.

Required repair:

1. Return nonzero whenever any replay fetch fails after completing the rest of the sweep.
2. Preserve the permanent/transient classification and counts in the report/log; distinct exit
   codes are optional, but zero is not.
3. Replace the existing 422-success test with a failing-control-backed test requiring nonzero.
4. Add a mixed 422+transient test so the boolean cannot regress to the current `not permanent`
   mistake.
5. Re-run the 70-test suite and B4 mutation drive, adding a mutant for this branch.

## Non-blocking observations

- Pack and manifest uploads are two separate conditional PUTs. An inconsistent pre-existing state
  or interruption after the pack PUT can leave an orphan pack before the rerun key succeeds. This
  does not overwrite data, and readers are manifest-driven, so it is cleanup debt rather than a
  correctness blocker; document it and consider a future orphan census.
- `content_type="application/gzip"` is fixed in `upload_day` even though the packer supports zstd.
  The deployed host uses gzip, so current bytes are labelled correctly. If zstandard becomes
  installed, derive the MIME type from `pack.codec` alongside the extension.
- The B5 `GAPS` result is expected evidence, not a collector-code failure. It proves the current
  deployment cannot satisfy the later cut-over criterion until cohort/cap semantics change.

## Disposition

**REVISION_REQUIRED**, bounded to F1. Focused re-review is sufficient after the repaired commit,
tests, and B4 mutation evidence are published. The dependent S3-known-id dedupe task may proceed;
it should not obscure or silently absorb this predecessor fix.
