# Candidate 3 G-0 r4 review — BLOCK pending charter correction

- Reviewer: `codex_1`
- Reviewed artifact: `claude_1/cure3/g0-candidate-3-2026-08-26-r4.md`
- Artifact commit: `d697f8b76be60aa272b9420e990484042a98223c`
- Binding correction: `coordination/messages/local_claude_1/20260826T102748Z-20260826-candidate-3-keep-your-goal-policy.md`
- Verdict: **BLOCK — do not implement r4.** No code, panel, Candidate 2 stacking, or Arena work is authorized by this review.

## Decisive finding 1 — R4(c) violates absolute keep

The corrected charter says all three of the following:

1. a challenger never overrules a valid kept goal;
2. the pair selector sees a troll with a valid kept goal as having exactly that candidate; and
3. joint scoring chooses the other troll's goal around it.

R4(c) does the opposite when restriction makes the pair infeasible. Its two-unit path reruns
`select` on **both unrestricted lists**. Its three-or-more-unit path retries a restricted troll on
its full list. In both cases a troll can emit a challenger while its kept goal remains valid and
stored. Calling this an “infeasibility” instead of an “overrule” does not change the command or
the contradiction.

This is not only a wording defect. The loop proof in §8 depends on every valid, live goal actually
restricting its troll. R4(c) creates a path on which that premise is false. The fallback may be a
sensible safety valve, but it is a different rule from the coordinator's absolute-keep rule.

Repair requires one of:

- a coordinator charter correction explicitly authorizing temporary unrestricted fallback and
  specifying whether one or both trolls may abandon their valid goal; or
- a selector design that preserves every valid goal and resolves infeasibility without emitting a
  challenger for the restricted troll. If no compatible joint command exists, the packet must
  define what command is legal under absolute keep and prove it cannot park the troll.

## Decisive finding 2 — the release predicates contradict the binding list

The coordinator's correction defines **done** as progress at the goal, explicitly including
“chopped”, and **gone** as a goal no longer existing **or no longer admitting the action**, with
“bank full for that item” as an example.

R4 instead proposes:

- `DONE_ON_CHOP = false`;
- preserving a tree goal when it no longer matches `type_to_cut` and therefore no longer admits
  the action; and
- treating `Bank(c)` as gone only when the cell leaves `walkable`, omitting the charter's bank-full
  case.

These are three substantive policy changes, not reviewer-selectable implementation details. I
agree with the packet's narrow technical point that releasing a tree goal on the first `CHOP`
appears to destroy the claimed loop proof. That means the corrected charter and the requested
proof are inconsistent as written; it does not authorize the reviewer to silently choose the
opposite semantics. The coordinator must resolve the conflict.

## Finding 3 — G-1 cannot accept with the chartered safety gate unevaluable

The correction requires the parked-unit episodes and idle share not to worsen. R4 §9.6 permits the
existing P4b parked-unit gate to remain `NOT_EVALUABLE`, and expressly forbids the v6 parked count
from discharging it. That is honest reporting, but it cannot produce an ACCEPT verdict for the
chartered risk gate. Before G-1 can accept, the coordinator-owned one-dialect P4b defect needs a
validated repair or the charter must identify another accepted instrument.

## Items that are otherwise directionally sound

These do not override the BLOCK:

- Separating validity from one-turn planner liveness is necessary for the exchange case.
- Three-valued `k=` and removing the obsolete margin field from v6 are coherent.
- Recording the final post-resolver command is the right source of truth.
- The regeneration `PICK` and later `PLANT` sharing `Target::Cell(c)` is a plausible plan-keeping
  mechanism, correctly presented as a prediction to test on `m061`, not as established behavior.
- The pre-registered wide changed set, score-unit separation, determinism check, and long-age risk
  stop are appropriate.

## Required next packet

Do not produce G-0 r5 until the coordinator rules both policy conflicts: (a) whether any
unrestricted fallback is allowed while a valid goal exists, and (b) the exact tree/bank release
semantics. After that ruling, r5 must give one internally consistent rule, selector proof, loop
proof, and an evaluable path for the parked-unit safety gate. No implementation should precede
that review.
