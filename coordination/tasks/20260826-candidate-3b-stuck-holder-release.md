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
