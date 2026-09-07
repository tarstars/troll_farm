# Frozen prospective plan — claude_candidate_lumber (growth-aware chop investment)

Frozen 2026-09-07 (`date -u` at freeze: 2026-09-07T00:47Z), BEFORE any panel row exists.

## Parent

`claude_candidate_policy_flat.rs`
sha256 `95ee691ee1b26e074ac90851575a6a56d5b0bec738ff3851cd141585d85c6d23`.
Control arm = that same source re-rooted as `mod baseline`
(`claude_candidate_lumber_control_module.rs`), so the baseline is the unmodified
parent, not a re-derivation.

## Mechanism (concrete, single change)

In `chop_candidates`, after the parent's rate `1000 * wood / (travel + chop +
return + 1)`, price the *same plant chopped after it has grown out*:

* `ripe_score = 1000 * min(4, free_capacity) / (travel + ceil(tree_health(kind,4)
  / chop_power) + return + 1)`;
* `grow_turns = predicted.cooldown + max(0, 4 - predicted.size - 1) *
  effective_cooldown(kind, near_water)` (real referee growth, water boost included);
* if `final_size < 4`, no opponent chopper is predicted on the plant
  (`predicted_opp_chop(view, plant) <= 0`), `ripe_score > score`, and
  `view.turn + grow_turns + ripe_turns <= TOTAL_TURNS`, multiply the premature
  plan's score by `PREMATURE_CHOP_DISCOUNT = 0.25`.

It is a demotion, never a deletion: the candidate stays in the pool, so a unit
with no better job still chops, and a unit with a real alternative takes it.

## Fixtures (fixed before use)

* Real controller `candidate_compare_panel_runner.rs`, real referee via
  `troll_farm_bot` (neighbour crate, read-only).
* 192 pairs: map seeds 9947500..9947507 (8), both seats, 12 opponents.
* Command streams matched to run `20260906T210944Z-3184968-1` (gap):
  `panel_runner 9947500 8 <tsv> <threads>` with `ALLOW_ANY_MAP_SEED=1`.
* Rust 1.90.0 absolute:
  `/data/separate_troll_farm-working/toolchains/rustup/toolchains/1.90.0-x86_64-unknown-linux-gnu/bin/rustc`.
* Run-local cargo target `<run>/target`.

## Acceptance (frozen, no post-treatment subgroup, no fresh holdout)

ACCEPT iff **both** hold on the whole 192-pair panel:

1. candidate whole-panel points `W + 0.5 D` strictly greater than the baseline's;
2. candidate critical issue count is exactly **0** across all 192 candidate games.

Baseline failures are reported whatever they are; they do not relax gate 2.
Reported either way: full W/D/L, points, own score, margin, per-opponent
breakdown, and every diagnostic row.

## Pre-panel checks (must pass first)

* focused embedded tests under Rust 1.90;
* serial 16-stream bench, nothing else running: `over_50ms == 0`;
* exact/readable equality of the shipped compact `_a.min.rs` against the readable
  arm over those 16 streams: `changed_games == 0`;
* compact export `<= 100000` UTF-16 units.

## Deployment limitation stated in advance

This is an offline local-panel measurement against the bundled opponent pool. It
is not ladder evidence and carries no publication authority.
