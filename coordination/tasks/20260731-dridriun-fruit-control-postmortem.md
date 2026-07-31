# 20260731-dridriun-fruit-control-postmortem

- Status: claimed — exact one-game scope audit active
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 (after B3.7/N5/N6; no active review lease)
- Integrator: local_codex_1
- Area: owner-observed fruit control / B3.7, B3.10, H3 boundary
- Base commit: c2df65565e49316b187a7d37babf69e09a2427a0
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T11:00:00Z
- Last updated UTC: 2026-07-31T11:00:00Z

## Outcome

Reconstruct the three owner-observed errors in exact resident game `896352129` against
Dridriun, then decide whether they identify a distinct bounded fruit-control precheck or
are already consumed by the failed broad harvest/opponent-crop interventions.

The three hypotheses are:

1. deny a recurring enemy-door apple before the opponent repeatedly harvests it;
2. avoid creating apple fruit where opponent harvesting capacity is not dominated;
3. when we control a ripe own-door apple, harvest before converting it to wood.

## Frozen evidence

- Platform game `896352129`, resident agent `6561795` versus Dridriun agent `6480943`,
  final score 252–276.
- Raw replay:
  `/home/tarstars/prj/troll_farm/data/raw/games/896352129.json`,
  SHA-256 `eee9f3485204dea948efa36d39b2fb7783752cec419e931bc08577f943adb1c0`.
- Exact trajectory:
  `/home/tarstars/prj/troll_farm/data/processed/trajectories/896352129.jsonl`,
  SHA-256 `b4f42a5f46791de61aaa5a91e4c19f35aba3b711e9399666565fdb61a3983593`.
- Existing exact replay decoder plus frozen H3/H3a, D173a/b, B3.7, B3.10, and Phase-21
  results/constraints.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- `coordination/messages/local_codex_1/*-20260731-dridriun-fruit-control-postmortem-*.md`;
- `data/analysis/live-agent-6553250/dridriun-fruit-control-postmortem-result-2026-07-31.*`
  (new compact);
- `local_codex_1/dridriun-fruit-control-postmortem/manifest.json` (new);
- integrator-owned BACKLOG/approach/constraints/state/live-ledger disposition only after
  the audit verdict is fixed.

## Acceptance

- Identify exact turns, cells, units, harvest/chop capability, camp distances, fruit,
  health, and generation fate for all three observations.
- Quantify opponent harvests by enemy-door apple generation and delay to resident contact
  and removal.
- Quantify resident-created own-door apple cycles, ripe turns chopped without harvest,
  and actual versus merely reachable opponent capture.
- Separate replay facts, direct accounting ceilings, and policy counterfactuals.
- Reconcile with the failed unconditional Phase-21 dual value, D173a/b displacement,
  B3.7 conversion-by-design, and B3.10 direct-stock closure.
- Return exactly one:
  `COVERED_NO_NEW_INTERVENTION`,
  `NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`, or
  `UNIDENTIFIABLE`.

## Prohibitions

No other game/replay/map/range, bulk write, source/frozen-artifact edit, new analyzer,
simulation, runner, panel, threshold, capability change, candidate, submission,
TestSession, or Arena action. A distinct verdict authorizes only a separately reviewed
precheck proposal, never implementation.
