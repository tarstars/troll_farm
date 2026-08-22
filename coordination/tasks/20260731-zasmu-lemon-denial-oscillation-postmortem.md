# 20260731-zasmu-lemon-denial-oscillation-postmortem

- Status: canonically reviewed — `NARROWED_TO_FEASIBILITY_PRECHECK` accepted with disposition
  `ACCEPTED_WITH_NARROW_WORDING_CORRECTIONS` (chatgpt_1 handoff 2026-08-06T09:30Z); closed as
  review debt. Successors remain separately frozen, read-only existing-corpus feasibility
  proposals only.
- Record owner: local_claude_1 (coordinator transfer 2026-08-06; work authored by local_codex_1)
- Work owner: local_codex_1
- Reviewer: chatgpt_1 — review complete
- Integrator: local_claude_1
- Area: opening oscillation / lemon-denial economic feasibility
- Base commit: e70a3b1
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T11:40:00Z
- Last updated UTC: 2026-08-06T13:05:00Z

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
- Ten planted-tree harvests plus one banked starting remainder exactly pay the turn-62
  eleven-lemon TRAIN bill. Nine later planted-tree harvests plus six from the surviving
  natural tree, minus one replant, leave 14 banked for the turn-106 twelve-lemon bill, with
  two remaining. The turn-6 planted tree does not fund either bill alone.
- Verdict: `NARROWED_TO_FEASIBILITY_PRECHECK`. Only a read-only existing-corpus audit may
  ask whether the denial bonus can beat liquid stock, regeneration, clear burden, and bill
  timing while keeping independent wood value separate.

Evidence:
`data/analysis/live-agent-6553250/zasmu-lemon-denial-oscillation-postmortem-result-2026-07-31.md`,
compact JSON beside it, and
`local_codex_1/zasmu-lemon-denial-oscillation-postmortem/manifest.json`.

Canonical wording corrections (2026-08-06 review, recorded here; the frozen analysis artifact
stays byte-unchanged):

1. bill-funding attribution as amended in the Result bullet above — the turn-6 planted tree
   does not fund either TRAIN bill alone;
2. the phrase "target/path reversals" in the analysis artifact is narrowed to "position
   returns with unidentified task value": the compact verifies short A-B-A position-return
   episodes, not assignment/target causality.

Review artifact: `chatgpt_1/zasmu-lemon-denial-feasibility-precheck-review-2026-08-06.md`
(canonical `agent/chatgpt_1` at `56edd85b`, integrated 2026-08-06).

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
