# HANDOVER 2026-08-10 — `local_claude_1` session close

Written for a context flush. Everything here is verified state, not intention. Where something is
half-done it says so and gives the exact next command.

## ★★★ ONE ACTION IS HALF-DONE — READ FIRST

**A quarantine is adjudicated but not entered.** I published an invalid handoff, then began
quarantining it and was interrupted between the two required steps.

| step | state |
|---|---|
| invalid message published | `coordination/messages/local_claude_1/20260810T080000Z-20260807-transport-quarantine-and-outbox-lint-handoff.md`, blob `16a301ee` |
| valid replacement published | `…20260810T081500Z-…-correction.md` — same content, `artifact_ref: agent/local_claude_1`, `artifact_commit 74dc6f4b` |
| adjudication published | `…20260810T090000Z-20260807-transport-quarantine-self-adjudication-policy.md`, carries the required `quarantines:` array ✅ |
| **quarantine entry added** | ❌ **NOT DONE** — `coordination/quarantine.json` has **9** entries, needs a 10th |

**Consequence right now:** `delivery errors (1)` in both `claude_1`'s and `codex_1`'s sweeps.
Harmless but permanent until the entry lands.

**To finish:** append an entry to `coordination/quarantine.json` on `agent/local_claude_1` with
`path` = the handoff above, `target_blob` = `16a301eeb4f2a697a4b93bd824871af1ae1a4574`,
`adjudicated_by` = the `20260810T090000Z` policy, and a reason. Then verify
`quarantined (10)`, `quarantine errors (0)`, `delivery errors (0)` for both peers.

**A prior attempt failed and broke things — do not repeat it.** I first cited the *correction* as
`adjudicated_by`. A `correction` carries `supersedes`, not `quarantines`, so the sweep rejected the
entry — and per transport rule 7 a malformed quarantine file **suppresses nothing**, which
disabled all nine existing quarantines (`quarantined 9 → 0`, `claude_1` delivery errors `1 → 8`)
until I reverted. The `adjudicated_by` message **must itself declare the path in a `quarantines:`
array.** The `20260810T090000Z` policy does.

**Conflict of interest, unresolved:** this is the coordinator quarantining his own message under
sole quarantine authority, on the task where that authority is the declared conflict. Both peers
were told they may demand the entry's removal and it comes out.

## Arena — no action pending

- Resident **`6604529` / `41113243`**, source `98628e98…`
  (`cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`).
- Settled **22.46 / rank 35 of 139**, 160 games, `identity_clean=True`, `signals=0`. Re-verified
  unchanged nine hours later. **Owner ruled KEEP.**
- Cycle closed. Nothing in flight. Sacred source `fff6669b` intact.

## Owner rulings this session — all four are binding

1. **Noise-band gate REMOVED** (`STATE` §3). *"We shouldn't gate candidates. This way we starve
   our channel."* The QUALIFIED-verdict correctness bar stands; the magnitude bar is gone.
2. **KEEP `readable__no_orchard`.**
3. **STRICT: no banana manipulation before the second troll is trained** (`CONSTRAINTS` §h).
   Threshold 0, no exemption, marked "for now". This is D-9 branch (a) `banana_before_train`.
4. **Rework the label system for consistency** → done, `CONSTRAINTS` §h "LABEL DISCIPLINE".

## Measurements established

- **σ = 1.098** score points, CI [0.707, 2.418], 4 families / **10 deployments** / 6 d.o.f.
  Tool: `cgauto/arena_noise_band.py`. Difference SD at one run per arm = **1.552**, so a +1.5
  effect is invisible at n=1; SE 0.5 needs 10 runs per arm (~40 h).
  *Corrected from my own first figure of 0.957, which counted 13 observation rows including three
  second-checkpoints of a single run — a unit error in the tool written to quantify unit errors.*
- **Re-submission draws an independent sample** — 10 distinct deployments of 4 byte-identical
  sources, **zero duplicate scores**. Answered from committed data at zero Arena cost.
- **A mature 160-game read takes ~2 hours**, not days. B0.3's "days of standing" is a fossil of
  the frozen-score regime; weakened in `STATE` §3 on measured grounds.
- **Corpus: 14,930 games / 582 agents / 279 names, 0 parse failures.** Raw and parsed agree
  exactly; the old 10,470 figure was stale because the cron rewrites `stats.json` uncommitted.

## Work completed and verified

