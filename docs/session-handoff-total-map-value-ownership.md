# Session Handoff: Total Map Value Ownership

## Why This Exists

The user plans to reset the session so the Superpowers skill is active. This note captures the
feature discussion and the files created so the next session can continue without reading the
chat transcript.

## Current Feature Thread

The current feature idea is **Total Map Value Ownership**:

- Optimize for our captured share of total remaining map value, not raw production.
- Avoid the recurring "pie logic" failure where we create/preserve extra value and the opponent
  converts more of it than we do.
- Treat the pressure-aware farm governor as the first concrete application, not the whole
  strategy.

Core invariant:

> Choose actions that increase our expected captured share of total remaining map value, after
> accounting for travel, timing, banking, worker capacity, and opponent capture risk.

## Files Created This Session

- `docs/map-value-ownership.md`
  - Short feature request and overview.
- `docs/pressure-aware-farm.md`
  - First concrete application: dynamic farm size/liquidation based on ownership pressure.
- `docs/superpowers/specs/2026-07-09-total-map-value-ownership-design.md`
  - Canonical Superpowers design spec.
- `docs/superpowers/plans/2026-07-09-total-map-value-ownership.md`
  - Diagnostic-only Superpowers plan for the next step.
- `docs/session-handoff-total-map-value-ownership.md`
  - This handoff.

Absolute plan path:

`/home/tarstars/prj/troll_farm/docs/superpowers/plans/2026-07-09-total-map-value-ownership.md`

Absolute spec path:

`/home/tarstars/prj/troll_farm/docs/superpowers/specs/2026-07-09-total-map-value-ownership-design.md`

## Important Scope Decision

Do **not** implement bot behavior yet.

The next step is diagnostic-only:

1. Build/read `cgauto/map_value_ownership.py`.
2. Run it on existing DEBUG/raw games, prioritizing:
   - `data/boss5_games/6480966` (`plcc`);
   - `data/boss5_games/6480914` (`mikdiet`);
   - `data/boss5_games/6480824` (`kurigen`);
   - `data/boss5_games/boss` as supporting context.
3. Write `data/analysis/map-value-ownership/report.md`.
4. End with one verdict:
   - `PROCEED: build v1.53.0-pressurefarm`;
   - `MORE DATA: collect <opponents/games>`;
   - `STOP: no repeatable ownership leak`.

Only `PROCEED` should create a behavior implementation plan.

## Current Project Context Worth Preserving

- The long-running goal remains Gold rank `<=99` verified twice.
- Current champion default in `cgauto/api_submit.py` was previously documented as
  `cgauto/submissions/v1.43.0-yield.min.rs`.
- Recent live/revert baseline was `v1.46.0-splitclaims`, after rejecting
  `v1.52.0-lateseedhome`.
- Many files in the worktree are dirty/untracked from prior work. Do not revert unrelated
  changes.
- The docs added in this session are new/untracked unless committed later.

## Restart Prompt Suggestion

After reset, start with:

> Use Superpowers. Read
> `docs/superpowers/specs/2026-07-09-total-map-value-ownership-design.md` and execute
> `docs/superpowers/plans/2026-07-09-total-map-value-ownership.md` through the diagnostic
> report only. Do not change bot behavior yet.
