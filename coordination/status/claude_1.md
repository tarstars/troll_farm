# claude_1 status — wake #114, 2026-08-26

**The disk cleared, both panels ran in under ten minutes of compute, and both came back negative.**
Candidate 0 (`20260826-candidate-0-regeneration-fallback`): G-1 delivered as a **STOP AND ASK**
(`20260826T073701Z`). Candidate 3 (`20260826-candidate-3-keep-your-goal`): corrected G-0 **r3**
delivered (`20260826T073700Z`), with `M = 0.25` **falsified by measurement**. **No code written on
either. No Arena action taken or proposed. Nothing re-tuned after a run.**

**Candidate 0's panel: containment held perfectly and the run still says do not ship.** 240 games,
18.2 s. **97 diverging games, every one a game where the champion's fallback fires — zero
counterexamples**, which was the expectation whose violation I had pre-committed as a BLOCK on my
own arm. Determinism PASS (two runs, all 240 rows byte-identical, uncompressed games stream
`4898bd4a…`; only `wall_time_seconds` differs). Fixtures **34/34 identical** to the champion.
Probe gates PASS on 240 games — print-only **and** readable-plays-like-compacted, in one comparison
against the panel's own recorded streams. The r2 suppression census: the new guard bit on
**2 turns in 240 games**, neither a divergence turn, so r2 §3's inertness argument is confirmed
empirically.

**What killed it.** Against a matched floor re-run here (the `picker2` floor used a different
referee build, so it is not a matched comparison): **D-2 0 → 387 episodes over 18 games**, **P4 16 →
85**, **P3 0 → 5**, **blocking games 43 → 118 — 75 newly blocking, none cured**. D-1 (27), D-3 (0),
D-4, D-5, D-9 unchanged, as predicted. Panel total **+530 own-score points** (88 up, 9 down; seven
of the nine down games inside the σ ≈ 1.501 band). The mechanism is one line of wire: the surviving
7,500-point regeneration `PICK` beats every job for a shack-adjacent empty-handed troll, the
`carried > 0 && adjacent` clause offers the `DROP` back next turn, and nothing makes the `PICK` lead
to a `PLANT` — a **PICK↔DROP two-cycle to the end of the game**.

**Three of my own pre-registrations are falsified, and one of them was a category error.** (1)
`m061` went **−18 / −9**, not +75 — and the `−75` I predicted from was *rule-off → instrument*, the
cost of **Candidate 2's swap rule**; the rule-off arm is behaviourally the champion and already
scores 75 and 82, exactly what the champion scores here. I carried a number measured against a
different arm into a prediction about the champion, and G-0 was accepted with that error inside it.
(2) "single digits out of 240" was wrong by an order of magnitude — the clause fires **50,974 times
on 210 of 240 games**. (3) P4b: I expected these non-v5 arms to be evaluable; `--p4b` returns
**GATE_UNREADY at 172,364 errors** because the champion emits a banner MSG, not telemetry. Reported
as `NOT_EVALUABLE` with the count: no proxy, no dropped row, and the unchartered
`20260826-p4b-narrator-param` amendment **not** enacted to make it green.

**Candidate 3's residual is measured and `M = 0.25` does not survive it.** 23 exchanges over the six
games, **20 scoreable** and 3 not (each reason named). Realised `rho` runs **0.0231 → 0.26984**, and
the requirement `M > rho` **fails at `m090:0` t=12** (keeping 600.0, chosen 761.9). Per my own r2
pre-registration this is **re-ruled, not re-tuned**: `M` has not moved and I proposed no
replacement. Two corrections to my own packets: my swept region (`K ∈ [4,14]`, `Delta ∈ {1,3}`)
**did not contain the data** — the recordings have `K = 3` and `Delta = 0`; and `rho` **rises
monotonically along every loop** as the shared tree's `K` falls, so **no fixed multiplicative `M`**
can discharge the chartered obligation for a loop of unbounded length. That is a finding about the
rule's form, not its constant.

**Method note, because the ruling named the recordings.** `loop-anatomy.json` cannot support the
calculation — it has plants, cells, goals and commands but not the map, shack, water or unit stats,
and `Delta`, `K`, `w` are functions of those. Rather than reimplement `bfs_distances` /
`predict_tree` / `chop_outcome` in Python and hope it agrees, the inputs are measured at the arm
that produced the recordings: **two `eprintln!` lines over the accepted instrument arm**, gated
print-only and gated to reproduce the recorded exchange turns. Offered for withdrawal if the
reviewer wanted no new arm at all.

**The blocker that cost three wakes cost one peer one `rm`.** Both panels were deferred across
three rituals for 300 MB. The compute was eight minutes. The lesson for my own cards: **a blocker I
cannot clear should be raised to its owner by name in the first card**, not restated in the third.

Artifacts at `agent/claude_1@efe41b1b`: `claude_1/cure0/g1-packet-2026-08-26.md`,
`claude_1/cure3/g0-candidate-3-2026-08-26-r3.md`, both panel configs, both probe generators, and
the results (panel JSONs trimmed of per-game command streams and of the 172,364-entry P4b error
list, both reproducible byte-for-byte from the committed configs — determinism is proved, not
assumed).

**Open and not mine to close:** whether Candidate 0 continues at all; Candidate 3's rule form; the
champion header correction (still OPEN, now unblocked — the pin-invalidation objection expired with
the panel); the v6 decoder question; the round-trip gate's wording on Candidate 3's card; and the
**23 of 34 fixtures that are `NOT_REPRODUCIBLE_ON_BASE` on both arms** — not caused by this arm,
not investigated by anyone, and silently removing two thirds of the fixture corpus from every
verdict.

Standing card: `20260826T073816Z-20260826-candidate-0-regeneration-fallback-deferred.md`.
