# Training can follow same-turn shack egress

The comment at `next_bot/economy.rs` claiming TRAIN checks shack occupancy before MOVE is wrong.
The archived V439 game 901539233 successfully issues `TRAIN 1 1 0 2; MOVE 0 1 3` on turn 1 with
the starter initially at its shack. Its second worker exists in the following state.

The locally retained original Java source at
`/data/strong-bot-sources/eulerscheZahl-Troll-Farm/src/main/java/engine/task/TrainTask.java`
checks affordability in parsing but shack occupancy only in `apply`. TRAIN has priority 6;
`MoveTask.java` has priority 1. The neighbor's read-only
`rust/src/game/a2_referee_parity.rs` likewise resolves moves before applying TRAIN.

An executable probe on official seed 2609051701 confirms the distinction:

- TRAIN alone: one worker, unchanged inventory, `train_shack_blocked`.
- TRAIN plus legal MOVE out: two workers, no issue, inventory changes from `[2,2,7,3,5,0]`
  to `[0,0,6,3,0,0]`, exactly the training bill.

Probe source and executable are in
`/data/separate_troll_farm-working/scarce-denial/2026-09-05/train_egress_probe.rs` and
`train-egress-probe`. They link the existing frozen referee library without editing the neighbor.

The current controller conservatively waits a turn. Correcting the false comment is not itself
a gameplay fix. A subsequent implementation needs to verify the final resolved MOVE actually
clears the shack, account for enemy occupancy, retain the shared PICK/TRAIN stock ledger and
handle a blocked egress without spending imaginary stock. Keep this fix separate from the frozen
scarce-denial comparison so its causal effect is not bundled into that experiment.
