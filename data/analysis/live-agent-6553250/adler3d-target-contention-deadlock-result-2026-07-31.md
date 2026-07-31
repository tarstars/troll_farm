# Adler3D target-contention deadlock and sticky-bank correction

Date: 2026-07-31
Task: `20260731-adler3d-target-contention-deadlock`
Verdict: **exact inherited deadlock; sticky productive-bank successor locally validated**

## Exact game

- Game `897552551`.
- Resident agent/submission `6585739`/`41070944`, seat 1, valid 97–99 loss.
- Adler3D agent/submission `6481971`/`40751095`, seat 0.
- Official reconstruction: 300/300 turns, zero unknown diff updates.
- Raw replay SHA-256:
  `d17832e1427c40e0870a8c5df478b0694016584e6d8d021e42e942f5c7dac5c3`.
- Trajectory SHA-256:
  `7024f7f8ebdc772d7e8d901652fd0ecee4fa8f756dbfe14d2e39834dc8689768`.

## Failure

The productive adjacent-tree worker, unit 1, removes the target on turn 39 and begins
turn 40 with one wood. The qualifying-tree trigger has disappeared, so the existing
coordination layer forgets the productive bank role and ordinary far-denial scoring may
retarget the carrier.

The visible terminal trap is exact:

- unit 1 emits `WAIT` on turns 50–91: 42 consecutive decisions at `(10,4)`, full with
  one wood;
- unit 2 emits 41 alternating MOVE commands on turns 51–91 and occupies alternating
  decision states `(9,4)` / `(8,4)` from turns 51–92, full with three wood;
- the selector sees equal-score pairs `CHOP 1 + WAIT` and
  `WAIT + MOVE 2 10 4`, each totaling 90;
- first-equal retention chooses the latter, and collision avoidance repeatedly detours
  unit 2 because unit 1 occupies the shared tree.

The exact far-denial-d3 parent reproduces the stuck interval. The submitted
tent-proximity artifact reproduces all 300 recorded commands with zero stderr. The
failure is therefore inherited, though the new coordination layer exposes the missing
productive-role state.

## Owner-corrected patch

The owner froze the invariant:

> trolls with wood, when decided to bring wood to tent, should do it

The successor records the productive one-or-two-band worker in
`bank_commitment_units`. Once that worker has cargo, every later command uses the
existing banking path until `DROP` succeeds or cargo is empty. Trigger disappearance and
higher-scoring denial targets cannot cancel the commitment. The planted-tree non-banking
worker, >2 full-denial workers, global selector, score/tie order, and movement resolver
are unchanged.

Candidate:
`cgauto/submissions/candidate-agent6585739-owner-tent-banker-commitment-slim.min.rs`,
68,464 bytes, SHA-256
`f26e3781e972006cb2698420bba3474f1a038708225beeb562f3ab2242593e4a`.

## Validation

- Three compiled sticky-bank regressions pass: commitment survives trigger loss, remains
  bankward through multiple turns and exact `DROP`, then releases; a zero-trigger state
  without prior commitment is exact-parent behavior.
- All five original tent-proximity compiled boundaries still pass.
- On the exact 300-state Adler3D teacher-forced stream, active parent output matches all
  recorded commands. The successor first diverges on turn 48. At turn 50 it emits
  `MOVE 1 10 3` instead of `WAIT`, reducing distance to the own bank. This is mechanism
  evidence only, not a closed-loop outcome claim.
- Eight unsealed cells (seeds 1300–1303, both seats versus fixed `ringfix3`) terminate
  with zero stderr.
- Sacred source SHA remains exact:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Disposition

The candidate is locally ready for review, but no Arena action is authorized. The
tent-proximity trial failed independently at score 11.96 and exact-source restoration
`6585755`/`41071034` is the sole in-flight Arena leg. The sticky-bank successor remains
an unsubmitted incident fix until restoration is terminal and a distinct decision is
serialized.
