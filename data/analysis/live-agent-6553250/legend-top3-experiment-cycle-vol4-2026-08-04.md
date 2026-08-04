# Legend score-25.40 experiment cycle — volume 4 (opened 2026-08-04)

Objective and live state: `docs/STATE.md`. Closed branches: `docs/CONSTRAINTS.md` — check before
proposing. Volume 3 (`legend-top3-experiment-cycle-vol3-2026-07-30.md`) is frozen after the
owner-directed round-36 simplified E7a deployment.

Per-experiment obligations: one entry here; a CONSTRAINTS bullet for anything closed; a STATE.md
§4 update. The first session ending with this file over 100 KB freezes it and opens volume 5.

<!-- entries below -->

## 2026-08-04 — round-36 settled standing

The owner requested a settled position/game-count read for exact round-36 agent `6594200`,
submission `41090606`. At 16:25:25Z both platform score endpoints agree: **22.81, rank 32/137**,
with **160/160 games complete** and zero pending. The submission-scoped audit records 93W/2T/65L,
mean margin +8.925, 21 catastrophes, negative-margin mass 6,381, zero runtime signals, and clean
identity. Exact checkpoint SHA is `0f476514...`.

This read is recorded without Arena mutation. Round 36 remains active.

## 2026-08-04 — round-36 full replay corpus exported

The 160 settled games for agent `6594200`, submission `41090606`, are now available to agents
without platform access as a sanitized full-frame Git LFS corpus under
`data/shared-lfs/r36-agent-6594200/`. All 160 public replay fetches succeeded, with 86,940 frames
and exact game-ID equality to the settled checkpoint. The 40,006,551-byte staging set compresses
to 5,774,722 bytes at SHA `59f6283b...`; personal/session fields are removed and player names are
replaced by positional placeholders.

Payload commit `936cf577` uploaded successfully. A fresh smudge-disabled clone exposed the exact
LFS pointer and then reproduced the full payload and hash through an exact-path selective pull.
This was read-only with respect to both Arena and the collector-owned `data/raw/games/` cache.
