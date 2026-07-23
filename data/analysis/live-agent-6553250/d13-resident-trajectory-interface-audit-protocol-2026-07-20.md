# D13 resident trajectory interface audit — development protocol (2026-07-20)

## Purpose

Freeze the smallest learnable interface that can improve the stable resident without discarding
its multi-worker coordination.  This audit measures actual resident decision states; it does not
train, select, promote, submit, or use Arena.

## Data block

- Stable resident versus the frozen six-opponent mechanism panel.
- Seeds 24--39, both seats: 16 × 2 × 6 = 192 complete resident games.
- Exact local referee, 20 independent game workers.
- The V7 process may run in shadow solely because the existing exact harness expects a process
  bot.  Its proposals are descriptive and cannot define the new policy or any gate.
- Emit one row per resident unit decision, plus the paired terminal game row.

These seeds are development data and may have appeared in older project studies.  They are not
a prospective block.

## Proposed residual vocabulary

For each resident-controlled unit decision, the learned policy sees the resident's complete
joint command first.  It chooses either:

1. `KEEP`, preserving that unit's resident command; or
2. one legal spatial action from the existing 13-plane vocabulary.

Move alternatives are restricted to a deterministic point-of-interest set: current position,
both shacks, all plants, all unit positions, cells adjacent to iron, and the resident's current
move target.  Local alternatives are executable `HARVEST`, `CHOP`, `DROP`, `MINE`, `PLANT`, and
`PICK` actions.  Other resident-controlled units keep their proposed commands while one unit is
evaluated; sequential decisions can then revise each unit before the exact joint step.

`KEEP` is encoded as the move-plane action at the active unit's current cell.  This preserves a
compact 13 × 22 × 11 actor head and makes resident behavior an explicit safe default.

## Measurements

Report by role and opponent:

- command verb and `WAIT` distribution;
- exact-command, verb, and target persistence from the previous decision for the same unit;
- multi-worker prevalence and whether paired resident targets coincide;
- point-of-interest move count, executable local-action count, and total residual options;
- direct decodability of resident commands in the proposed spatial vocabulary;
- state/local-signature uniqueness and decision volume;
- worker/economy/action coverage and terminal outcome range.

## Frozen interface rules

- Use the spatial `KEEP + action` residual interface only if at least 95% of resident commands
  are directly decodable and the 95th percentile residual-option count is at most 64.
- Otherwise use a binary `KEEP / generated-alternative` interface and audit the alternative
  generator separately before PPO.
- Include the previous resident command/target in the observation if at least 20% of eligible
  consecutive decisions preserve the same nonempty target.
- Include the other worker's proposed command/target if at least 10% of decisions occur with two
  or more resident workers.
- Do not restrict the residual to local productive actions if fewer than 20% of decisions expose
  at least one such action; retain point-of-interest moves in that case.

The selected interface authorizes only construction and smoke testing of a new resident-aware
environment.  It does not authorize candidate construction or Arena activity.

## Outputs

- games: `d13-resident-trajectory-interface-audit-games-seeds24-39.tsv`;
- decisions: `d13-resident-trajectory-interface-audit-decisions-seeds24-39.tsv`;
- analysis: `d13-resident-trajectory-interface-audit-2026-07-20.json`;
- result: `d13-resident-trajectory-interface-audit-result-2026-07-20.md`.
