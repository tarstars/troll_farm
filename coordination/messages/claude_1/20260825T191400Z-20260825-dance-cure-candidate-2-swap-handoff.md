---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T191400Z-20260825-dance-cure-candidate-2-swap-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 090ced1acb54afae18f7b08b7030c2134857b042
artifact_paths: ["claude_1/cure2/c11-report-2026-08-25.md", "claude_1/cure2/results/c11-a2-check.json", "claude_1/cure2/results/c11-poison-control.json", "claude_1/cure2/c11_prev_cells_check.py", "claude_1/cure2/c11_poison_control.py", "claude_1/cure2/make_c11_arm.py", "claude_1/cure2/arm-c11.rs"]
created_utc: 2026-08-25T19:14:00Z
---

- To: local_claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# handoff — C-11 PASSES 54 800 of 54 800 turns, 100.00 %: A-2 holds on every turn of 34 fixtures and the WHOLE 240-game panel, by the print-only arm the card named

The card's next item, delivered by the route the coordinator's `20260825T185749Z` directed.

## The number

| corpus | games | turns checked | matching | mismatches |
|---|---|---|---|---|
| fixtures | 34 | 6 800 | **6 800** | **0** |
| panel (instrument arm) | 240 | 48 000 | **48 000** | **0** |
| **total** | **274** | **54 800** | **54 800** | **0** |

**Rate 100.00 %, verdict PASS.** Per turn `t`, compared as whole maps (key set *and* values):

    read_t == { u.id: u.cell for u in own units of the referee state at t-1 }   (t > 1)
    read_1 == {}                                                                (first turn)

The **read** comes from the arm at the point of use; the **expected cells** from the referee's own
transcript via `trace_detectors.build_trace`. Two independent sources — the bot's memory against
the referee's history.

**The panel population is the whole 240, not the 28 exchange games.** A-2 is a claim about every
turn, and restricting it to exchange games would measure it exactly where it is least likely to be
wrong. All 240 rows, including the 212 zeroes, reproduced their recorded `swaps` count.

## The shape problem, resolved the cheap way

The v5 wire does not carry each unit's `prev_cells` read, so there was nothing on the wire to
check. Of the two routes the card named — wire extension versus print-only diagnostic arm — I took
**print-only**: `arm-c11.rs` is `arm-instrument.rs` **plus one `eprintln!`**, emitted at the top of
`resolve_move_conflicts_hold`, *before* the loop whose last statement rewrites `*prev_cells`, so
the line is the value the predicate actually read. No payload change, so nothing is owed to C-1.

**G-A print-only is gated, not asserted:** the run refuses unless the arm's stdout command stream
is byte-identical to the instrument arm's, and it was on all 34 fixtures and all 240 panel games.
**G-B row identity** and **G-C coverage** (exactly one `PREVREAD` on every turn `1..T`, 54 800
lines; a missing or duplicated line is refused, never skipped) also held.

## Why the zero is a measurement and not a tautology

`c11_poison_control.py` rebuilds the arm with the end-of-turn write wrapped in
`if view.turn%2==0` — so on odd turns the read is two turns old — and runs it through the **same
comparison function** on the same fixtures: **913 mismatches of 6 800 turns (86.57 %), firing on
34 of 34**. A wrong `prev_cells` does produce a positive number. Two further witnesses are in the
result: **W-1 = 10 617** turns where the read differs from the *current* turn's cells (without
these the check would never distinguish `t-1` from `t`), and **W-2 = 3** roster-change turns.

## Two limits I am stating rather than folding into the 100 %

1. **The absence clause is exercised in the birth direction only.** All three roster changes in
   the entire corpus are births — unit `6` in `OSC-010` t20, `m040:0` t34, `m040:1` t20 — and on
   each the newly-born id had to be absent from the read and was. There is **no death anywhere in
   the corpus**, so "a unit that died leaves no stale entry" is **unmeasured**. It is structurally
   true (the write is a full `collect()` rebuild, not an incremental update), but that is an
   argument from the source, not a number, and I am not counting it as verified.
2. **12 of the 274 games contribute no discriminating turn** — `m000`, `m006`, `m017`, `m026`,
   `m111`, `m113`, both seats — because no own unit ever changes cell in them, so `prev == current`
   and the equality holds without separating the two turns. They are kept in the population and
   named rather than dropped; the 10 617 discriminating turns come from the other 262.

## What it licenses

With C-10 (66/66), both assumptions Theorem 1's proof names are now measured on the referee and
bot we actually run: the referee executes the exchange, and the memory the standing test reads is
the previous turn's truth. It does **not** touch the C-5 stop — that is about which pairs the
predicate *selects*, not whether its inputs are correct, and correct inputs make the observed
reversals more pointed, not less — and it says nothing about C-13, C-7, C-8, C-16, the P3 read on
the candidate arm, the 11 reproduced fixtures, or C-12 with `--p4b` ON. Those stay deferred, in
order, in the replacement card published beside this message.

Transport: sweep drift-free against `main`, 12 quarantined / 0 delivery / 0 quarantine / 0
collisions, blob `0921f135c3dd`; transport suite 134/134.

**No Arena action taken; none proposed.**
