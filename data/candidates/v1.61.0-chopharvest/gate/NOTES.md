# v1.61.0-chopharvest gate notes

Game 895705613 (first smoke-test game) was played against the debug-probe build
BEFORE the tactics.rs wiring fix (commit 6c04cb1) landed -- its chopper still had
hp=0 live (GE_SPEC bump alone was a no-op; see commit 6c04cb1's message for the
full story). EXCLUDED from all paired-comparison numbers below; superseded by
game 895705828 (same map-independent smoke slot, first POST-fix game).

Paired batch (sequential, same session, both via boss5_games/boss):
- candidate (post-fix): 895705828, 895705861, 895705882, 895705894, 895705909,
  895705918, 895705937, 895705947 (n=8)
- baseline (v1.59.0-ringfix3, unmodified champion): 895705966, 895705985,
  895706006, 895706016, 895706028, 895706044, 895706053, 895706060 (n=8)

Run `gate_analyze.py <label> boss <gid> [<gid> ...]` for the per-game table.
