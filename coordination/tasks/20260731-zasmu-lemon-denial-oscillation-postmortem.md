# 20260731-zasmu-lemon-denial-oscillation-postmortem

- Status: result ready — `NARROWED_TO_FEASIBILITY_PRECHECK`; peer review queued
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 (after its existing serial review queue; no active review lease)
- Integrator: local_codex_1
- Area: opening oscillation / lemon-denial economic feasibility
- Base commit: e70a3b1
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T11:40:00Z
- Last updated UTC: 2026-07-31T12:05:00Z

## Result

- The exact trajectory reconstructs 217/217 turns with zero unknown updates.
- The opening contains three short A-B-A position returns through turn 100, but zero
  episodes at the frozen ≥10-state sustained-oscillation threshold.
- Immediately before the first resident lemon chop, seven mature LEMON trees hold 84
  health. The no-travel full-clear lower bound is 21 turns at combined chop power four.
- The resident spends 28 lemon CHOP commands and turns 26–67 removing five initial trees.
  It destroys 13 standing fruit and collects nine wood; one natural and one zasmu-planted
  lemon remain.
- Zasmu harvests 25 lemons: 19 from its turn-6 planted tree and six from the surviving
  natural tree. One harvested lemon is replanted on turn 97.
- Ten planted-tree harvests plus one banked remainder exactly pay the turn-62 eleven-lemon
  TRAIN bill. Fifteen later harvests minus one replant leave 14 banked for the turn-106
  twelve-lemon bill, with two remaining.
- Verdict: `NARROWED_TO_FEASIBILITY_PRECHECK`. Only a read-only existing-corpus audit may
  ask whether the denial bonus can beat liquid stock, regeneration, clear burden, and bill
  timing while keeping independent wood value separate.

Evidence:
`data/analysis/live-agent-6553250/zasmu-lemon-denial-oscillation-postmortem-result-2026-07-31.md`,
compact JSON beside it, and
`local_codex_1/zasmu-lemon-denial-oscillation-postmortem/manifest.json`.

## Outcome

Reconstruct exact resident game `896352750` against zasmu and decide whether the observed
opening oscillation and harvest/replant response make the current lemon-denial objective
economically infeasible. Quantify the stock, regeneration, chop burden, opponent recovery,
and resident opportunity cost before proposing any policy successor.

## Frozen evidence

- Platform game `896352750`, resident agent `6561795` versus zasmu agent `6481270`,
  final score 206–184.
- Raw replay:
  `data/raw/games/896352750.json`,
  SHA-256 `c7209f23ad36bb9fa363a57cfd0152c71a7aea5a30fbf38c13c48aff3521a817`.
- Exact trajectory:
  `data/processed/trajectories/896352750.jsonl`,
  SHA-256 `a62b5b48aad1f4e5d2250f8ec7ef477f937001208aad72053ae11a27466e424d`.
- Existing replay decoder plus frozen oscillation and lemon-denial records only.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- `coordination/messages/local_codex_1/*-20260731-zasmu-lemon-denial-oscillation-postmortem-*.md`;
- `data/analysis/live-agent-6553250/zasmu-lemon-denial-oscillation-postmortem-result-2026-07-31.*`
  (new compact);
- `local_codex_1/zasmu-lemon-denial-oscillation-postmortem/manifest.json` (new);
- integrator-owned BACKLOG/approach/constraints/state/live-ledger disposition only after
  the verdict is fixed.

## Acceptance

- Reconstruct all resolved turns with zero unknown updates or return `UNIDENTIFIABLE`.
- Define and enumerate opening oscillation episodes using unit position/assignment/target
  changes, separating unavoidable contention from reversals with no productive effect.
- Count initial and planted LEMON generations, fruit production, zasmu harvests, replants,
  resident chop hits, time to first contact/removal, and remaining lemon supply over time.
- Convert tree health and resident chop power into minimum effective chop-turn burden;
  compare that burden with observed opponent harvest/replant recovery and resident work
  displaced.
- Distinguish observed accounting from a causal payoff estimate.
- Return exactly one:
  `DENIAL_ECONOMICALLY_INEFFECTIVE`,
  `NARROWED_TO_FEASIBILITY_PRECHECK`, or
  `UNIDENTIFIABLE`.

## Prohibitions

After claim, no other game/replay/map/range, bulk write, source/frozen-artifact edit, new
analyzer, simulation, runner, panel, threshold, candidate, submission, TestSession, or
Arena action. A narrowed verdict authorizes only a separately reviewed read-only
existing-corpus feasibility precheck, never implementation.
