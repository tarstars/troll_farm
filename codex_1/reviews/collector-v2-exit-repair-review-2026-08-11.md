# Collector-v2 exit repair review — 2026-08-11

- Reviewer: `codex_1`
- Pinned implementation: `030fb2e150b3949c6bfe5f3351bc2bcd5fb79f1a`
- Scope: the fetch-failure exit repair requested by my review of `406b67bb`
- Verdict: **ACCEPTED (bounded to the repair)**

## Result

The defect is repaired. `collector.py` now assigns exit 3 whenever any replay fetch fails,
after completing the sweep. Permanent HTTP 422 failures remain classified and counted but no
longer excuse the run from a nonzero end marker. This also fixes the sharper mixed case in which
one permanent failure previously masked transient failures beside it.

The coordinator phrase "exit nonzero with the failure count" is satisfied as a nonzero status
plus the exact counts in the structured `fetch` marker and run record. Treating the count itself
as a process exit status would truncate counts above 255 and would be a weaker interface.

## Independent execution

- Focused permanent/mixed/sweep-continuation tests: 3 passed.
- Documented offline environment (`uvx --with boto3`): 83 passed.
- Mutation drive: 23 defined, 23 applied, 23 caught, zero survivors, exit 0. The new C8b mutant
  reinstates the precise faulty predicate and is caught.

## Integration caveat outside this repair

With `zstandard` installed, seven pre-existing gzip-only assertions fail: three upload-key tests
hard-code `.jsonl.gz`, four packer tests use `gzip.decompress`, and upload content type remains
hard-coded as `application/gzip` while the packer selects `.jsonl.zst`. This is not introduced by
the exit repair, and the deployed/documented VM environment lacks `zstandard`, so it does not
change the bounded verdict. It must be resolved or the optional codec removed before relocating
the suite into an environment that installs `zstandard`.
