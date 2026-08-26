# 20260826-candidate-3b-stuck-holder-release: Candidate 3b — Candidate 3 plus the "stuck holder" release (owner 2: "A")

- Status: **OPEN — CHARTERED 2026-08-26T15:45Z by owner ruling (A)**. Board row D-4. A NEW candidate, not a reopening of Candidate 3 (closed 14:05Z).
- Record owner: local_claude_1 · Work owner: **claude_1** · Reviewer: codex_1 (D3-G1 review of the read, then one reproduction of the panel) · Arena: ladder slot 2 **only on a panel pass**, coordinator submits.
- **The rule (from D-3's data, `claude_1/cure3/m061-stale-goal-read-2026-08-26.md` §4 rule iii):** Candidate 3 as built, plus one release cause — **a kept goal is released when its holder has occupied ≤ 2 distinct cells for 20 consecutive turns and emitted no work command (CHOP/PICK/DROP/PLANT) in them** (`rs=`, counted). No margin, no turn cap, no other change. Fires t72 (seat 0) / t108 (seat 1) on `m061`; reaches 4 non-`m061` games, none won by the cure (`+risk 0`).
- **Done means:** one build (diff on the readable source `readable/diffs/candidate-3b-stuck-holder-release.diff`, round-trip identity), one panel (240 + 34) with these **pre-commitments written before the run**: containment byte-identical rule-off; `xc = 0` on the six loop games; **own-score total outside `m061` ≥ Candidate 3's +25 − 5**; **`m061` both seats within 10 points of the champion** (75 / 82); no game that Candidate 3 won lost; `ka` max < 60; determinism; every changed game named with its own-score delta. codex_1 reproduces once. Then the verdict is written and the task stops — pass or fail.
- **Dead means:** any pre-commitment fails → CLOSED, obituary, no r2, no retune (the owner's bound applies to 3b as to 3).
- **Budget:** 1 build, 1 panel, 1 reproduction, ladder slot 2 only on a pass (8 reads vs the champion's), 2 calendar days.
- Created UTC: 2026-08-26T15:45:00Z · Last updated UTC: 2026-08-26T15:45:00Z

## Honest expectation (owner-facing)
+25 fruit over 240 games is ≈ 0.1 fruit per game; the ladder has not seen two generations of cures. What this buys is a finished dance line with a positive, understood result and code the owner has read — not points. A ladder block is spent only on a pass.

## Order
Build may start now; **no panel number is read before codex_1's D3-G1 verdict on the read** (if the review breaks rule iii, the build stops). Diff and packet on `main` at the gate.

---

## Pre-commitments — written 2026-08-26T15:16Z by claude_1 BEFORE any source was generated

Nothing below may be edited after the first arm is built. The panel is read against exactly this
list; a failure on any line closes the task under "Dead means" with no retune.

**The rule, stated to the byte.** A kept goal is released when its holder has occupied **at most 2
distinct cells over the last 20 consecutive turns** *and* emitted **no work command in any of those
20 turns**, where a work command is one of **`CHOP`, `HARVEST`, `DROP`, `PLANT`, `PICK`**. Release
reason `rs=`, counted on the wire like every other release cause. No margin, no turn cap, no other
change to Candidate 3.

**Named discrepancy, resolved before the build (not after).** The charter line above abbreviates the
work set as "CHOP/PICK/DROP/PLANT" — four verbs, omitting `HARVEST`. The rule's source, D-3's read
§4(d), and the probe that produced every number the charter quotes (`claude_1/cure3/m061/fixprobe.py`
line 32, `WORK = ("CHOP", "HARVEST", "DROP", "PLANT", "PICK")`, used by `idleprobe.py`) both use
**five** verbs including `HARVEST`. The four-verb reading is a summary slip in the charter, not a
different rule: with `HARVEST` dropped, a troll standing at a tree harvesting fruit reads as "not
working" and gets released, which is exactly the false positive the second clause was added to
prevent. **I implement the five-verb rule** — the one the measurement was made with, so that
"fires t72 / t108 on `m061`, touches 4 games outside it, removes 58 productive commands" remains a
statement about the thing I built. The two readings are separated by measurement before the build,
on the existing archives, at no panel cost; the result is published with the packet.

**The gates, each pass/fail, each read once.**

1. **Containment.** The rule-off arm (`KEEP_RULE_ENABLED=false`) is byte-identical to the champion's
   command stream on all 240 panel games. A cure that leaks with its own rule off is not a cure.
2. **Loop cure preserved.** `xc = 0` on all six loop games — 3b must not lose what Candidate 3 won.
3. **Own score outside `m061`.** Total ≥ **+20** (Candidate 3's +25, minus a 5-point tolerance).
4. **`m061` both seats within 10 points of the champion** — champion 75 (seat 0) / 82 (seat 1).
5. **No game that Candidate 3 won is lost by 3b.**
6. **`ka` maximum < 60** across all 240 games — the 171-turn goal is the disease being treated.
7. **Determinism.** Re-running the panel reproduces every command stream byte-for-byte.
8. **Every changed game named** with its own-score delta, in the packet — no aggregate without its
   rows.
9. **One source, one flag line.** `build_arms3.py`'s existing check still holds: each arm differs
   from `cure3-keep-v6.rs` by exactly one line. Rule iii is anchored replacement inside the shared
   source, not a fourth arm.

**Order.** Build, then the panel, then codex_1 reproduces once. Diff on the readable source at
`readable/diffs/candidate-3b-stuck-holder-release.diff` with a round-trip identity report. No ladder
booking before a pass; on a pass it goes to the owner's queue, and the coordinator submits.
