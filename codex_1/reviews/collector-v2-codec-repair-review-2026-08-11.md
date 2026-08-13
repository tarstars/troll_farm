# Collector-v2 codec-independence repair review — 2026-08-11

- Reviewer: `codex_1`
- Pinned implementation: `879bc7ec60fa76d40a68bf2e1314b8e619276f70`
- Scope: repair of the optional-zstd integration defect raised in my prior reviews
- Verdict: **ACCEPTED**

## Code audit

The repair addresses both the symptom and the production defect:

- `packer.py` now derives extension, media type, and magic bytes from the selected codec.
- `collector.py` uploads pack bytes using `packer.CONTENT_TYPE`; zstd bytes are no longer
  mislabeled as `application/gzip`.
- Packer and collision tests use codec-derived extension/decompression/magic instead of encoding
  gzip assumptions.
- A collector test pins agreement among uploaded media type, extension, and active codec.
- C4b reinstates the hard-coded gzip media type and runs with `zstandard` installed, where the
  mutation is behaviorally reachable. The generalized mutation runner records per-mutant extras
  and restores its target from an in-memory original in `finally`.

## Independent execution

- Default environment (`uvx --with boto3`): 84 passed.
- Zstd environment (`uvx --with boto3 --with zstandard`): 84 passed.
- B3 mutation drive: 12 defined/applied/caught, zero survivors, exit 0.
- B4 mutation drive: 24 defined/applied/caught, zero survivors, exit 0; C4b executes under its
  declared `zstandard` extra.

No remaining codec-specific mismatch was found in the reviewed upload/pack/test path. This clears
the integration caveat in my exit-repair and dedupe reviews.
