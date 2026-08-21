# 20260821-p4-stalls-real-end-regrade — the 34 recorded windows against the real end of the game

Task `20260821-p4-stalls-real-end-regrade`, coordinator-chartered 2026-08-21T09:30Z (policy
`coordination/messages/local_claude_1/20260821T093404Z-20260821-p4-stalls-real-end-regrade-policy.md`).
Work owner claude_1 · reviewer codex_1 · integrator local_claude_1.

**Measurement only.** No fix, no candidate, no behaviour change, no re-ruling of any case, no
class-wide claim beyond these 34, no Arena action. Nothing here touches the resident file, the
dev copy or the Arena.

- Instrument: `claude_1/regrade1/real_end_regrade.py`
- Artifact: `claude_1/regrade1/real-end-regrade-2026-08-21.json`
- Frozen library: `claude_1/banana-restoration-r2/oscillation-library-98628e98/library/`
  (`library_sha256` `1370384da9ca…`, 34 situations)
- Adapter: the **G-3-accepted** one, `claude_1/cause1/g3_finding.py`, imported unmodified
  (`to_sim_state`, `check_adapter_fidelity`, `stall_negative_control`); its per-turn identity
  control runs on every turn of every fixture of both arms. Digest recorded in the artifact.
- Predicate: the frozen `sim.engine.has_stalled` (Rust original `rust/src/game/engine.rs:819`,
  referee v1.0.5 `Board.hasStalled`), unmodified and unwrapped.

---

## The answer in one paragraph

**None of the 34 recorded windows extends past the real end of its game. Not one turn.** On the
bot that actually produced them, 18 of the 34 games never reach `has_stalled` at all inside the
200-turn horizon, and the other 16 end between **3 and 46 turns AFTER** their window closes; the
tightest is OSC-009 at +3. Zero wholly artifact, zero partly artifact. That includes OSC-031 and
OSC-034, and it includes **OSC-032 and OSC-033**, whose recorded games never stall.

The reason that last sentence does not read like the OSC-032/033 ruling is the finding below:
the card's premise re-runs the **champion** against windows recorded from a **different bot**,
and on 23 of the 34 fixtures the champion's replay is demonstrably not the recorded episode.

---

## 0. FINDING — "the champion re-run" and "the recorded window" are two different games

The card asks for the real end turn "on the champion re-run". The champion is
`claude_1/chop4c/candidate-door1.rs` (`547fa706…`). The 34 windows were not recorded from it.
The frozen library's own provenance names its subject:
`cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` (`98628e98…`), judged against
itself on the panel floor.

So the run has two arms, and they answer different questions:

| arm | bot | reproduces the recorded episode | what its end turn is about |
|---|---|---|---|
| **subject** | `98628e98…` | **34 / 34** | the recorded window. **This is the arm that answers the card.** |
| champion | `547fa706…` | 11 / 34 | the champion's own game on that map, seed and opponent |

On 23 fixtures the champion's replay fails episode identity — different commands inside the
window, and/or a different board at the window's first turn.

**OSC-032 and OSC-033 are two of those 23.** Their window commands are every one `WAIT`, so a
command comparison alone passes; the boards do not. At OSC-032's window entry, turn 91, the
library's frozen state still carries a **live PLUM at (11,5)** and 5 WOOD in the shack. The
champion's replay of that map has had a **bare board since turn 82**. Same map, same seed, same
opponent profile, two different games — and both sides emit `WAIT`.

This does not make the G-3 numbers wrong. Re-run here, they reproduce exactly: the champion's
game on the OSC-032 map does end at turn **82**, and on OSC-033 at turn **13**, and its own idle
turns after those points are real idle turns past a real end. What does not follow is the step
from there to *the recorded windows*: turns 91–200 and 58–200 are the **subject's** window
numbers, and in the subject's games the referee never ends either one. Comparing an end turn from
one bot's run with a window from another's is the cross-game figure error, and it is what the
one-line inference "no real game would have reached the audited windows" rests on.

Scope discipline: this is **not** a re-ruling and **not** a claim that the owner's "unplayable"
was wrong. It is a statement about which game each number describes. The consequences are put to
the owner as a question in §4, exactly as the card requires.

---

## 1 & 2. The table — all 34, P4 stalls first

Real end = the first turn `has_stalled` returns True on the SUBJECT arm. `+n` is how far that
falls **after** the window closes. "Window turns past the real end" is the card's deliverable-1
number.

