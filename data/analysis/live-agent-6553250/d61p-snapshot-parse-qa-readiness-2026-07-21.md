# D61p snapshot parse/QA readiness (2026-07-21)

## Status

The snapshot-scoped parser, integrity verifier, split freezer, and confirmation sealer are
implemented and locally verified. No network or platform request was made.

## Frozen implementation

- implementation protocol SHA-256:
  `ad6eab29c00f8b8da46e7d7e699a698e22eae1297810c05252668ca948dcf277`
- `data/scripts/parse_snapshot.py` SHA-256:
  `a68f8f26ba9dc0a897909e2b4053dee30ceb643d61d20bd3a6ad98def38fa641`
- `tests/test_parse_snapshot.py` SHA-256:
  `6582cc3aae327265eefb991972e20b52cf23b4cf3ff2c012dc930a6795e2236e`

The entry point verifies every acquisition-manifest file and replay-cache hash, parses only named
eligible game IDs, supplies recorded command context to the official diff-state decoder, checks
turn/state alignment and final inventories/scores, enforces exact terrain and initial-plant point
symmetry, detects duplicate game/trajectory content, freezes the two-hash resident split, and
publishes atomically below the source snapshot.

Confirmation game outcomes and trajectories are written only below
`processed/sealed_confirmation/`. Open QA rows expose their identity, split, and integrity boolean
only; open turn histograms exclude them. Split manifests contain no scores. Detailed confirmation
parse failures are also sealed.

## Verification

The focused parser/collector/QA/conformance test set reports:

```text
24 passed in 0.10s
```

Coverage includes snapshot hash tampering, replay-cache tampering, split hashing/agreement,
confirmation file separation and QA redaction, atomic overwrite refusal, final-state decoding,
score classification, collector immutability/pacing, and transition-classification helpers.
One end-to-end test feeds the collector's exact files directly into the parser and reaches a clean
parsed replay without schema adaptation.

Two read-only compatibility audits add real-corpus evidence:

- all 1,302 existing parsed maps pass the new exact terrain and initial-plant symmetry checks; and
- a deterministic 63-replay edge-spread raw sample parses 17,960 resolved turns with 63 exact score
  matches and zero failures.

## Invocation after collection

After an explicitly authorized collector run produces a completed snapshot:

```bash
.venv/bin/python data/scripts/parse_snapshot.py data/raw/snapshots/<snapshot-id>
```

Inspect and hash `processed/manifest.json`, `qa.json`, and `split_manifest.json` before beginning any
field analysis. A failed volume gate preserves the snapshot and does not authorize expanding the
sampling frame. This parser authorizes no TestSession, Arena, or submission action.
