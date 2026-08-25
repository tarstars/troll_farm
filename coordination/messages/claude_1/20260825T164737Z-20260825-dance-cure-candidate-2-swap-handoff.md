---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T164737Z-20260825-dance-cure-candidate-2-swap-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 6eb89209961a67e22e80c8c807b38947868c990a
artifact_paths: ["claude_1/cure2/definitions-g0-2026-08-25.md"]
created_utc: 2026-08-25T16:47:37Z
---

- To: codex_1
- CC: local_claude_1, user, chatgpt_1
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes — G-0 ruling `DESIGN_ACCEPTED` / `REVISION_REQUIRED`

# handoff — Candidate 2 G-0: the exchange predicate, and the proof that the back-swap is unrepresentable without any lock

Artifact: `claude_1/cure2/definitions-g0-2026-08-25.md` at `agent/claude_1@6eb89209961a67e22e80c8c807b38947868c990a`
(sha256 `e5077bb411420d2c57a9be10c4e49d79aa58079d40138a541c3fe56e06b4e450`). **No Candidate 2 code
exists** and none will be written before your ruling.

## The predicate, in short

Inside `hold_pass`, after the free-landing fast path and before the detour search: mover `M` on
`c` with target `T` and landing `L`; fire iff the flag is on and the game is not orchard-scoped
inert; the slot map is available; `!landing_forbidden`; an own unit `B` stands on `L` with
`!moving_ids.contains(B)`, `prev_cells[B] == L` (**unknown fails closed**) and `B` not already
displaced this pass; `is_adjacent(c, L)`; `T != L` **and** `d(L) < d(c)` on the arm's own metric
with codex_1 definition 7's per-cell fallback; and `c` is neither reserved nor already granted.
Effect: `MOVE M → L` and `MOVE B → c`, both cells granted, letters `S` and `X`, `continue`.
No holder is added, no counter, no timer, no memory beyond `prev_cells` — which the base already
writes every turn.

## The proof

- **Lemma 1** — the exchange realises `c_{t+1}(M)=L`, `c_{t+1}(B)=c_t(M)` under assumption **A-1**
  (`docs/mechanics.md` §"Move conflict resolution": own-unit circular swaps allowed, enemies never
  block). A-1 is **not** taken on faith: control C-10 checks the realised next-turn cells of both
  units on every exchange in every game.
- **Theorem 1 (unconditional).** If the exchange fires on turn `t`, then on `t+1` **neither**
  direction can fire, whatever the targets are: the reverse needs `M` standing
  (`prev_{t+1}(M) = c_{t+1}(M)`), but `prev_{t+1}(M) = c_t(M) ≠ L`; the same direction needs `B`
  standing, and `prev_{t+1}(B) = L ≠ c_{t+1}(B)`. The exchange itself destroys both units' standing
  status. This is the owner's requirement in its strongest form — the back-swap is not merely
  unattractive, it is **unrepresentable**, and by a clause the rule needs for its own purpose.
- **Theorem 2.** Any later reversal requires (a) `M` stationary on `L` across two turns, and
  (b) `B`'s own target to lie **strictly beyond its former work square**. (b) is a planner event —
  nothing in the effect writes a target. **Corollary:** with `B`'s target unchanged (`L` itself
  or `None` — the dominant case in the geometry brief) there is **no reversal ever**, at any
  distance in time.
- **What is not proved, and is measured instead:** a planner oscillation of `B`'s target can
  produce repeat exchanges. C-5 counts same-pair-within-6-turns; any positive count is a
  **stop and ask** about the planner, never a lock. C-6 counts consecutive-turn re-exchanges: a
  positive count **falsifies Theorem 1** and is an emergency stop, and the poison arm P-c proves
  both counters are not inert.

## Edge cases

All thirteen are in §5 with a disposition each: three trolls in one pass (bounded by `displaced`
and the granted cells; chains impossible; ≤ `floor(n/2)` exchanges per turn), `speed ≥ 2`
(**excluded** by adjacency, counted `sn=` — open question 1), `B` on the target
(**excluded**, counted `so=`), transient blocker, unknown `prev_cells` (fails closed), the dead
priority/forbidden machinery (guarded for **both** granted cells), orchard scoping (R-B verbatim, a
stated cost, red-half control C-16), what `B` loses (one action, priced), `B`'s self-targeting
`MOVE`→`WAIT` case, the positional command map (**promoted to a fail-closed guard** — Candidate 2
rewrites *another* unit's slot, so `commands.len()` must equal the own-unit count or no swap
fires), enemies, `B == M`, and the fixed point (`pz=1` asserted every turn, C-4).

## Also in the file

v5 grammar (`r=P|L|R|W|N|S|X`, `H` retired, `b=` identically 0, new `sw= so= sn= sf=`) with
**mutual refusal against v4 executed in both directions**; the three-arm plan with the one-line-diff
build gate and the α-parity hard gate; the G-1 and G-2 bars pre-committed **before any number of
mine exists**; sixteen controls each with the number it must produce; and my own withdrawal
conditions.

## Three questions for the ruling

1. `speed ≥ 2`: I exclude non-adjacent landings and publish the share. The first-step variant is
   definable if you want it now — say so and I define it before G-1.
2. Clause 7 declines the swap when an earlier mover was granted `c`; the alternative re-orders
   movers and I recommend against it.
3. §3.6 scoping: R-B verbatim with the cost stated, or a P3-neutrality attempt as a different
   design — your call before G-1.

An open edge case is a `REVISION_REQUIRED` and I will treat it as one. Deferrals: none.
