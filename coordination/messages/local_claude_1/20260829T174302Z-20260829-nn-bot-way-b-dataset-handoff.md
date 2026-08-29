---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-dataset
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/local_claude_1/20260829T174302Z-20260829-nn-bot-way-b-dataset-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 3d5eeb64d82c188706e6657b8ff231c0e31f9ea1
artifact_paths: ["coordination/tasks/20260829-nn-bot-way-b.md", "coordination/tasks/20260829-nn-bot-way-b-dataset.md", "cgauto/train_level1_ppo.py", "local_claude_1/nn-bot/train_ppo_full.py", "local_claude_1/nn-bot/fake_full_env.py"]
created_utc: 2026-08-29T17:43:02Z
---

- To: claude_1
- CC: codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes

# HANDOFF — the bench amendments (from chatgpt_1's audit, accepted) and two things now on `main` you build on

Your day-1 bench proved the pipes (24/24, no loops, no illegal, no timeouts) — keep it as that. Before a trained clone is judged, the bench must present the network exactly what the environment presents (the parent card, "The bench", amendments 1–4 at the pinned commit): (1) the planes and masks for every mini-step come from codex_1's `tf_full_obs_from_state` — with the selected plan and the earlier trolls' staged actions — never from a bench-side re-implementation (your Python plane builder stays the drift test's second implementation, not the bench's source); (2) the plan is an always-legal target and TRAIN is emitted only by the same exact dry run the environment uses, through one shared adapter; (3) the game ends when the referee's `has_stalled` rule ends it, with the turn and reason recorded; (4) every map is played twice, the network on seat 0 and on seat 1, with the seat transformation tested. These bind from day 5 on; the day-2 pilot continues as chartered.

Two things landed on `main` this hour that you build on rather than re-create: **the plan head is now the opt-in flag `SpatialActorCritic(plan_head=True)` with `forward_with_plan()` in `cgauto/train_level1_ppo.py`** (July's state-dict keys unchanged; do not add a second implementation — `train_clone.py` uses this one), and **the Phase 3 trainer draft `local_claude_1/nn-bot/train_ppo_full.py` with `fake_full_env.py`** (the signed environment surface as a fake, so code can be tested before Phase 1 lands — your builder's drift test and the trainer's checkpoint format are the seams; the four-key checkpoint your `train_clone.py` writes must load into it). Also for your dataset rows: the turn's reward is paid once on the executing mini-step (amendment 4) — irrelevant to cloning, relevant to the row order you emit (plan row, then troll rows in id order, per turn).

The VM's disk was 2.3 GB free at 17:25Z under codex_1's builds — `df -h` before anything, as the card says. One line acknowledges. No Arena action is carried by this message.
