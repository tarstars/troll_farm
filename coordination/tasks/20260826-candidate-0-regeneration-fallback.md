# 20260826-candidate-0-regeneration-fallback: Candidate 0 — the champion's replant fallback keeps the moves it built; delivered as a GitHub PR; measured on the platform as an 8-exposure self-replacement block

- Status: **OPEN — CHARTERED 2026-08-26T06:05Z by owner ruling** (coordinator session ~06:00Z,
  the coordinator's transcription): *"I want to measure impact of these changes on platform: check
  that the bot we are going to fix as Candidate 0 has its score on platform. After change give it
  platform measurement AAAAAAAA (8 expositions, self-replacement). I want to get acquainted with
  code, do changes through github PR."*
- Record owner: local_claude_1 · Work owner: **claude_1** (readable baseline, the fix, panel, the
  PR branch) · Reviewer: **codex_1** (the diff and the panel from a fresh archive) · PR reviewer
  and merger: **the owner** · Arena controller: local_claude_1 (the block is owner-authorized by
  this charter; each submission is surfaced before it starts).
- Area: a champion bug fix. Base: the champion **`cgauto/submissions/candidate-door1-pure-deletion.rs`**
  (sha256 `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`, 75,653 bytes) —
  **not** Candidate 1's source (the hold is parked) and not Candidate 2's.
- Inputs: the diagnosis `claude_1/cure2/m061-diagnosis-2026-08-25.md` §4 (the clause, measured
  at the code line with a print-only probe); claude_1's 2026-08-21 anti-benching Phase 3a report
  (the same defect, then unanswered); rule R-2 (`docs/RULES-LEDGER.md`).
- Branch: `candidate-0/regeneration-fallback` (a PR branch off `main`), work also mirrored on
  `agent/claude_1`; review on `agent/codex_1`; record on `agent/local_claude_1`.
- Progress lease: 15 minutes without concrete evidence.
- Created UTC: 2026-08-26T06:05:00Z · Last updated UTC: 2026-08-26T06:05:00Z

## THE QUESTION (owner's, plain words)

When a map has no trees left, the champion's planner builds "plant a new one" moves (two `PICK`s
worth 7,500 on `m061`) and then, in a fallback branch meant for the idle case, **returns a bare
`WAIT` and throws them away** — both trolls stand goal-less to the end of the game (131 and 96
turns on `m061`, 75 points). That is a troll with available work not employed (rule R-2). **Fix
it in the champion itself, show the fix as a pull request I can read, prove on the panel that it
changes nothing else, and measure it on the platform eight times.**

## The change — one clause, read from the code

In `main_candidates` (champion), the branch

```rust
let chops = Self::yamo_chop_candidates(view, unit, type_to_cut, opponent_eta_penalty);
if idle_regeneration && chops.is_empty() {
    let mut fallback = vec![MoisanBot::wait()];
    fallback.extend(Self::idle_harvest_candidates(view, unit));
    if unit.total_carried() > 0 { fallback.extend(Self::bank_candidates(view, unit)); }
    return fallback;            // returns `fallback`, DISCARDING `out`
}
```

becomes: the fallback **extends** `out` (the candidates already built — the regeneration `PICK`s
included) instead of replacing it, and returns the extended list. The exact edit is the builder's
to propose at G-0 (extend vs. append order, and whether `WAIT` stays first); the intent is fixed:
**nothing already built is discarded; nothing new is invented.** No other line changes.

## Delivery — the readable diff file (owner amendment 06:10Z: "not exactly PRs — I want to see diffs in files"; a PR is optional)

**The deliverable of record is `readable/diffs/candidate-0-regeneration-fallback.diff`** — a
unified diff of `readable/door1-champion.rs` (now on `main`, round-trip EXACT) → the fixed readable
source `readable/candidate-0-regeneration-fallback.rs`, beside its round-trip report and the
regenerated compact arm. The coordinator integrates these onto `main` after codex_1's review, so
the owner reads the diff at `https://github.com/tarstars/troll_farm/blob/main/readable/diffs/candidate-0-regeneration-fallback.diff`.
The PR shape below is kept as the description of the change's parts; opening an actual PR is
optional.

### The original PR shape (kept as the description of the parts)

1. **Readable baseline first.** `claude_1/readable-source/format_readable.py --compacted
   cgauto/submissions/candidate-door1-pure-deletion.rs --readable readable/door1-champion.rs
   --report readable/door1-champion.round-trip.json`; the round-trip gate
   (`cgauto/compact_rust_source.py` reproduces `547fa706…` byte-exactly) must pass — a readable
   artifact without it is not a readable artifact (`docs/readable-format.md`). **Commit 1** of the
   PR: the readable champion + its report, no behaviour change.
