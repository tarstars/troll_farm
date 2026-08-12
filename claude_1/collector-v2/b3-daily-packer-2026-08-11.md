# B3 — daily packer (task `20260811-s3-collector-v2`)

- Author: `claude_1`, on the VM
- Date (real UTC): 2026-08-11
- Plan: `docs/superpowers/plans/2026-08-11-s3-phase1-collector-v2.md` Part B, task B3

## Result

**B3 passes.** 40 offline tests green; a 12-mutant drive over the packer catches **12/12, zero
survivors** (exit 0); and the packer verifies on the real corpus — 290 games, **`B3_VERIFIED`**,
every game byte-for-byte identical through the round-trip, identical bytes across two runs.

| Artifact | What it is |
|---|---|
| `claude_1/collector-v2/packer.py` | the packer |
| `claude_1/collector-v2/tests/test_packer.py` | 16 tests (part of the 40 in `claude_1/collector-v2/tests`) |
| `claude_1/collector-v2/b3_verify.py` + `b3-verification-2026-08-11.json` | real-corpus verification |
| `claude_1/collector-v2/run_b3_mutations.py` + `b3-mutation-results-2026-08-11.json` | the mutation drive |
| `claude_1/collector-v2/mutation_runner.py` | drive mechanics, now shared by B2 and B3 |

## Layout and schema

```
pack      games/raw/daily/YYYY-MM-DD.jsonl.gz     line: {"game_id","sha256","size","raw"}
manifest  games/manifest/daily-YYYY-MM-DD.jsonl   line: {"game_id","sha256","size","pack"}
```

Line schemas are **identical to Part A's** `data/scripts/pack_games.py`, so backfill and daily
objects can be read by one reader. That is pinned by a test that compares the exact bytes of a
pack line against Part A's encoding (`ensure_ascii=False, sort_keys=True`) — not just its parsed
content, which is a distinction two surviving mutants forced me to make (below).

**Compression is gzip, and the extension says so.** `zstandard` is not installed on this VM.
The extension is derived from the codec actually in use rather than hard-coded, because the
plan is explicit that the extension must name the truth.

## Determinism, and how it is actually pinned

Ids sort numerically, JSON keys sort, and **the gzip header's mtime is pinned to 0** — otherwise
the same games packed a second later would produce different bytes, and every digest comparison
downstream would be meaningless. There is no timestamp anywhere inside a pack; the date lives in
the object name, the only place it can live without breaking byte-identity.

Real-corpus numbers (`b3-verification-2026-08-11.json`): 290 games, 90,621,726 raw bytes →
12,478,353 packed (**13.8%**), round-trip byte-identical for all 290, identical pack bytes across
two runs, and identical when the input file list is reversed. Manifest covers every game, ids
sorted, every digest agreeing with the source file.

## What the mutation drive changed

The first drive caught 9 of 12. All three survivors were informative:

- **P3 (unsorted JSON keys)** and **P4 (`ensure_ascii=True`)** were **real test gaps**. Both
  round-trip fine and both are perfectly deterministic — they just produce different bytes from
  Part A. Nothing pinned the encoding, only the parsed content. Now a test asserts the pack
  line's exact bytes, its sorted key order, and that non-ASCII stays literal. Both mutants are
  now caught.
- **P12 was inert, not uncaught.** It mutated the `zstandard` branch's extension, which cannot
  execute on a host without `zstandard`. An inert mutant proves nothing about a suite, so it was
  re-aimed at the branch that does run here — gzip packs mislabelled `.jsonl.zst` — and that is
  caught.

Final: **12 defined, 12 applied, 12 caught, 0 survivors, exit 0.** The B2 drive was re-run on
the shared runner and still reports 10/10, exit 0.

## Limits worth stating

- **The real corpus contains no non-ASCII bytes** (`non_ascii_games: 0` across all 290 games),
  so unicode handling is pinned by fixtures only. It is exercised — a `тролль` nickname in the
  byte-level encoding test, chosen because the platform does return unicode nicknames — but not
  witnessed in this corpus. Same distinction B1 drew: pinned by test, not by population.
- **Empty days are normal and do not raise.** A day with no games yields an empty pack and an
  empty manifest rather than an error; the collector can run before the platform has anything.
- **Duplicate ids are refused, not merged.** Two staging directories can each hold the same
  game; packing both would double-count it.
- **A corrupt pack raises rather than returning.** `read_pack` re-verifies every embedded game
  against its own recorded digest and size; a pack that decompresses but does not hash correctly
  is an error, since storing the digest is pointless if nothing checks it.
- `rerun_key`-style naming (`YYYY-MM-DD.rerun-N`) is implemented and tested here, but the
  re-run *policy* belongs to B4.

## Deviation

Same as B2: tests live under `claude_1/collector-v2/tests/` because the repo's `tests/` tree is
outside my exclusive write set, so they are invoked by path
(`uvx --with boto3 pytest claude_1/collector-v2/tests -q`) rather than by a bare `pytest`.
The `--with boto3` is needed only by the B2 signing oracle; `test_packer.py` has no third-party
dependency.
