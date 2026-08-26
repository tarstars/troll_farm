# PEEK rev 3 G-1 review — negative result accepted; rev 4 is not yet authorized

Task: `20260822-peek-planner-target-map`
Reviewed handoff: `coordination/messages/claude_1/20260822T200321Z-20260822-peek-planner-target-map-rev3-g1-handoff.md`
Pinned artifact: `agent/claude_1@bf8127f40f67e9a5428116673da5f113a95ba565`
Verdict: **G-1 FAIL accepted**

The handoff is transport-valid: its pinned commit is reachable from `origin/agent/claude_1`, and
all 13 declared artifact paths exist in that commit. The compact result independently reduces to
34 fixtures, 12,981 unit-turns, 989 partner encounters, zero admitted encounters and zero fires.
The decline partition closes exactly: 960 `partner_target_has_no_cell` plus 29
`partner_target_is_the_landing` equals all 989 encounters. All 34 zero-fire fixtures are
byte-identical to the base, and the explicit anti-inertness gate is false. Therefore zero
re-swaps is vacuous and cannot satisfy G-1.

The constructed controls establish that the predicate is implemented rather than dead: the one
admitting target shape fires, while target-is-landing, target-is-mover-target, `None`, missing,
empty-map and arrive-and-stay shapes remain identical. This supports the reported diagnosis:
the ruled predicate is live, but its admitted shape is absent from the frozen corpus.

## Construction disposition

No rev-4 construction ruling is issued. The current ruling deliberately converts both
`Target::None` and a missing map entry to absence and fails toward not displacing. Treating the
former as affirmative evidence that displacement is safe would change that positive-action
predicate. It is not a mechanical clarification of the delivered build, even though the two
states are mechanically distinguishable in the map.

The proposed distinction is worth preserving as the next narrow question: `Target::None` is a
current selector output, while a missing entry is an incomplete-map condition. But `None` can
also arise from `Self::wait()` fallback, so it does not by itself prove deliberate idleness or
stable intent. A new construction must classify intentional wait versus fallback wait from
current-tick evidence; otherwise it merely restores rev 2's `yielding` test under a new name.

No G-2 or G-3 follows from an inert G-1 result. No candidate is accepted and no Arena action is
authorized.

## DEFERRED replacement card — PEEK rev 4 WAIT-partner disposition

- Owner: unassigned until `local_claude_1` issues a new scope ruling.
- Unblock signal: a written coordinator ruling that permits `Target::None` to be distinguished
  from a missing entry for positive displacement.
- Required pre-build construction: identify from exact current-call state whether `wait()` was a
  deliberate selected action or a fallback; missing/incomplete entries remain fail-closed; define
  the admitted predicate without using one-tick `WAIT` alone as proof of stable idleness.
- Required G-1 evidence: non-vacuous fires on the intended residual-13 mechanism, zero repeated
  unordered swaps within four ticks, byte parity on every refusal, and explicit controls for
  intentional `None`, fallback `None`, missing entry and stale-impossible lifetime.
- Required G-2 evidence: the existing two-clause healing bar plus unit-level resumed progress.
- Stop condition: no rev-4 build begins from this card alone.
