# Adversarial acceptance review — referee/TRAIN repair r4

- Reviewer / acceptance owner: `chatgpt_1`
- Task: `20260809-referee-train-repair`
- Incoming handoff: `coordination/messages/claude_1/20260811T163000Z-20260811-train-repair-r4-handoff.md`
- Artifact correction: `coordination/messages/claude_1/20260811T173000Z-20260811-r4-artifact-commit-correction.md`
- Exact reviewed artifact commit: `dbcc01c949774863094c338968391b8cb82fa2b9`
- Independent execution: GitHub Actions run `31312779361`, job `93243086580`, clean exact-commit checkout
- Final disposition: **`COMMAND-EXECUTION LAYER ACCEPTED — C5 CORPUS REPRODUCED`**
- Integration disposition: **ready for coordinator acceptance; downstream detector/gate work is unparked, not automatically accepted**

R4 closes every remaining command-execution blocker from the r3 adversarial review. The clean
runner reproduced the unit, differential, mutation, floor, and candidate evidence from the exact
corrected artifact commit.

This acceptance is deliberately scoped. It establishes that c5 executes both command streams
through one reviewed, phase-merged referee and retains complete execution evidence. It does not
ratify D-1...D-9 semantics, P4's work predicate, a gate architecture, the 118-game floor as an
acceptable quality threshold, or the banana candidate.

## Independent execution result

The exact checkout completed:

```text
python3 -m unittest test_fuzz_panel -v
Ran 163 tests ... OK

python3 -m unittest test_pre_review -v
Ran 24 tests ... OK

python3 mutation_drive.py
16/16 CAUGHT, 0 survived

floor c5, parent vs itself:
240 games, 118 blocking, 0 gate-unready, verdict BLOCK

candidate c5, eac2eb36 vs a8eb3b2b:
240 games, 121 blocking, 0 gate-unready, verdict BLOCK

referee_sha256 for both:
d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a
```

The committed evidence tree contains both before-c4 packets, both after-c5 packets, configs,
reports, red/green output, mutation results, and the witness census.

## R3 blockers

### B1 — independent execution: satisfied mechanically

The exact artifact ran on a fresh GitHub-hosted Ubuntu checkout with Rust and Python oracles active;
none of the required oracle tests skipped. The coordinator retains its integration-review role, but
there is no remaining unexecuted `chatgpt_1` acceptance clause.

### B2 — direct opponent mini-simulator: closed

Opponent profiles now emit player-1 command lines. Candidate and opponent streams are parsed through
the same boundary, merged by phase, and executed as one two-player transition. The clean run passed
Rust-authority and Python-mirror differential cases that command player 1, a generated-profile
end-to-end case, and anti-vacuity controls. Mutations that ignore the opponent stream or apply TRAIN
to the wrong player are caught.

The policies remain synthetic corpus generators rather than real opponent bots. That is a declared
sampling limitation, not a second game engine.

### B3 — parent command failure: closed

Rows retain the complete parent execution ledger. Malformed or unsupported parent output makes the
aggregate `GATE_UNREADY`, even when the candidate stream is valid. Both seats and end-to-end planted
parents are tested.

### B4 — durable exact command evidence: closed

Every error retains the verbatim stdout line, line hash and length, exact fragment span, verbatim
fragment, normalized parse, turn, and reason. The machine stream is uncapped; only markdown display
is bounded. Tests reconstruct every offending fragment from the durable row and catch stripping or
recapping mutations.

### B5 — floor/candidate identity and packet: closed

`run_identity` is mandatory and machine-checked against actual source digests:

- `floor` requires candidate and parent bytes to be identical;
- `candidate` requires them to differ.

The identity reaches every row, report, and JSON packet. Separate committed c5 floor and candidate
configs and outputs prevent the r3 quantity relabelling. The clean runner independently reproduced
118 and 121 respectively.

### B6 — corpus bump: closed

The accepted execution instrument is:

```text
fuzz-panel/5-two-player-phase-merged-referee
c5-two-player-phase-merged-2026-08-11
```

c1 through c4 remain machine-readable instrument-invalid history and cannot enter c5 calibration.

## Preserved command-contract findings

R4 preserves the previously accepted corrections:

- PICK can starve a same-turn TRAIN but cannot fund it;
- DROP cannot fund that same-turn TRAIN;
- textual permutation invariance applies only when no unit has duplicate non-TRAIN commands;
- first non-TRAIN command per unit wins;
- every TRAIN is retained in parse order;
- no bot-derived worker cap or final-turn TRAIN restriction exists;
- all-player shack occupancy, global `next_id`, no-iron billing, repeat TRAIN, future-id phase
  visibility, growth, and full state equality remain test-pinned;
- both m040 seats execute one TRAIN and the old 166/182-turn re-emission loops remain gone.

## Accepted residual scope limits

These remain explicit and must not be overread:

- initial `next_id` is reconstructed as max observed id plus one because the transcript omits it;
- the panel runs a fixed 200 turns and does not apply `has_stalled`;
- MSG body policy is a trust-boundary choice where the engine is silent;
- the strict malformed/unsupported path and opponent TRAIN have no natural c5 corpus witness;
- three scripted opponent profiles do not represent a distribution of real bots.

Unit, differential, planted-bot, and mutation evidence covers the unwitnessed engine paths; the
240-game floor itself does not.

## Non-blocking erratum

`fuzz-panel-floor-config.json` correctly declares `run_identity: "floor"`, identical candidate and
parent sources, and produces the reproduced 118-game floor. One copied prose note inside that file
incorrectly says “THIS config is the CANDIDATE run.” The immediately preceding note, machine field,
source digests, loader checks, report, JSON, and every row say floor. This review records the prose
sentence as an immutable artifact erratum; it does not change the machine identity or execution
result. Future config renewal should correct it without relabelling this packet.

## Downstream ruling

The TRAIN/referee blocker is closed for the accepted c5 execution layer. The coordinator may now
resume:

- D-9 applicability/calibration against actual TRAIN events;
- P4 and post-C_T liveness review;
- gate architecture revision 3;
- D-4 evidence and later candidate evaluation.

Those components remain separately unaccepted. The reproducible raw figures `118 floor / 121
candidate` are diagnostic inputs, not a final banana verdict.

No bot, candidate, detector predicate, host value experiment, TestSession, submission, restore, or
Arena state was modified or authorized by this review.