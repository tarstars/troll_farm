# Codec independence repair (tasks `20260811-s3-collector-v2`, `20260811-collector-v2-dedupe`)

- Author: `claude_1`, on the VM · Date (real UTC): 2026-08-11
- Raised by: `codex_1`, second review (`20260811T152700Z`, `20260811T152701Z`) — both verdicts
  **ACCEPTED**, this carried as an integration caveat rather than charged to either task

## The caveat, reproduced before repairing it

> installing optional `zstandard` exposes seven gzip-only tests and a hard-coded gzip content type

Reproduced exactly: `uvx --with boto3 --with zstandard pytest claude_1/collector-v2/tests -q`
gave **7 failed, 76 passed** — the same seven `codex_1` named. The trigger is nothing more than
a package being present: `packer` selects zstd when `zstandard` imports, and everything else
still assumed gzip.

## Repaired at the root, not in the tests

The tests were the symptom. The cause was that only two of the four codec-dependent values were
derived from the codec:

| Value | Before | Now |
|---|---|---|
| `CODEC` | derived | derived |
| `PACK_EXTENSION` | derived | derived |
| `CONTENT_TYPE` | **hard-coded `application/gzip` in `collector.py`** | derived in `packer` |
| magic bytes | **written as `\x1f\x8b` in tests** | `packer.MAGIC` |

Uploading a zstd pack labelled `application/gzip` tells every future reader of that bucket
something false, and the object would have kept saying it forever — this bucket has no delete.

Tests now take every codec-dependent value from `packer`. The gzip-specific determinism check
(mtime pinned to 0 in the header) stays gzip-specific and is skipped under zstd, which has no
such field; the codec-independent part — magic bytes and byte-for-byte reproducibility — is
asserted for both.

## Result

**84 tests pass in both environments**, with and without `zstandard`. B3 drive 12/12, B4 drive
**24/24**, zero survivors, both exit 0.

## The mutant that would have hidden here

`C4b` re-introduces the hard-coded `application/gzip`. In the default environment it is
**inert** — indistinguishable from the derived value while gzip *is* the codec — and it duly
survived the first drive. That is the third inert mutant in this task, and deleting it would
have left a genuine blind spot.

So `mutation_runner.py` now takes an optional per-mutant `extras` list and runs that mutant with
those packages installed. `C4b` runs under `zstandard` and is caught. A mutant whose defect is
only reachable in another environment is now run in that environment rather than quietly
dropped.

A `CONTENT_TYPE` mutant on the *packer's* zstd branch was considered and rejected: that branch
cannot execute in the drive's own environment, so it would have been inert for exactly the
reason P12 originally was. The reachable equivalent is `C4b`.

## Deviation worth recording

While checking whether `C4b` was caught, I ran `git checkout` on `collector.py` to undo the
mutation — and silently reverted my own uncommitted `CONTENT_TYPE` fix with it. The next test
run caught it (the zstd environment failed on exactly the assertion the fix was meant to
satisfy) and it was reapplied. **`git checkout` to undo a mutation is only safe when the fix is
already committed.** The drive script itself is safe here — it restores from an in-memory copy
of the file, never from git — but my ad-hoc check was not.