| case | kind | recorded window | real end (full rule) | grace-only bound | window turns past the real end | verdict | champion arm |
|---|---|---|---|---|---|---|---|
| OSC-031 | P4 | 11–200 (190t) | never | never | **0** | real throughout | ends never, **different game** |
| OSC-032 | P4 | 91–200 (110t) | never | never | **0** | real throughout | ends 82, **different game** |
| OSC-033 | P4 | 58–200 (143t) | never | never | **0** | real throughout | ends 13, **different game** |
| OSC-034 | P4 | 6–99 (94t) | **115** (+16) | 115 | **0** | real throughout | ends 8, **different game** |
| OSC-001 | D1 | 6–200 (195t) | never | never | **0** | real throughout | ends never, same game |
| OSC-002 | D1 | 12–200 (189t) | never | never | **0** | real throughout | ends never, same game |
| OSC-003 | D1 | 25–47 (23t) | **59** (+12) | 59 | **0** | real throughout | ends 26, **different game** |
| OSC-004 | D1 | 9–22 (14t) | **45** (+23) | 50 | **0** | real throughout | ends 33, **different game** |
| OSC-005 | D1 | 7–18 (12t) | **61** (+43) | 61 | **0** | real throughout | ends never, same game |
| OSC-006 | D1 | 12–20 (9t) | **46** (+26) | 46 | **0** | real throughout | ends 28, **different game** |
| OSC-007 | D1 | 8–16 (9t) | **30** (+14) | 35 | **0** | real throughout | ends 18, **different game** |
| OSC-008 | D1 | 57–64 (8t) | **110** (+46) | 147 | **0** | real throughout | ends 93, **different game** |
| OSC-009 | D1 | 77–83 (7t) | **86** (+3) | 96 | **0** | real throughout | ends 107, **different game** |
| OSC-010 | D1 | 80–86 (7t) | never | never | **0** | real throughout | ends 200, **different game** |
| OSC-011 | D1 | 26–32 (7t) | **52** (+20) | 52 | **0** | real throughout | ends 48, **different game** |
| OSC-012 | D1 | 8–200 (193t) | never | never | **0** | real throughout | ends never, same game |
| OSC-013 | D1 | 14–200 (187t) | never | never | **0** | real throughout | ends never, same game |
| OSC-014 | D1 | 33–200 (168t) | never | never | **0** | real throughout | ends 57, **different game** |
| OSC-015 | D1 | 44–200 (157t) | never | never | **0** | real throughout | ends 68, **different game** |
| OSC-016 | D1 | 7–200 (194t) | never | never | **0** | real throughout | ends 14, **different game** |
| OSC-017 | D1 | 7–200 (194t) | never | never | **0** | real throughout | ends never, same game |
| OSC-018 | D1 | 10–200 (191t) | never | never | **0** | real throughout | ends 15, **different game** |
| OSC-019 | D1 | 23–200 (178t) | never | never | **0** | real throughout | ends 46, **different game** |
| OSC-020 | D1 | 29–200 (172t) | never | never | **0** | real throughout | ends 34, **different game** |
| OSC-021 | D1 | 32–200 (169t) | never | never | **0** | real throughout | ends never, same game |
| OSC-022 | D1 | 106–200 (95t) | never | never | **0** | real throughout | ends 38, **different game** |
| OSC-023 | D1 | 27–100 (74t) | never | never | **0** | real throughout | ends 38, **different game** |
| OSC-024 | D1 | 5–69 (65t) | **80** (+11) | 80 | **0** | real throughout | ends 80, same game |
| OSC-025 | D1 | 12–32 (21t) | **46** (+14) | 52 | **0** | real throughout | ends 51, **different game** |
| OSC-026 | D1 | 17–25 (9t) | **40** (+15) | 45 | **0** | real throughout | ends 40, same game |
| OSC-027 | D1 | 3–24 (22t) | **37** (+13) | 37 | **0** | real throughout | ends 32, same game |
| OSC-028 | D1 | 2–54 (53t) | **86** (+32) | 96 | **0** | real throughout | ends 107, **different game** |
| OSC-029 | D1 | 28–44 (17t) | **61** (+17) | 67 | **0** | real throughout | ends 53, **different game** |
| OSC-030 | D1 | 24–31 (8t) | **46** (+15) | 64 | **0** | real throughout | ends never, same game |

**Wholly artifact: none. Partly artifact: none. Real throughout: 34 / 34.**

The two P4 stalls the card asked to see first, OSC-031 and OSC-034: OSC-031's game never stalls
inside the horizon, so its 190-turn window is real end to end; OSC-034's ends at turn 115, which
is **16 turns after** its window closes at 99. No D1 dance straddles a real end either — the
closest any window comes to one is OSC-009, whose window closes at 83 with the referee ending at
86.

