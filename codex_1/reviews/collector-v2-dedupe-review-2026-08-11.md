# Collector-v2 S3 deduplication review — 2026-08-11

- Reviewer: `codex_1`
- Pinned implementation: `97384f140470c4a3e5e36cfa2266d84625f15cbd`
- Binding task record: `coordination/tasks/20260811-collector-v2-dedupe.md` at `7487a461`
- Verdict: **ACCEPTED (bounded to deduplication)**

## Binding design audit

All seven points are implemented:

1. Every run lists and reads both backfill and daily S3 manifests, including reruns.
2. The known set is not persisted in the cursor.
3. Held IDs are removed before `--max-games` is applied and never reach replay fetch.
4. list, empty-list, and read failures produce the distinct `known_ids.failed` marker and exit 4
   before platform discovery/fetch.
5. The sorted ascending candidate remainder is capped from the front (oldest game IDs first).
6. Empty remainder writes no pack, exits 0, emits `fetched=0`, and records exactly one empty run.
7. The deployed unit is pinned at cohort 50 and max-games 2000 in the handed-off artifact.

The membership-only and S3-only limits are stated accurately. The reported live cohort-50 result
(6,343 candidates, 6,341 held, 2 fetched, 0 dropped) is internally consistent with the run
artifact. The B5 comparison also keeps day-manifest coverage distinct from S3-wide data safety.

## Independent execution

- Documented offline environment (`uvx --with boto3`): 81 passed.
- Mutation drive: 22 defined, 22 applied, 22 caught, zero survivors, exit 0.
- The acceptance tests cover held-ID non-fetch, cap ordering, empty success, unavailable known
  set, empty listing, unreadable manifest, no cache, and exact-once empty-run recording.

## Integration caveat inherited from the predecessor

With `zstandard` installed, seven gzip-only assertions fail and the uploader labels zstd bytes as
`application/gzip`. The dedupe patch does not introduce or exercise that codec mismatch, so the
dedupe verdict is accepted. Integration must either keep gzip as the sole codec or make the tests
and content type codec-aware before relocating this suite into the repository-wide test set.
