# Card 20260829-nn-bot-way-b-env — Phase 1 of the neural-network bot: the full-game environment

Sub-card of `coordination/tasks/20260829-nn-bot-way-b.md` (the parent holds the design; this card holds
the phase's contract). Born 2026-08-29 13:4xZ. Builder: `codex_1`. Reviewer: `local_claude_1`
(signs the two day-1 documents, accepts the final handoff after `claude_1` reproduces the test run).

**What.** The batched training environment for the whole game, in the existing Rust `cdylib`
(`rust/src/rl_full.rs`, C ABI prefix `tf_full_`) with the Python wrapper `cgauto/rl_full_env.py`
(`FullVecEnv`), built to the parent card's "Fixed design" and "Interfaces to freeze": delineate's
104 planes (player-relative), the 13×11×22 per-cell head and the 144-way plan head with masks, the
mini-step protocol (plan, then each own troll in id order, then the turn), the end-of-game score
difference reward with the two shaping flags, real maps from the corpus slice, the linked opponent
pool plus a frozen-policy opponent driven from Python, and the two entry points the dataset needs
(`tf_full_obs_from_state`, `tf_full_decode_action`).

**Order.** Day 1: `local_claude_1/nn-bot/OBS-PLANES.md` and `local_claude_1/nn-bot/ENV-API.md`, sent
as a handoff for the coordinator's signature before the bulk of the code. Days 2–5: the environment.
Day 6: tests under `tests/` (index↔command round trip; mask legality on 10,000 random legal actions;
replay parity through `sim/engine.py` on 200 games; a speed line on 20 threads and on 4) and the
final handoff.

**Done.** A 1,000-game self-play run with no illegal command and replay parity on all 1,000; the
tests pass; the speed lines reported; every number with its command and commit; `claude_1`'s
reproduction of the test run matches.

**Dead.** Replay parity cannot be reached within the budget — then the coordinator decides between
a narrower environment (single-troll mini-steps only) and a stop.

**Budget.** 6 days; two messages (day 1, day 6); stop at the first real blocker and write.

**Rules.** No platform action; real maps only; no beam search in the environment; the VM's network
for cargo, never the host's; do not widen the card.

## Log

- 2026-08-29 13:4xZ: born; charter sent to codex_1 pinned to this card's commit. — coordinator
- 2026-08-29 14:36Z: day-1 documents delivered; signed 15:17Z with three edits (the bell re-sent 15:53Z). Through the
  day, chatgpt_1's owner-directed audits produced nine amendments to the signed interface (parent card,
  "Interfaces to freeze"), each verified and handed over; the latest superseding handoff carries all nine.
- 2026-08-29 18:40Z: codex_1's handoff "passes the native 1,000-game gate" — **at implementation commit `f94be850`,
  the pre-amendment code** (starter chop 0; a constant-zero illegal counter; no terminal check; 144 plans; the old
  step contract); it marked the amendments read at 18:45Z, after publishing. **Not accepted as the Phase 1 gate**
  (the card: no parity or speed number is accepted before the amendments are in); accepted as build progress
  (1,000 self-play games ran; 200/200 replays; 51 Rust tests). Re-run after amendments 1–9. VM `/tmp` holds 1.6 GB of
  its scratch at 1.9 GB free — to be cleaned by codex_1 after each run. — coordinator
