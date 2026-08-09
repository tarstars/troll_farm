# claude_1 Status

- Updated UTC: 2026-08-12T17:00:00Z
- State: inbox clean (sweep exit 0, 0 unacknowledged); tooling repaired; awaiting revision work on four dispositions
- Role: contributor + **execution reviewer** on every artifact (coordinator, integrator, arena controller AND detector-semantics owner = `local_claude_1`; `chatgpt_1` = adversarial/committed-blob reviewer; `chatgpt_2` = read-only sync-architecture reviewer, new)
- Branch: agent/claude_1-banana-restoration-r2; canonical agent/claude_1 at `fd05fbb5`
- **Read `claude_1/SESSION-FINDINGS-2026-08-07-to-11.md` before acting.** It carries the programme state, the measured findings, and the error patterns. It predates the 08-12 unblock below.

## Blocking state

- **The TRAIN/referee blocker is CLEARED.** r4 accepted by `chatgpt_1` for the c5 execution layer; B1 closed by `local_claude_1` through independent execution in a second checkout (7/7 artifact digests, `engine.rs` `7c240abf` untouched, panel 163 OK, pre-review 24 OK, mutation 16/16 caught, and floor packets **row-level `IDENTICAL`** to committed `evidence-r4/` — agreement on *which* games block, not just the total). The r4 panel is merged to `main`: `main:claude_1/pipeline/fuzz_panel.py` = `d8900abf31dd030d…`, 33 TRAIN references. `main` was pre-r4 until 08-12, so anything measured from `main` before then used the broken referee.
- **This does NOT authorize verdicts.** `chatgpt_1` holds I-30 at `GATE_UNREADY / MEASURED_UNTHRESHOLDED` and states plainly: **no detector branch is authorized for candidate acceptance, and no I-30 PASS, FAIL, threshold or candidate verdict is accepted.** Do not read the r4 acceptance as a gate opening.
- Instrument `fuzz-panel/5` · corpus `c5-two-player-phase-merged-2026-08-11`. **Floor (parent vs itself) = 118/240. Candidate run (banana `eac2eb36` vs parent) = 121/240.** Different quantities; `run_identity` is machine-checked. `118/240` is quotable **only** with r4's binding restriction attached: TRAIN is witnessed in 2 games (1 spawn each), and 10 of 17 repaired rules have no corpus witness — those are pinned by unit tests, the two-oracle differential and the mutation drive, never by the floor.

## Open dispositions requiring my revision work

- **M3a correct-subject** — `REVISION_REQUIRED — DATA INTERNALLY CONSISTENT, SOURCE REPLAY NOT PORTABLE`. 34 situations / 46 episodes verify; both replay suites fail on a clean runner because committed configs point at `/home/tarstars/…` and `/tmp/claude-1000/…`. Repair: materialize source from its pinned Git ref into a temp dir, verify SHA, evaluate historical corpus skips before compilation, rerun replay on a fresh checkout. Separately: the c5 46-episode diagnostic library is **not** the same population as the golden v2 record (34 exact D-1 episodes / 32 source games) — the coordinator must select and version the M3b substrate explicitly.
- **Bite-test audit r2** — `HISTORICAL_REPAIRS ACCEPTED — CURRENT REVISION REQUIRED`. Six current/architectural blockers: `LIVE` does not establish legal-game reachability; committed D-3 probe implements only next-cell consistency with `max(speed,1)` and omits the same-player conflict label; D-9 `INSTRUMENT_UNSUPPORTED` rows are stale post-c5 and need the retired proxy separated from now-supported paired branches; `run_mutations.py` returns success on incomplete experiments when the control is green; the 47-branch ledger is hand-maintained; D-5 conformance is expressed on the wrong axis.
- **I-30 rev 3** — `CORE_ACCOUNTING_ACCEPTED — REVISION_REQUIRED AT THE TRUST ROOT`. `ExecutionValidity` validates self-declaration rather than binding a run to a reviewed referee artifact; owner-freeze chronology compares caller-supplied strings against a blob on moving `main`.
- **M2 rev 2** — accepted. **Fast-verification-executor requirements** — review requested.

## Owed, now unparked by r4

M1 Decision Packet implementation (spec frozen against `98628e98`) · M3b adjudication (needs M1 + valid M3a) · P4 re-do on c5 evidence · D-4 repair · gate revision 3 execution review. **With the owner:** the D89a label; whether to fund a fresh 512-row corpus for U4.

## Do not cite

The `+12.453/+76.508` D89a split (`UNRESOLVED`, TSVs never committed) · `oscillation-library/` as M3a (it is parent lineage `a8eb3b2b`) · D-9 as `INAPPLICABLE` or "196 false positives" (now `INSTRUMENT_UNSUPPORTED / GATE_UNREADY`) · D-6 as falsified (it is a `CONTRACT AUTHORITY: CONFLICT`) · any floor figure for the ~10 of 17 rules lacking a corpus witness.

## Transport

**Dual-format MANDATORY** (v2 front matter + legacy `- To:` bullets) — a peer was blind to v2 for ten days. **`ack_for` is inert unless `type: ack`** (I broke this 4x). **Gate publishes on `lint_outbox.py` EXIT STATUS**, not on grepping its output. `pytest` absent — use `python3 -m unittest`. Push before citing: *unpushed is unsent*, and a stale remote-tracking ref makes `git merge` a silent no-op. Never `git add -A` — agents share this tree.

**Tooling is repaired as of `6c7e6650`.** `scripts/lint_outbox.py` had been **absent from this branch entirely** — the publish gate did not exist where I was publishing from, which is the mechanical cause of all three of my quarantined messages. `scripts/inbox_sweep.py` was stale at `12b27e9c…`. Current, matching `main`: `inbox_sweep.py` `0f78bf38…`, `lint_outbox.py` `f3c47b70…`. **Verify your tool digest before trusting a sweep** — the stale copy reported 56 unacknowledged against the current tool's 16 and printed no quarantine section at all, with nothing on screen to signal it was the old one.

**Three of my messages are quarantined** (`20260807T090000Z` non-canonical type, `20260807T113000Z` correction with empty `supersedes`, `20260811T163000Z` handoff pinning a commit lacking two of its own paths). All rejected on transport, not substance; all have verified replacements; no content lost.

**Watermark deliberately NOT advanced.** 141 messages remain `new (unseen)`. Protocol forbids blanket-marking a backlog by timestamp: actionable messages are acknowledged by exact path (done — 16 of 16, sweep exit 0), and the rest need a pushed legacy-backlog audit before `--mark`. That audit is outstanding.

## Standing constraints

Arena controller: **NO**. `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`) byte-untouchable; `engine.rs` (`7c240abf`) is the authority, not any bot's self-restraint. `trace_detectors.py` is `local_claude_1`'s. No CI anywhere.
