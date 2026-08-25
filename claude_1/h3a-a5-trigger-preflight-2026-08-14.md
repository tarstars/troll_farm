# A-5 — H3a exact-17-game trigger preflight

- **Author:** `claude_1`, on the VM · **Date (real UTC):** 2026-08-14
- **Task:** `20260814-iteration-3-work-plan` item **A-5**, resuming
  `coordination/tasks/20260802-h3a-conditioned-value-unblock.md` Phase A2
- **Verdict: PASS — all five gates.** A-6 opens on the coordinator's acceptance.
- Read-only. No candidate, no source change, no Arena action.

## In plain terms

The H3a idea is: *when the bot is under workforce pressure, play differently*. Before building
anything to test whether that helps, we have to check the cheap thing first — **does the pressure
condition actually occur in the archived games where the treatment would need it?** A condition
that never fires cannot be worth conditioning on, and finding that out costs hours instead of days.

It fires. In **9 of 10** disaster games the condition turns true by turn 150, and in **10 of 10**
it turns true *before* the collapse began — so it is early enough to act on, not merely
correlated with the wreckage. In the **7 comparison games the bot won**, it fired **0 times** by
turn 150, so it is not simply always-on. And in **9 of 10** disasters there was a real move
available afterwards that the treatment would have scored differently.

**One thing I had to fix before I could report any of this**, covered below: the fifth gate — the
one that checks the input data is what it claims to be — was named in the analyzer's own
documentation and had never been written.

## Input reachability — checked first, as instructed

The coordinator's queue said *"mind the input reachability check first"*, after `codex_1`'s F1
work blocked on an unmounted volume. **A-5 is not storage-blocked:** all six inputs are committed
in-repo and every one hash-matches the value frozen in the task record.

| input | frozen sha256 (16) | on disk |
|---|---|---|
| `…state-package….maps.jsonl.gz` | `decfa8f49580a0fb` | match |
| `…state-package….decisions.jsonl.gz` | `a60cbf05a81fecd3` | match |
| `…state-package….manifest.json` | `4336ce47a1529c47` | match |
| `…preflight-package….games.jsonl.gz` | `e3029c7e506e3da2` | match |
| `…preflight-package….manifest.json` | `f3b28d735fe69a5b` | match |
| `…shared-2026-08-02.sides.csv` | `e4e4923446b6449d` | match |

## Gates 1–4 — re-run, not cited

A prior result JSON existed from 2026-08-10. I re-ran the pinned analyzer rather than quoting it,
because a committed number is not evidence that the number still reproduces. **The re-run is
byte-identical to the committed result.**

| gate | requirement | result | |
|---|---|---|---|
| 1 | predicate true by turn 150 in ≥8/10 catastrophes | **9 / 10** | PASS |
| 2 | first true turn precedes the collapse interval in ≥8/10 | **10 / 10** | PASS |
| 3 | false-positive activation by turn 150 in ≤20% of 7 matched wins | **0 / 7** | PASS |
| 4 | ≥1 exact ETA-6-eligible treatment-scoring decision after activation, in ≥6/10 | **9 / 10** | PASS |

**Two boundary facts worth stating rather than leaving implicit**, because both are places where a
looser reading would have improved the result:

- The single gate-1 miss is game `897782213`, which activates at turn **169** — after the
  150-turn line. It still counts for gate 2 (169 precedes its collapse at 200), which is why gate 2
  reads 10/10 while gate 1 reads 9/10. The two gates measure different things and I have not
  merged them.
- Matched win `897781674` activates at turn **169**. Gate 3 is scoped to *by turn 150*, so it is
  not a false positive under the gate as written. Under an unscoped reading it would be 1 of 7 —
  still inside the 20% allowance, so the verdict does not depend on the scoping, but the number
  does and I am not quoting 0/7 without saying so.

## Gate 5 — it was claimed and had never been implemented

`claude_1/h3a-conditioned-value-unblock-preflight.py` says in its own docstring that it evaluates
*"the four pinned Phase-A2 gates **plus the integrity gate**"*. It assigns `gate1`…`gate4` and
computes no fifth. **A gate named in the documentation, absent from the code, and therefore
incapable of failing** — the same shape the guards work spent a week removing from the detector
audit.

Implemented at `claude_1/h3a-preflight-integrity-gate.py`. Gate 5 asks whether the preflight's
*inputs* are what they claim; it recomputes none of the preflight:

| check | result |
|---|---|
| all 6 inputs hash-match the task record's frozen values | PASS |
| cohort identities are exactly the 10 + 7 named games | PASS |
| counts: 17 games, 5,100 decision rows — manifest, its validation block, and the decompressed file all agree | PASS |
| per-game row counts match the manifest for all 17 | PASS |
| ETA semantics: analyzer pins threshold 6; frozen reconstruction record agrees | PASS |
| package asserts `exact_ids_only` and no sealed data | PASS |
| the locked resident is the sacred source `fff6669b…` | PASS |

**Every check was observed failing before it was trusted.** `--self-test` sabotages each of the
seven in turn and requires the gate to fail each time; all seven do. A gate that passes on the
real data proves nothing until you have watched it reject something.

Note the check compares on-disk bytes to **the task record's** frozen hashes, not to the
manifest's own. A manifest can be perfectly self-consistent while describing different data; only
an external anchor catches substitution.

## What this verdict does and does not license

**PASS means the trigger preflight cleared — nothing more.** Specifically it does **not**
establish that conditioning on the trigger has value; that is what A-6's three-arm comparison
would measure, and it is exactly the question the preflight exists to make affordable.

Carried forward unchanged from the task record, since a PASS is when these get forgotten:

- The state package is a **causal public-outcome-anchored reconstruction, not an independent
  continued-RNG replay.** Admissible for this retrospective coverage audit; **forbidden for the
  Phase-C value panel**.
- The Phase-B/C substrate blockers stand and are A-6's first scope, not A-5's finding: 213
  accepted numeric fruit aliases crash the locked substrate, continued-RNG diverges, and the
  platform-legal empty `MSG ;` cannot be replayed natively.
- 232 WAIT-canonicalized no-landing moves and referee-derived tree dynamics remain disclosed
  residual risks.
- Any future value claim needs **5 runs per arm at σ = 1.501**.

## Verification

Analyzer re-run byte-identical to the committed 2026-08-10 result; gate 5 self-test 7/7 able to
fail, then 7/7 passing on real data; no source, candidate, corpus or Arena state touched.

**I authored this and review none of it.**
