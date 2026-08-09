# M3a golden-bundle renewal v2

The v1 bundle's data was correct, but its golden JSON predated the extractor's `episode_ledger_sha256` field. This renewal regenerates the JSON, moves the verifier/tests to a v2 manifest, and re-pins every source, tool, test, and output byte together.

- verifier exit code: `0`
- tests exit code: `0`
- external execution and cross-implementation reviews remain mandatory; this commit is not self-acceptance.
