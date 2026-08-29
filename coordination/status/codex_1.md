# codex_1 Status

- Updated UTC: 2026-08-29T22:03:52Z
- State: Phase 1 corrected gate complete and peer-reproduced; corrected delivery being published for coordinator acceptance
- Role: contributor / reviewer
- Current task: 20260829-nn-bot-way-b-env — full-game neural-policy environment
- Branch: agent/codex_1
- Head: v400-2026-08-29 full-game environment with independently invoked transition and terminal parity checks, strict staged-prefix validation, both-seat codec coverage, and real command-rejection accounting
- Write set: `local_claude_1/nn-bot/OBS-PLANES.md`; `local_claude_1/nn-bot/ENV-API.md`; after signature `rust/src/rl_full.rs`, `rust/src/lib.rs`, `rust/Cargo.toml`/`Cargo.lock` for JSON dependencies, `cgauto/rl_full_env.py`, task tests and `codex_1/results/**`; own status/messages
- Last concrete progress UTC: 2026-08-29T22:03:52Z
- Evidence: corrected gate from `6b3ed3c4` is separately invoked transition parity 1,000/1,000, terminal parity 1,000/1,000, illegal commands 0, seeds 320000–320999, 1,000 unique action/state hashes, portable digest `8ae5a0098ff3…`; claude_1 independently reproduced the v400 digest and 1,000/1,000 plane drift; native Python 7/7 pass in 189.07 s
- Running job: none
- Latest verified result: raw gate SHA256 `5e1a27ab1d73654c02995eb336b483dbd679039757b7b7ffc3f03d9f6ce7b810`; timing-independent SHA256 `8ae5a0098ff3bf27ecc8de4d3dad8bd3aaa5070bfe37273b366706d3412618de`
- Next checkpoint: coordinator acceptance of the corrected delivery; no local environment work remains
- Signed-plane audit: corrected planes 38–39 so both the shack and its adjacent walkable door cells are distance zero; focused Rust 5/5 and Python 2/2 tests pass after the correction
- Signed-mask/input audit: non-MOVE verbs now honor earlier-troll end-cell reservations and MOVE/current is conflict fallback only when needed; map JSON requires matching declared shacks, valid terrain symbols, and valid distinct natural trees; focused Rust 6/6 passes
- Blocker requiring signature: cleared; `serde` with derive and `serde_json` are approved with the matching lockfile edit
- Validation limitation: this VM's whole-crate Cargo entry point still lacks historical compile-time input `d105a-q6-expert-population.tsv` (known since task X1); no replacement was made. A focused temporary crate compiles and tests `state.rs`, `engine.rs`, and `rl_full.rs` directly.
- Completed replacement card: Candidate 0 independently reproduced BLOCK accepted; task closed with no successor under that charter
- Completed replacement card: Candidate 3 G-0 r6 reviewed once; `ACCEPT-WITH-EDIT`; Claude applied the exact C5 edit and owns the bounded build
- DEFERRED replacement card: panel-digest/analyzer repair only under a separately published charter and write set; no current task authorizes it
- DEFERRED replacement card: NARRATE v3 independent review only after a mature live corpus, exact identity pin, and mandatory forbidden-key sweep are published
- DEFERRED replacement card: G-2 first-pass and champion second-pass fresh-archive execution review only after DEFINITIONS_ACCEPTED and a valid claude_1 handoff naming its canonical full commit and artifact paths
- DEFERRED replacement card: G-1 fresh-archive execution review after the complete canonical handoff specified in `20260825T142509Z`
- Completed replacement card: Track T-1 storage blocker cleared by coordinator policy `20260826T141035Z`; first table computed on the hash-pinned local copy
- Completed replacement card: Track F-1 stops under its dead condition; 98 recorded games exist, the processed corpus covers the first four, and attribution remains impossible without per-turn replay data
- Completed replacement card: P4b pipeline integration after the coordinator assigned it and Claude transferred the two destination files
- Completed replacement card: D-2 accepted by the one budgeted re-review; 10 pipeline tests and 11 private tests pass, Candidate 3 v6 is READY with 0 decode errors, and Candidate 2 v5 reproduces
- Completed replacement card: Candidate 2 G-0 reviewed at `agent/claude_1@6eb89209`; `DESIGN_ACCEPTED` with one non-gating proof-wording correction
- Completed replacement card: D3-G1 repaired producer reproduced byte-for-byte; coordinator's conditional acceptance is satisfied
- Completed replacement card: fixture drift 0-1 closed; 34 old-bot fixtures retired as gates
- Completed replacement card: Candidate 3b one-shot reproduction confirms the closed FAIL; no retune and no ladder slot
- DEFERRED replacement card: fresh-fixture dataset 0-3 starts only after T-1's first two tables and one day of champion version-6 ladder telemetry; unblock when the board or coordinator records both facts
- Completed replacement card: cured-dancing-troll bot B identity check accepted at 240/240 command streams after complete `MSG` removal; annotations await hash-tagged collected games for both arms
- Completed replacement card: bot B identity delivery re-pinned after rebase at reachable commit `589c4614`; the 240/240 result is unchanged
- DEFERRED replacement card: fresh-fixture dataset 0-3 now follows the 1.5-day ladder-measurement collection window and a successful collected payload decode; bot B games count when tagged by hash
- DEFERRED replacement card: collection and decode gates are met; input access waits for the coordinator's <=10 MB hash-manifested slice or a passing mandatory storage preflight
- Completed replacement card: P4b farm dialect corrected from the already-taken v7 token to v8; exact narrate8 controls and 12 gate tests pass
- Completed replacement card: banana-farm F-2 reproduction confirms the validity BLOCK; farm-off 52, instrument 96, candidate 92, containment 34/34; no Arena mutation
- Completed replacement card: `coordination/tasks/20260825-quarantine-on-main.md` G-1 implementation and live dry runs
- Blockers: exact referee-success ownership, near-shack distance, and goal-based idle/contention are absent from the turn export and are reported unavailable rather than inferred as fact
- Blocker: the floor generator cannot reproduce its committed `rustfmt_check` field in this environment; the task's dead condition forbids continuing to bed or smoke
- Arena controller: no
## 2026-08-27 06:18Z — active wake

- `20260827-goal-keeping-ladder-cost`: started; deterministic replay slice is 208 champion games
  versus 4 keep-rule games. Building the chartered one-script comparison, with the dead condition
  active if that sample cannot separate behaviour.
- `20260826-banana-farm-candidate`: accepted the owner-directed parity check; blocked until
  `claude_1` publishes the compacted farm instrument and round-trip report.

## 2026-08-27 06:25Z — deliveries ready

- `20260826-banana-farm-candidate`: ACCEPT packaging parity; compacted watching submission and
  panel arm are identical after stripping diagnostics on 240/240 games. This does not change the
  standing validity failure.
- `20260827-goal-keeping-ladder-cost`: STOP under dead condition. The supplied slice has 208
  champion games but only 4 keep-rule games, all bad losses; version-6 telemetry lacks opponent
  invalidation cause, contested-target outcomes, and score composition. Hypothesis under-determined.

## 2026-08-27 06:38Z — review accepted; idle

- `20260827-goal-keeping-ladder-cost`: the single chartered review ACCEPTED the stop. Its added
  outcome split preserves the reversal-rate direction but not causality. No replacement card:
  more ladder play or telemetry requires a new owner ruling.
