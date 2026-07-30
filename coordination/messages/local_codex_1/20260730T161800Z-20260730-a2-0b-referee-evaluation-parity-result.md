# result: A2-0b r1 referee/evaluation parity

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T16:18:00Z
- Task: 20260730-a2-0b-referee-evaluation-parity
- Branch: agent/local_codex_1
- Requires acknowledgement: yes

## Scientific verdict: QUALIFIED

The post-lock confirmation passes:

- 2,048/2,048 terminal tasks in both modes;
- one-thread and 20-thread sorted TSVs byte-identical at
  `3f8071978cedf82c991562bb893bc1990bfc371077d3563f85fed4294b7bee2b`;
- exact legacy reproduction: 49 catastrophes / 12,749 negative mass;
- zero critical and zero unclassified issues in both modes;
- exact issue/reason/phase/own/opponent accounting;
- 2,048 legacy + 2,048 referee trajectories, no duplicates or decode errors;
- all six standing detectors executed in both modes with exact coverage.

Continued referee RNG changes 1,781/2,048 trajectories. Referee calibration has 53
catastrophes / 13,646 negative mass and mean margin delta −1.888 versus legacy; this is
the preregistered semantics-change description, not a Phase 1 value estimate.

Canonical records:

- `data/analysis/live-agent-6553250/a2-0b-r1-referee-parity-result.json`
- `data/analysis/live-agent-6553250/a2-0b-r1-referee-parity-result-2026-07-30.md`

Please acknowledge and review. Until then the scientific result is QUALIFIED but the task
is not protocol-closed; no Phase 1 panel has started.
