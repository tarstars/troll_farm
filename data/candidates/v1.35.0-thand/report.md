# Candidate v1.35.0-thand — Builder Report

(Persisted by the orchestrator: the builder subagent's Write access to report files was
policy-blocked; content returned in its final message and saved here verbatim in substance.)

**Task:** T-hand — Tempo + funded third hand. Salvage from the parked Scale/Hoard arc (per the
Amendment in docs/superpowers/specs/2026-07-07-last-mile-and-basin-jump-design.md): revive the
dormant GE_MAX_TROLLS feeder slot (2→3) under the live Tempo meta itself, funded by extending the
battle-tested elevated funding stack (iron 65/64, deficit-fruit 63) from Scale-only to ANY pending
ladder hand, including Tempo's. Builder role only; champion-equality gate explicitly waived
(candidate changes Tempo behavior by design). Base tree: 5db7bc9.

## What changed
- TDD tests first, both confirmed FAILING pre-fix:
  - rust/tests/phase_hoard.rs `tempo_ladder_funding_treks_to_deficit_fruit` (Tempo mirror of the
    hoard deficit-trek test; failed with `MOVE 0 3 2` — nearer non-funding banana won).
  - rust/tests/tactics_scale.rs `tempo_wants_third_hand` (3 farm bananas, starter+chopper, t=50;
    failed with want_feeder=false).
- rust/src/botmain.rs: GE_MAX_TROLLS 2→3; VERSION → "1.35.0-thand"; GE_FEEDER_T 60→45
  (ANOMALY, resolved per brief contingency: 60 was dead-constant drift from commit 3e8b2b52 in
  the v1.28.x era, inert while GE_MAX_TROLLS=2 made want_feeder unreachable; 45 = the original
  value, now live and boss/arena-unvalidated on its own — first knob to reconsider if hand
  timing looks off). GE_FEEDER_FARM=3, GE_FEEDER_SPEC=(1,1,1,0) confirmed as assumed.
- rust/src/botmain/planner.rs: `scale_funding = plan.phase != Phase::Tempo && plan.want_feeder`
  → `ladder_funding = plan.want_feeder` (all 3 use sites: iron Mine 65, iron MoveTo 64,
  deficit-fruit 63). Generic wallet band 62 remains Hoard-only (verified: its gate reads
  plan.phase directly). tactics.rs: comment-only updates.
- Diffstat: botmain.rs 6±, planner.rs 29±, tactics.rs 9± (comments), phase_hoard.rs +27,
  tactics_scale.rs +26.

## Gate results
1. cargo build --release: clean (pre-existing warnings only).
2. cargo test --release: 24 suites, 48 tests, 0 FAILED (+2 new tests, green post-fix).
3. Self-determinism: EQUAL 16 games (8 seeds × 2 seats).
4. bundle.py: 68,010 chars → rustc (dot-free copy): exit 0. VERSION/GE_MAX_TROLLS=3/
   GE_FEEDER_T=45/ladder_funding(5 hits) confirmed in bundle.
5. Bundle-inlining sanity: bundled bin vs cargo bot EQUAL 16 games.
6. minify: 68,010 → 41,951 B (58% under cap); rustc on minified copy: exit 0; minified bin vs
   cargo bot EQUAL 16 games.
7. Champion-equality: N/A (waived by design).

## Artifacts
- cgauto/submissions/v1.35.0-thand.rs (69,353 B) and .min.rs (41,951 B); duplicated to
  data/candidates/v1.35.0-thand/ (cmp-identical).
- DEBUG probe for the gatekeeper: data/candidates/v1.35.0-thand/v1.35.0-thand.debug-probe.min.rs
  (41,950 B; DEBUG=true ×1; GE_META=Tempo; rustc exit 0; 2-seed local smoke EQUAL, no crash).

## Next steps (gatekeeper)
collect_debug_games.py <probe> boss 8 + field (incl. denial-style mikdiet 6480914 / plcc
6480966); read @TFFARM: does n reach 3 (t≥45, farm≥3, wallet-dependent), does the hand PLANT,
does wood improve vs the ~50-wood Tempo era norm; ramp.py --last 8 for wood/delta; no crater.
Champion comparison falls on gatekeeper/arena (builder equality was waived).