2. **The fix. Commit 2:** the edit on `readable/door1-champion.rs` — the diff the owner reads —
   plus the regenerated compact arm `cgauto/submissions/candidate-0-regeneration-fallback.rs`
   (compacted from the readable file, its sha256 pinned in a manifest) and the panel results.
3. **PR against `main`** from `candidate-0/regeneration-fallback` (`gh pr create`, by claude_1 if
   it has `gh` on the VM, else by the coordinator from claude_1's pushed branch): title in plain
   words, body = the question, the one clause before/after, the panel table, the named games, the
   round-trip digests, and the platform plan. **The owner reviews and merges** (or says
   "merge" and the coordinator merges). Nothing is integrated into `main` by any other route.

## Gates

- **G-0 (codex_1, ack-required, before the fix is written):** the exact edit (line, before/after),
  the readable-baseline plan and round-trip digests, the panel plan below, the PR layout.
- **G-1 panel (claude_1 builds; codex_1 reproduces from a fresh archive):** on the 240-game panel
  and the 34 fixtures, the fixed arm vs the champion: **byte-identical in play on every game where
  the fallback never fires** (the fallback's firing turns are logged by a print-only probe arm, as
  in the `m061` diagnosis); every game that changes is named with its first divergence and its
  score delta **in own-score points**; `m061` both seats must show the replant cycle resuming
  (the two trolls no longer goal-less); D-1 / D-3 / P3 / P4 / **P4b (`--p4b` ON, v4 instrument
  arm)** not worse than the champion, every change named; determinism (two runs byte-identical).
  Expected shape, stated before the run: a small number of changed games (those reaching an
  empty map with fruit in hand), no change elsewhere.
- **G-2 platform — the owner's block, authorized by this charter:** after the PR is merged, the
  merged arm `candidate-0-regeneration-fallback.rs` (sha256 verified) is submitted **eight times
  in succession, each submission replacing the previous one** ("AAAAAAAA"); each read taken at
  maturity as the 08-23 block defined it (the game burst finished, ≈160 games, the score flat
  across ≥ 3 checks over ≥ 20 minutes), recorded with submission id, agent id, games, score,
  rank; games collected before the next submission (`collect_submission_games.py`). The ledger:
  `local_claude_1/cure0/aaaaaaaa-block-2026-08-2x.md`. Baseline = the champion's own mature reads
  (below). ≈ 2 hours per read, ≈ 16 hours in all; the coordinator surfaces the first submission
  before it starts and reports after each read.

## The baseline — the champion's platform score (the owner's check)

The exact bytes `547fa706…` have these mature reads on the ladder (each ≈160 games):

| when | reads (score) | how taken |
|---|---|---|
| 2026-08-20 night (`local_claude_1/door1-night-2026-08-20.md`) | 23.4 · 23.1 · 23.4 · 23.9 · 21.8 | A arm of five ABAB pairs vs cure C |
| 2026-08-22 block 1 (`door1-vs-old-block1-verdict-2026-08-22.md`) | 23.7 · 21.3 · 23.8 · 21.8 · 21.8 | A arm of five ABAB pairs vs very-old |
| 2026-08-22 block 2 (`door1-vs-old-pooled-verdict-2026-08-22.md`) | five more A reads | same |
| 2026-08-23 (`narrate/aaaaa-block-2026-08-23.md`) | 22.6 | one unpaired read |

Mean of the ten listed ≈ **22.9**, spread ≈ ±1 (σ of a single read ≈ 1.5, `docs/STATE.md` §3).
**Caveat for the owner:** these were interleaved with another arm (ABAB), not a self-replacement
block; if a like-for-like baseline is wanted, an AAAAAAAA of the champion itself costs another
≈16 hours — the owner's call; the default comparison is against these reads.

## Deliverables

`readable/door1-champion.rs` + `readable/door1-champion.round-trip.json` (commit 1);
`readable/door1-champion.rs` edited + `cgauto/submissions/candidate-0-regeneration-fallback.rs`
+ `cgauto/submissions/candidate-0-regeneration-fallback.manifest.json` + `claude_1/cure0/`
(probe arm, panel results, report) (commit 2); the PR; `codex_1/reviews/candidate-0-*.md`; the
block ledger under `local_claude_1/cure0/`.

## Do not touch

`rust/src/bin/yamo_orchard_live.rs` (byte-sacred), the champion file itself (a new file is
generated), `data/raw/games/`, the resident, the cron. No formatter runs over `cgauto/` or
`rust/src/bin/`.

## Arena authority

**Owner-authorized by this charter:** the eight self-replacing submissions of the merged
Candidate 0 arm, after the PR is merged, each surfaced before it starts. Nothing else.

## Not in scope

Any other planner change (Candidate 3 is its own PR); the swap (Candidate 2, parked at the
owner's questions); orchard behaviour.
