# Canonical human-readable source format — owner ruling 2026-08-11

**The canonical human-readable format for bot sources is idiomatic rustfmt, produced by
`claude_1/readable-source/format_readable.py`** (salvaged from the 2026-08-10 stranded-work
archive; authored in the readable-source effort):

- rustfmt with `reorder_imports = false`, `max_width = 100`;
- rustfmt's token-level insertions (trailing commas) are reconciled back out by token-stream
  diff — any other token difference aborts the build;
- **round-trip is mandatory**: compacting the readable file with
  `cgauto/compact_rust_source.py` must reproduce the exact minified parent SHA-256. A
  readable artifact without a passing round-trip is not a readable artifact.
- rustfmt version at ruling time: `rustfmt 1.9.0-stable (8bab26f4f6 2026-07-14)`. Version
  drift is tolerated only while the round-trip gate passes; a rustfmt upgrade that changes
  layout produces a **new** readable artifact, never an edit of an existing one.

**The formatter hazard stands unchanged**: no formatter ever runs in place over
`rust/src/bin/` or `cgauto/` (experiment locks record file hashes). The canonical format
applies to *derived* readable copies only.

**Line-count rule** (resolves the e7a 375-vs-586 question): readable line counts are
formatting-dependent, so **bytes are the canonical cost measure** — the E7a orchard strip is
**15,013 bytes = 23.9%** of the 62,820-byte program, agreed byte-exactly by both
measurements. Any published line figure must name its expander: 375 lines under the
2026-08-04 task's expander (`coordination/tasks/20260804-readable-orchard-loc-cost.md`);
586 lines under the stricter stranded expander
(`archive/local_codex_1-stranded-20260810:local_codex_1/readable-orchard-code-cost/`).
A line figure under the canonical format may be derived on demand with
`format_readable.py`; until someone does, no unattributed line count is quotable.

Related, distinct tool: `claude_1/readable-source/expand_to_readable.py` is a
whitespace-and-comments-only annotator — valid as a measurement/annotation instrument,
not the canonical reading format.

## Delivery of bot changes — owner ruling 2026-08-26 (morning)

The owner wants to get acquainted with the code and read every change: **candidate changes to a
bot are delivered as GitHub pull requests against `main`**, with the patch visible on the
canonical readable source (a `readable/*.rs` file produced by `format_readable.py`, round-trip
proven against its compact parent). Shape of a candidate PR:

1. **Commit 1 — the readable baseline** of the base bot (no behaviour change; the round-trip
   report beside it), if that baseline is not already on `main`.
2. **Commit 2 — the change** on the readable file (the diff the owner reads), the regenerated
   compact submission file under `cgauto/submissions/` with its sha256 pinned in a manifest, and
   the panel evidence.
3. A plain-words PR body: the question, the clause before/after, the panel table, the named
   games, the digests, the platform plan.

The owner reviews and merges (or says "merge"). Code reaches `main` by no other route. The
formatter hazard is unchanged: `format_readable.py` writes a *new* readable file; nothing runs in
place over `cgauto/` or `rust/src/bin/`. First instances: `20260826-candidate-0-regeneration-fallback`,
`20260826-candidate-3-keep-your-goal`.
