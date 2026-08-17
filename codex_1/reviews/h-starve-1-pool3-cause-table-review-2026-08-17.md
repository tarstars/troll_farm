# H-STARVE-1 Pool #3 cause-table review — 2026-08-17

Verdict: **REVISION_REQUIRED** (lossy situation-level aggregation).

Pinned artifact: `4514db90aadb0358bd6cdf9dab29f6acef2bfad9`.

## Accepted measurement layer

I independently reran `cause_table.py` and its `--control`; the committed JSON is
byte-reproducible. The parser's verb/count guards, slot-to-unit checks, per-situation
parity/coverage/final-stage gates, and WORLD_INTERACTION observed-firing control are
sound. The per-turn attribution supports the headline that selector-stage withholding
dominates generator-stage absence in this corpus: 2,240 versus 521 WAIT turns.

## Blocker: one plurality token erases mixed causes and conflates status with cause

`classify()` replaces each situation's complete `wait_attribution` distribution with
the most common token. It then overwrites that cause with `NOT_STARVED` whenever fewer
than half of window turns are WAIT. Consequently the handoff's mutually exclusive
“situations” counts are not a faithful cause census:

- OSC-001 is labeled `CANNOT_USE_WORK`, yet it has 39 usable-work WAIT turns:
  16 `NO_GOAL_ASSIGNED` and 23 `GOAL_SPLIT_WRONG`;
- OSC-009 has both 4 `NO_GOAL_ASSIGNED` and 3 `GOAL_SPLIT_WRONG` turns but is counted
  only in the former;
- OSC-031 has 189 `NO_GOAL_ASSIGNED` and 1 `GOAL_SPLIT_WRONG` turn but is counted only
  in the former; and
- OSC-005 is labeled `NOT_STARVED`, erasing its one `NO_GOAL_ASSIGNED` turn from the
  situation incidence table.

The artifact itself proves the correct non-exclusive incidence: `NO_GOAL_ASSIGNED`
occurs in **8** situations, `GOAL_SPLIT_WRONG` in **24**, and `CANNOT_USE_WORK` in
**2** (with 521, 2,240, and 349 WAIT turns respectively). `NOT_STARVED` is a
window-level parked-status predicate, not a stage that produced a WAIT, and must be
reported on a separate axis.

This matters operationally: Pool #5 is “mechanism note per no-goal case.” Using the
six plurality-labeled cases would omit OSC-001 and OSC-005, even though both contain
generator-origin WAITs.

## Required revision

Retain the full per-turn records and add:

1. a non-exclusive situation-incidence table for every cause token (any occurrence,
   situation count, WAIT-turn count, situation IDs);
2. parked/not-starved status as a separate field and summary, never overwriting the
   cause distribution; and
3. an explicit Pool #5 input set containing every situation with at least one
   `NO_GOAL_ASSIGNED` turn.

A `plurality_wait_token` may remain as a descriptive convenience if it is named as
such, but it must not be presented as the exclusive situation cause. No rerun or new
owner decision is needed; this is a lossless re-aggregation of the accepted rows.

No cure code, resident mutation, Arena action, or spec implementation is authorized.
