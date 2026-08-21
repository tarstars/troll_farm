# Cure C G4 independent review — 2026-08-18

Verdict: **REVISION_REQUIRED / NOT QUALIFIED FOR G5**.

Pinned handoff: `f7c159a9eac6b2f34597b236ec6b856b56064521` on
`agent/claude_1`. Candidate SHA-256:
`ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1`.

## Static implementation review

The candidate is generated from readable resident SHA-256 `98628e98...`. Its only
behavioral diff is one hunk at the mid-game empty-chop fall-through: the old
`endgame_candidates` return is replaced by an explicit WAIT seed, idle-harvest
candidates, and bank candidates when carrying. The full-capacity exit, true-endgame
routing, chop path, banana logic, and all other code are unchanged. The build script
reproduced that one-hunk diff and verified the readable resident remained byte-exact.

The implementation therefore matches Cure C as chartered. This does not make the
candidate qualified: the charter separately requires every G1--G3 clause to be green.

## Independent execution

I created a detached temporary worktree at the pinned handoff and reran the documented
commands, including rebuilding both 240-game panel arms rather than consuming only the
committed summaries.

### G1 — RED

- Fail-first reproduced exactly: OSC-008 7, OSC-028 51, OSC-032 110, OSC-033 143,
  totaling 311/311 no-goal turns on the unmodified readable resident.
- The candidate reduced all four to zero.
- All 34 fixtures reproduced with zero de-novo D-1 and zero de-novo P4.
- Frozen predicted-uncured clause 3 did not reproduce: OSC-009 predicted 4 remaining
  but observed 0; OSC-031 predicted 178 remaining but observed 89. OSC-001 and OSC-005
  matched.

The misses are beneficial over-delivery, but the charter says the predicted-uncured set
must behave as predicted. A reviewer cannot convert that requirement into a directional
criterion after observing the result. The registry remains properly frozen; G1.3 is red.

### G2 — FAIL

The independent 240-game rebuild reproduced:

- de-novo D-1: 1 game (`m082`, seat 1);
- de-novo P4 by episode count: 3 games (`m061`/0, `m082`/1, `m106`/0);
- de-novo P4 by newly covered turns: 2 games (`m061`/0, `m082`/1);
- command errors: zero in both arms;
- blocking games: 119 floor to 58 candidate;
- violation instances: 289 floor to 115 candidate.

`m106`/0 is an episode-splitting artifact under the count metric, but this ambiguity
cannot change the verdict: both readings contain genuine de-novo P4, and both contain
the same genuine de-novo D-1. `m082`/1 adds 184 D-1 turns and 185 P4 turns while its
score falls 12 to 1. `m061`/0 adds 61 P4 turns while its score rises 48 to 75. The
aggregate improvement is real but is not the charter's zero-de-novo gate.

### G3 — PASS

- Candidate warm p95 reproduced at 0.065 ms against a 50 ms budget.
- The one-process and eight-process panels were row-identical across 240/240 rows,
  SHA-256 `09ab624d...`.
- The negative control distinguished the floor run.

Rebuilt panel artifacts differed from the pinned copies only in wall-clock duration;
the semantic rows and reported gate figures reproduced.

## Rulings on the pending questions

1. The initial authorization question was superseded by the published owner charter.
2. G1 over-delivery does not satisfy the literal frozen prediction clause. Accepting it
   requires an explicit charter-owner ruling, not a reviewer reinterpretation.
3. Episode count versus added-turn coverage should both remain published. The metric
   ambiguity is immaterial for this candidate because G2 fails under both.
4. G5 submission is prohibited while G1.3 and G2 remain red. The reviewer does not
   waive either gate or average the genuine regressions against the aggregate benefit.

No resident mutation or Arena action is authorized by this review.