- **Bite-test blockers 1, 2, 4, 5, 6 closed**; **3 substantially unblocked** by owner rule 3.
  D-9 paired branches (b)(c)(d) still need recalibration — they are **live in the production panel
  and untested by the bite-test harness**, which is worse than their stale
  `INSTRUMENT_UNSUPPORTED` label suggests.
- **Gate-architecture review integrated** (`codex_1`, `REVISION_REQUIRED`, 5 findings). F2 is the
  substantive one: per-map `delta <= 0` permits **within-cell episode substitution**, so it is not
  a no-new-failure rule; needs a signature-subset rule.
- **M3a replicated** (`codex_1`): population reproduces exactly (32/34/19/20) but **both blocker
  claims are UNRESOLVED** from permitted evidence. `claude_1` then published a regeneration recipe
  (`1aae7ca2`) — verified structurally, **not executed**. Status: derivable at the cost of one
  panel run.
- **Transport**: `ack_for` honoured on every kind; guarded parse; unexpected failure exits **2**
  not 1; `tool_drift()` warns when the sweep is itself stale. 96 tests. Two reviews received;
  `codex_1`'s RQ-1..RQ-3 addressed at `74dc6f4b`, **focused re-review requested, not yet returned.**
- **D176a artifacts committed** — its closure was cited 7× in `CONSTRAINTS` while the code that
  produced it sat untracked for twelve days, i.e. unfalsifiable in practice.
- **Eight `claude_1` messages discharged** that I had answered but never acked (three of my own
  rulings carried `ack_for: []`).

## Open — needs the owner

1. **G6**: build fixtures for the **22 of 47 detector branches that have none**. Needs go-ahead;
   real work, no score attached.
2. **Spend a panel run** to settle the idle-blocker claim? The oscillation repair plan leans on it.
3. **σ task** (`20260810-arena-noise-band-measurement`): unowned. Q1 answered; Q2–Q4 open —
   churn cost, how many runs, era normalisation. **Blocked ordering cannot separate our variance
   from ladder drift; only interleaved A/B/A/B can.**
4. **The gate's reference bot fails its own gate** — parent judged against itself BLOCKS 118/240,
   D-1 = 35, D-4 = 6. Owner rule 3's D-1/D-4 strict-zero requires repairing the parent lineage
   first; this is the size of that repair.
5. **M1 spec, M2 second adversarial review, M3b adjudicator** — unowned; neither peer can take
   them without becoming author and checker both.

## Live tasks and owners

| task | owner | state |
|---|---|---|
| `20260810-guards-that-cannot-fail` | G1 `codex_1`, G2 `claude_1`, G5 me, G6 gated | **new, P0** |
| `20260807-transport-quarantine-and-outbox-lint` | me | re-review pending from `codex_1` |
| `20260810-arena-noise-band-measurement` | unassigned | proposed |
| `20260802-h3a-conditioned-value-unblock` | `claude_1` work, `codex_1` review | active — sole surviving ranked route |
| `20260810-manifest-implementation` | M3a done; M1/M2/M3b vacant | open |

Roster: `local_claude_1` coordinator + sole Arena controller · `claude_1`, `codex_1` active ·
`local_codex_1` dormant since 2026-08-06 · `chatgpt_1`, `chatgpt_2` unreachable.
**`codex_1` ≠ `local_codex_1`** — different agents; I conflated them once and reassigned ten slots
to the wrong one.

## The failure pattern this session, recorded because it recurred

**A claim true of one artifact, asserted of another.** Roughly nine instances, most of them mine:
records committed but unpushed while described as live; a roster fix pushed to a ref its reader
does not consult; peer reviews declared missing that had been delivered; a completed task marked
incomplete; `api_submit.py`'s stale default reported as the wrong hash; a naive scan reporting 83
vacuous tests against a true 6; hashing a nonexistent path and getting the empty-string SHA twice;
and grepping absolute paths out of a comment that merely described them.

Two standing rules now exist against it (`CONSTRAINTS` §h): **every published count names its
unit**, and **every label names its axis and evidence class**. A third is in the new task:
**a test is not finished until it has been observed failing.**

**The sharpest instance:** I ran `lint_outbox | tail -3 && commit && push` all session. A pipeline
exits with `tail`'s status, so `&&` never gated on the lint. It printed `errors (1)` and the push
proceeded — that is how the invalid handoff above got published. **Always run the lint as its own
command and check `$?` before committing.**
