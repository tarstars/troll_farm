# Card 20260829-nn-bot-way-b-dataset — Phase 2 of the neural-network bot: the dataset, the bench, the clone's trainer

Sub-card of `coordination/tasks/20260829-nn-bot-way-b.md` (the parent holds the design; this card holds
the phase's contract). Born 2026-08-29 13:4xZ. Builder: `claude_1`. Reviewer: `local_claude_1`
(checks the day-2 pilot's labels, accepts the final handoff after `codex_1` reproduces the bench and
the pilot). The clone itself is trained on the host by the coordinator once Phase 0 (the runtime)
has the owner's WiFi word.

**What.** Three deliverables built to the parent card's "Fixed design": (1) **the bench**
`local_claude_1/nn-bot/bench.py` — one seat a Python policy, the other a compiled single-file bot,
over the July Python referee harness, on the 24 owner's-read maps and on 400 seeded maps, with the
per-game outputs the parent lists and the games saved for the owner's turn-by-turn read; proven with
a random-legal policy against the champion's file; (2) **the dataset builder**
`local_claude_1/nn-bot/build_dataset.py` — from the exact reconstruction, one plan row per turn per
seat (label = the talents of the next TRAIN that player actually issues, 0 if none) and one row per
own troll (label = the flat 13×242 index; a MOVE label = the cell actually reached), sharded `.npz`,
seat-swap augmentation, held-out by game; a Python plane builder written from
`local_claude_1/nn-bot/OBS-PLANES.md` with a drift test against `tf_full_obs_from_state` (byte-equal on
1,000 states, run when Phase 1 lands); the full build runs on the host (the raw corpus lives only
there) — the script and its test on the 10-game slice are the deliverable; (3) **the trainer**
`local_claude_1/nn-bot/train_clone.py` — `SpatialActorCritic` with the 144-way plan head as an opt-in
constructor flag, two masked cross-entropies, held-out by game, per-verb accuracy reported and never
used as a gate, the four-key checkpoint format, a minutes-long smoke on the pilot rows.

**Order.** Day 1: the VM runtime (Python 3.11 + CPU PyTorch via `uv`) and the bench with the random
policy. Day 2: the dataset pilot on `local_claude_1/nn-bot/replays-slice-10/`, sent as a handoff (five
sample rows, the label histogram per verb, row counts, bytes per 1,000 rows). Days 3–6: the full
builder, the drift test, the trainer and its smoke. Day 7: the final handoff.

**Done.** The bench runs the random policy against the champion's file on 24/24 maps with every
output the parent lists; the pilot's labels accepted by the coordinator; the builder's test on the
slice passes; the trainer's smoke runs; every number with its command and commit; `codex_1`'s
reproduction matches.

**Dead.** The reconstruction cannot yield a MOVE label (the reached cell) or a plan label for the
top-four games within the budget — then the coordinator narrows the labels to what is exact.

**Budget.** 7 days; two messages (day 2, day 7); stop at the first real blocker and write.

**Rules.** No platform action (the bench is local); no generated maps; the raw corpus stays on the
host (the 10-game slice is the VM's data; the host's network is metered); do not widen the card.
**The VM's disk is at 91 % (1.9 GB free on 2026-08-29 13:5xZ): `df -h` before anything; clean your
own scratch first (`/tmp/claude-1000`); if fewer than 3 GB are free after that, do not install PyTorch
on the VM — deliver the trainer with a test that runs without it (the model built lazily, the data
path tested with NumPy) and the coordinator runs the smoke on the host.** A dying session's last act
is a blocker message, never silence.

## Log

- 2026-08-29 13:4xZ: born; charter sent to claude_1 pinned to this card's commit. — coordinator
- 2026-08-29: day 1 (the bench, random policy vs the champion's file, 24/24), day 2 (the pilot, accepted with three
  rulings), day 3 (the 400 vocabulary; the mask question ruled), day 5 (the Python plane builder, byte-identical to the
  environment on 1,000 states, v144 then v400) — all early. The full build run on the host by the coordinator at 21:4xZ:
  817,811 rows, 14 MB (parent card). — coordinator
- 2026-08-30 00:4xZ: claude_1's wake set is empty (its DEFERRED card discharged itself with the day-5 delivery), so its
  day 6–7 work had no signal — rung with an ack-required handoff: `train_clone.py` with the load-time plane batcher, the
  bench amendments 1–4, the builder's slice test against the amended codec; the day-7 final. — coordinator
- 2026-08-30 01:11Z: claude_1's day-7 final (`agent/claude_1@c7d86c3f`): `nn_runtime.py` (one adapter for planes, masks,
  codec, the TRAIN dry run, the end rule, both seats), `train_clone.py` (six self-tests; the checkpoint loads into the PPO
  trainer; a foreign version refused), the bench amendments 1–4 with tests (random-mask both seats 48/48, illegal 0), the
  builder's codec test PASS on all 10,059 pilot rows; the shard now carries its maps. Merged onto `main` (`12d07ba4`).
- 2026-08-30 02:30Z: codex_1 REPRODUCED all of it (`agent/codex_1@78e524ed`): the codec slice row for row, the bench
  24/24 and 48/48 with 0 differing per-game rows, the trainer's self-test 6/6 and the smoke's losses to four decimals
  (plan 2.9722 → 2.1589, command 3.2499 → 2.2378), the adapter read clean. **The three deliverables are ACCEPTED 03:2xZ.**
  The card's done line now waits only on the clone: the first full run (4 epochs over 817,811 rows) is on the host since
  02:2xZ — epoch 2: command accuracy 0.61, plan 0.68 — then the bench on 24 maps, both seats, both plan decodings, and
  the games for the owner's read. — coordinator
