# RESULT — DispatchBot runs the whole game, expands past two workers, loses the panel

**Verdict: PARK.** The frozen rule (positive whole-panel W+0.5D **and** zero
candidate issues) fails on both counts: **77.5 vs 170.0** points and **26,313**
candidate issues. No tuning was done after the panel.

**Architecture (authoritative, not a wrapper).** `claude_candidate_dispatch.py`
splices a self-contained `dispatch` module beside the parent's `SearchBot` and
re-points `candidate::bot::moisan::SecureOrchardBot` at `DispatchBot`. It never
constructs the parent policy and never reads a parent command string; it reuses
only `game::{types,rules,nav,protocol}` and `flat`. Each turn it prices complete
finite jobs (Chop/Harvest/Mine/Bank/Plant) per worker — carry cap truncates wood,
`harvest_power` truncates fruit — assigns one job per worker with exclusive
target claims from one shared bank ledger, and emits jointly: one action per
worker, <=1 TRAIN, bill reserved against same-turn PICK, landing-cell moves,
endgame banking. Orchard branch untouched.

**Changed files (all new; sha256).** `claude_candidate_dispatch.py` 57362ad8,
`_core.rs` c6adaf1e, `test_claude_candidate_dispatch.rs` 44c368da,
`_a.rs` 858ca3de (303,335 UTF-16), `_a_module.rs` dc16abb8,
`_a_tests.rs` cdf45071, `_control_module.rs` 526cd9cc. Parent 95ee691e,
`bot.rs` 44e3daca, `submission.rs` 7f61a6cd **unchanged**.

**Tests (rustc 1.90.0 absolute path): 18 run, 18 pass**, `--test-threads=1`.
Nine new executed referee fixtures: realistic opening; **full bill acquired by
mining + foraging then paid twice** (roster 1->2->3, hires t115/t172, net banked
**22** points, no pre-granted funding); ore-free map **abandons** the hire;
banked-ore ore-free map pays it; reserved bill never PICKed on a TRAIN turn;
capacity caps a size-4 tree at 1 wood; blocked-door banking; endgame banking;
`ripen_turns` equals the referee's growth ticks (Lemon 33/13, Banana 25).

**Rule found:** `parse_player` charges the **full** bill incl. IRON before
`apply_train`'s no-iron exemption, so an ore-free map cannot hire past banked ore.

**Panel (192 pairs, 9947500..9947507, 12 opponents, both seats).** Baseline
167/6/19 = 170.0, own 231.35; candidate **77/1/114 = 77.5**, own 111.66, margin
-30.37, delta **-92.5**. Loses every opponent (worst resident -10, compact_gold
-4). Baseline matched the authoritative 20260906T210944Z-3184968-1 controls on
all 24 outcome columns (only `divergent_command`, a diagnostic, differs).
**Investment activated**: 186/192 games hire, mean 3.71 workers vs 2.00. Wood
collapsed 42.4 -> 23.3. **All 26,313 issues are non-critical `move_blocked`;
critical 0.**

**Limitations.** No compact export, no 16-stream equality, no timing, no
platform action.

**Next action.** Path on walkable-minus-own-units (BFS excluding team-mates)
instead of ignoring occupancy; reproducer: any panel game's `move_blocked` list.
Evidence: `panel.tsv`, `summary.txt`, `issue-reasons.txt`, `tests-full.log`,
`hashes.txt`, `PLAN.md`.
