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

## Log

- 2026-08-29 13:4xZ: born; charter sent to claude_1 pinned to this card's commit. — coordinator