Read the last column with care: on the champion arm the numbers marked "different game" are the
champion's, and the ones marked "same game" only had identity checked up to the window's end —
after that the two bots may diverge, so a champion end turn lying beyond the window is not
attributable to the recorded episode either. Nothing in the champion column is used for a
verdict.

---

## 3. What this does NOT change

- **Every ruling already made stands.** The 18 BUG (benching class), the six BUG (4b sittings of
  2026-08-21) and the 8 FIXED are untouched. This card annotates them with a real-end turn; it
  does not re-grade them.
- It does not say any case was mis-classified as an oscillation. Whether a window is an
  oscillation is the detectors' question; this measures only whether the referee would still
  have been playing.
- It does not say the harness lesson from OSC-032/033 was wrong. The harness really does play a
  fixed horizon and really does not call the referee's end condition. What this run shows is that
  on the recorded corpus that gap **changes nothing** — the windows all close before the end
  anyway — and that the hazard which actually bit was a different one (§0).
- It does not re-open OSC-032/033. That is §4's question, for the owner.
- No claim is made beyond these 34 fixtures.

---

## 4. Deliverable 4 — the recommendation, and the question the finding raises

**Q1, to the owner (via the coordinator): does §0 change anything about the OSC-032/033
disposition?** The recorded OSC-032/033 episodes never stall; it is the champion's replay of
those maps that ends at 82 and 13. Both statements are measured and both are in the artifact. I
am not proposing a re-open and have no view on which the ruling should rest on — the cause
task's subject may well have been the champion's behaviour all along, in which case the ruling
stands untouched and only the wording "the recorded idle turns do not exist" needs narrowing.

**Q2, to the coordinator — should `sweep34` and the harness apply `has_stalled` by default?**

Recommendation: **not as a horizon cut; yes as an annotation — and fix the identity gap first.**

- On this corpus, cutting the horizon at `has_stalled` would change **no** window, because none
  of the 34 reaches its real end. The change buys nothing here, and it silently truncates any
  future window that does straddle an end, turning a measured artifact into an invisible one.
- Record the real end turn on every graded row instead, from the same frozen predicate. Then a
  window that straddles an end is visible as a number rather than as a missing tail.
- Quote the **grace-only** bound whenever the opponent is in doubt. The full rule's mercy clause
  reads the opponent's inventory and score, so it is a property of the replayed opponent, not of
  the map. Both columns are in the table above for exactly this reason.
- **The gate worth adding is episode identity, not `has_stalled`.** Two cheap comparisons —
  window commands, and the board at the window's first turn against the frozen
  `world_state_at_entry` — would have caught §0 at the moment the champion was pointed at a
  subject-recorded window. `spec_for` already refuses a wrong *map*; nothing refuses a wrong
  *game*. I would put this ahead of Q2's own subject.

---

## Gates, and where this run could still be lying

| gate | what it rules out | outcome |
|---|---|---|
| spec fidelity (`fixture_harness.spec_for`) | replaying a different map | pass, 34 × 2 |
| recorded-episode identity, (a) window commands + (b) frozen entry state | comparing turn numbers across two games | subject **34/34**, champion **11/34** |
| adapter fidelity, per turn (G-3's, unmodified) | handing `has_stalled` a board the referee never had | pass, every turn, 34 × 2 |
| corpus non-vacuity | a predicate observed in one direction only | False-with-plants on 34/34; True-on-bare on 16/34 (subject) |
| stall predicate control (G-3's four constructed states) | an inert predicate | pass, 2 must-stall / 2 must-not |
| subject-bot digest vs library provenance | replaying something that is not the subject | pass |
| fail-closed | a silently skipped fixture making "34" a lie | no fixture skipped |

**The identity gate is non-vacuous by construction, and this is the point worth checking hardest.**
A guard that has only ever agreed is not evidence of agreement, and comparison (a) on its own is
exactly that on an all-`WAIT` window — it passed OSC-032/033 while the boards differed. The run
therefore *requires* the pair to accept all 34 on the subject arm and to reject at least one on
the champion arm, and fails if either does not hold. Both arms were run for this reason and not
only to answer the card twice.

**What this run does not control for.** Episode identity is verified at the window's first turn
and across the window's own turns; turns after the window close are unchecked, because the
library froze nothing about them. For the subject arm this is harmless — it is the recorded bot
replaying its own recorded game — but it is the reason no verdict is drawn from the champion
column even where identity passed.
