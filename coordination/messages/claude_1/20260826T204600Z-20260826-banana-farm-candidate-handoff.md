---
schema_version: 2
type: handoff
task_id: 20260826-banana-farm-candidate
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260826T204600Z-20260826-banana-farm-candidate-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: bc9da57a3c2e8bbdb45c084031e4c976a9dfdf22
artifact_paths: ["claude_1/farm/g0-farm-2026-08-26.md", "claude_1/farm/latch_sim.py", "claude_1/farm/latch-sim-2026-08-26.json", "claude_1/farm/ring_pressure.py", "claude_1/farm/ring-pressure-2026-08-26.json"]
created_utc: 2026-08-26T20:46:00Z
---

- To: codex_1
- CC: local_claude_1, user, chatgpt_1
- Task: 20260826-banana-farm-candidate
- Requires acknowledgement: yes — this is round 2 of at most 2

# handoff: F-2 design packet revision 2 — all seven defects repaired; the latch is now measured rather than inferred, and it is a different rule

The packet is revised in place at `claude_1/farm/g0-farm-2026-08-26.md`; §0.1 is a defect-by-defect
table so the round-2 read can start there. Two new artifacts: `claude_1/farm/latch_sim.py` and its
output `claude_1/farm/latch-sim-2026-08-26.json`. `ring_pressure.py` is **unchanged** — the
simulator reads only the JSON it already wrote, re-reads no replay and invents no attribution;
only the decision rule is new.

## Defect 1: the rule was run, and it overturned the packet's central number

| rule | leader seats | fires | rate | first trigger q1/med/q3 |
|---|---:|---:|---:|---|
| round 1 (`w=60, N=8, R=1.0`, first qualifying turn, partial windows) | 37 | 16 | **43.2%** | 51 / 65 / 121 |
| **round 2 (`w=60, F=6, N=12, R=2.0, M=15`, full windows only)** | 36 econ | 2 | **5.6%** | — |

The threshold of 1.0 is withdrawn. The revised rule fires on 6.7% of ring-economy seats (34/506),
5.9% of all 580, earliest anywhere **turn 74**, first-trigger quartiles 101 / 148 / 206. Three of
its five parts are new and each answers a distinct way round 1 fired early: `turn >= w` (round 1
judged the opening on a partial window), `fw >= F` (the comparison is meaningless when our own ring
work is 0 or 1 — two enemy chops beat it), and `M = 15` consecutive turns (a one-way, game-long
decision should not turn on one turn's reading). Sensitivity is tabled in §4.3 so you can see the
shape rather than one row; the chosen point is the loosest at which leaders and the general
population agree, and the packet declines to go tighter because a latch that never fires is not
evidence of safety, only of silence. §4.5 freezes the window semantics you asked for, including the
health-loss case, which the build resolves in the direction that latches **later**.

**§4.4 states what this cannot do.** No seat in the corpus runs a banana farm, so it bounds the
false-trigger side only. Round 1 filled that gap with the whole-game "tail"; round 2 refuses to,
because those seats are small denominators rather than farms being harvested, and the `F` gate
removes them by construction. No "catches X% of the tail" figure is quoted, because it would be the
wrong population.

## Defects 2–7

- **2** — `fE=`/`fW=`, the **window** counts frozen at the latch turn, added to the v7 group (nine
  tokens, ≤ 44 chars, still first). The claim that cumulative `fe`/`fw` audit the latch is
  **retracted**: 300 turns of cumulative counts cannot be narrowed to a 60-turn window afterwards.
  New gate **L4** recomputes the rule from the snapshot on every game with `fl > 0`. The `M = 15`
  part is not snapshot-recomputable and is checked against the panel's per-turn trace instead;
  §8 says so rather than implying the wire covers it.
- **3** — §2.1 is a strict priority order (`t`, `c`, `a`, `d`, `b`) evaluated once per turn, first
  match wins, written once. `d` is reworded so it and `a` are mutually exclusive, not merely
  ordered. The first round's baseline is the aim count **at aim selection**. An aim-species change
  resets the streak, and the design now prefers holding one aim through DENY, reselecting only on
  the `a`/`d` invalidations.
- **4** — W1 is unconditional on cargo: while wood is carried, that troll may select only
  move-toward-shack or DROP, whatever it was targeting at pickup. V3 inspects the accepted action
  stream from pickup to DROP-or-loss.
- **5** — V2 is now `codex_1/p4b/p4b_gate.py` run farm-on against farm-off on the identical
  `(map_id, seat)` corpus, keyed `(map_id, seat, own_unit_id)`, requiring
  `candidate_failed − base_failed` empty, with `GATE_UNREADY` a failure. V5 stays as a narrower farm
  invariant and §9 says explicitly that it does not stand in for V2. **One build step this creates,
  named so it is reviewed and not discovered:** `p4b_gate.py:310` allowlists `v4/v5/v6/none`, so the
  build must teach it `v7` plus a `narrate7` module with `narrate6`'s interface. That is an additive
  change to your tool and it is yours to approve.
- **6** — accepted; cancellation is same-**cell**. Invariant P is redundant with the existing
  `compatible`/`select` pair and the round-1 suppression rule is **removed from the design**. The
  champion's regeneration plants are left alone. V7 survives as a check, not a mechanism.
- **7** — the 0.2–0.6 band is demoted to a descriptive read with its caveat attached and travelling
  into the panel packet; it is not a gate and not proof. Value now reports the farm arm's own
  **window** `fe(60)/fw(60)` distribution against farm-off on the same games. Pre-registered
  expectation 3 is rewritten to be falsifiable three ways — above 40% means the rule is still too
  loose and the packet is at fault; 0% across 240 games is a suspicion, not a pass, and then L3/L4
  must be shown live on a constructed fixture; any fire before turn 60 is a build defect.

## §4.6 answers local_claude_1's scale run

The 23,613-replay run reproduces §1 exactly on the same 580 rows and confirms the 300-turn cap from
47,226 seats. Its game-length confound is a whole-game **denominator** artifact — the same class of
error as defect 1 — and it reverses under the windowed rule: on this sample short games (<290 turns)
fire at 4.0% against 6.9% for full-length ones, and the shortest game that fires anywhere is 269
turns. So the packet's answer to "what does the latch do when the game is ending early" is *nothing,
by construction*: a game under 74 turns cannot fire it, and after turn 250 the champion's endgame
wave has taken over planting, so a fire there has no behavioural effect. No turns-remaining term is
added. That reversal rests on **25 short ring-economy seats**, which is stated as a limit, not
hidden: `latch_sim.py` runs unchanged on the host's 66 MB full-corpus JSON, and the packet
pre-commits that `w`, `F`, `N`, `R`, `M` are **not** re-tuned on it if that run happens.

## Departures

D8 (the latch is five parts, not one comparison) and D9 (round 1's cumulative-counter audit claim,
withdrawn) are added to §10. D1–D7 stand as reviewed. Nothing in D1–D9 touches the three owner
decisions: the hut ring, the one-way latch, mothers-only planting during denial.

Reproduce both artifacts from §"Reproduce". No build is running; a build starts on ACCEPT and not
before.
