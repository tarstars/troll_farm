# Cure α re-graded with the two-clause test — G-1 instrument + G-2 table

Card `20260822-alpha-progress-regrade`, owner-approved 2026-08-22. Work owner `claude_1`,
reviewer `codex_1` (instrument-first), integrator `local_claude_1`.

**Read G-1 first.** G-1 is the adapter and its controls; the G-2 numbers below it are not a
finding until the adapter is ruled on. They are printed together only because they came out of
one run, and the one place the instrument departs from the accepted one is named in G-1 §3
rather than left to be discovered.

---

## STEP 0 — the price, answered: NO RE-RUN IS NEEDED

The card required this before anything was built.

**The panel run's traces were retained.** Both packets of the 2026-08-21 rev-2 run survive as
scratch:

| packet | path | sha256 |
|---|---|---|
| candidate | `/tmp/claude-1000/swap-g2/games/games.jsonl.gz` | `cb14ef2c566184f20d5739fe0f66eb34e65c0eb4810e415ffa5b1eed8bea68a1` |
| floor | `/tmp/claude-1000/swap-g2-floor/games/games.jsonl.gz` | `3678412ecabcd5139c6c9b87fe5dded6dd3dbe3fefa64d8d786f7c1476b00c46` |

They are proven to be **that** run and not some other one: re-running the accepted
`claude_1/swap1/g2_grade.py` over them reproduces the published
`claude_1/swap1/g2-panel-rev2-2026-08-21.json` **byte-identically** — same 27→9, same 16→0, same
30 changed games, same P3 explanation. Gate M is re-run inside this re-grade too, and passes on
all 240 games.

**Named cost, since these are scratch files.** `/tmp` does not survive a reboot, and the bulk
roots are unavailable today (`python3 cgauto/check_external_storage.py --intent read` → `FAIL`,
exit 2), so the packets cannot be archived. Both sha256 are therefore pinned in
`claude_1/regrade3/alpha-progress-regrade-2026-08-22.json`, and the rebuild command is the one in
`claude_1/swap1/g2-report-rev2-2026-08-21.md` (~15 s wall per arm). If the packets are lost, a
re-run can be **proven** identical rather than assumed.

**On "20 games".** The card says 210 of 240 are byte-identical, so 20 games can differ. Both
numbers are right and they count different things: **30** games have a command stream that
differs from the base (240 − 210), and of those exactly **20** carry a base D-1 episode or P4
violation, so 20 is the re-grade surface. The 210 unchanged games are not re-graded; they are
used once, as control C4.

---

## G-1 — the instrument

`claude_1/regrade3/panel_progress_adapter.py` (the adapter)
`claude_1/regrade3/panel_adapter_controls.py` → `panel-adapter-controls-2026-08-22.json`

### 1. The predicate is not copied — it is imported

The adapter does not define `grade`. It imports `claude_1/t1/fixture_harness.py` and calls
`fixture_harness.grade(...)`. There is no second copy, so there is nothing that can drift. C1
pins it anyway: the harness file's sha256 and `inspect.getsource` digests of `grade`,
`had_progress`, `left_the_cycle` and `unit_positions`, so an edit to the accepted harness fails
here rather than quietly changing what "progress" means under a published number.

### 2. What the adapter builds

A panel base event → the `sit` shape the predicate consumes. D-1 events come from
`detect_d1` on the base arm's own transcript, field for field. Candidate-side detector inputs are
the candidate arm's D-1 episodes and its own P4 violations; the base P4 column is the **floor
panel's own candidate arm**, where P4 is computed in the full accepted mode with `post_state`
supplied — never the reduced `post_state=None` mode.

### 3. THE ONE SUBSTITUTION, AND IT IS THE REVIEW OBJECT

`grade()` refuses to grade without an identity verdict under
`reproduces_the_recorded_episode`. In the fixture setting that key means *this re-run replays the
recorded episode*, proven by the frozen window's command lines and entry board.

**That question is not askable of a cure arm.** Measured today, not recalled — control C5 ran
`fixture_harness` unmodified against `claude_1/picker2/candidate-cureC-p1p2.rs` on the card's own
four fixtures and got `NOT_REPRODUCIBLE_ON_BASE` **4 of 4**, with reasons like *"14 of 14 frozen
window command lines differ"*. A cure exists to change those lines. Applying that gate here would
reject exactly the twenty games the re-grade exists to measure.

So the adapter supplies the identity question the **card** names instead —
`window_askable()`: does the candidate run reach the window's last turn, and is the unit present
in it? It is passed **into the parameter that gates `grade()`**, which is what keeps
`WINDOW_ABSENT` a third outcome that cannot be folded into either other bucket.

**This is a different question wearing the accepted question's key, and it is stated here rather
than buried.** It is the thing G-1 is being asked to rule on.

### 4. P4 has no unit, and the progress clause does — the composition, flagged loudly

A panel P4 violation reads *"candidate makes no own-inventory/own-cargo progress over turns
42-200"*. It is a statement about the **side**; its detail carries no unit id.
`had_progress(tr, uid, lo, hi)` is unit-scoped.

The adapter therefore grades a P4 event **once per own unit** and composes at the event level:
detector-silent is unit-independent, so the event is HEALED_WITH_PROGRESS iff the detector is
silent **and at least one own unit progressed** — which is P4's own notion, own-side progress.
The composition lives in the adapter; no per-unit verdict is altered.

**Reviewer, this is load-bearing and it is not a formality: the composition changed the answer on
all 16 P4 events.** In every one, exactly one of the two own units progressed and the other did
not. Under the OR the P4 half of α's headline is 16/16 real; under an AND it would be 0/16. The
whole P4 result rests on reading P4's window as side-scoped, which is how P4 itself is worded.
Per-unit rows are kept in the JSON so this can be recomputed rather than trusted.

For a P4 event the frozen "cycle cells" do not exist; the adapter supplies the cells the unit
occupied in the window **in the base run**. `left_cycle` is a reported diagnostic only — codex_1's
accepted finding 1 of 2026-08-16 removed it from the verdict — so this cannot move a bucket.

### 5. Controls — all five PASS, and each can fail

| control | what it proves | result |
|---|---|---|
| C1 | predicate imported from the accepted harness, source digests pinned | PASS — file sha256 matches pin, all four function sources match, `A.fh.grade is fh.grade`, adapter defines no `grade` |
| C2 | `grade(..., identity=None)` refuses | PASS — raises |
| C3 | `WINDOW_ABSENT` is reachable and its own outcome | PASS — a window past the candidate horizon and a window whose unit is absent both bucket `WINDOW_ABSENT`, not `QUIET_BUT_STALLED` |
| C4 | the detector clause is **live**, not vacuously silent | PASS — all **43** base events of all **240** games, graded against the **base** arm, come back `STILL_FIRING`, 0 offenders |
| C5 | fires **both ways** on the card's named cases | PASS — OSC-004/013/017 → `QUIET_BUT_STALLED`, OSC-034 → `HEALED_WITH_PROGRESS`, reproducing the ruled outcome; and the fixture gate refuses the cure arm 4/4 (§3) |

C4's 43 = 27 D-1 + 16 P4, which is α's base column exactly. C5 is the control the card asked
for, staged through the adapter's identity question because the fixture gate cannot host it.

---

## G-2 — the answer

### The per-event table

Every base event of the 20 event-carrying changed games, each in exactly one bucket.

| game | shape | window | unit | bucket | detector silent | progress |
|---|---|---|---|---|---|---|
| m004 s0 | D-1 | 24-31 | 2 | **STILL_FIRING** | False | False |
| m004 s0 | D-1 | 52-200 | 0 | HEALED_WITH_PROGRESS | True | True |
| m004 s0 | P4 | 42-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m012 s1 | D-1 | 12-32 | 0 | HEALED_WITH_PROGRESS | True | True |
| m014 s1 | D-1 | 7-200 | 2 | HEALED_WITH_PROGRESS | True | True |
| m014 s1 | P4 | 5-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m021 s0 | D-1 | 27-200 | 0 | HEALED_WITH_PROGRESS | True | True |
| m021 s0 | P4 | 22-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m028 s1 | D-1 | 26-32 | 0 | **QUIET_BUT_STALLED** | True | False |
| m039 s1 | D-1 | 32-200 | 0 | HEALED_WITH_PROGRESS | True | True |
| m039 s1 | P4 | 26-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m040 s0 | D-1 | 176-200 | 0 | **QUIET_BUT_STALLED** | True | False |
| m046 s0 | D-1 | 14-200 | 2 | HEALED_WITH_PROGRESS | True | True |
| m046 s0 | P4 | 11-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m058 s1 | D-1 | 29-42 | 0 | HEALED_WITH_PROGRESS | True | True |
| m059 s0 | P4 | 11-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m059 s1 | D-1 | 12-200 | 2 | HEALED_WITH_PROGRESS | True | True |
| m059 s1 | P4 | 11-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m061 s0 | D-1 | 2-9 | 2 | **STILL_FIRING** | False | False |
| m061 s0 | P4 | 39-99 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m063 s1 | D-1 | 50-200 | 2 | HEALED_WITH_PROGRESS | True | True |
| m063 s1 | P4 | 47-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m070 s1 | D-1 | 7-18 | 2 | **STILL_FIRING** | False | False |
| m070 s1 | D-1 | 52-200 | 0 | HEALED_WITH_PROGRESS | True | True |
| m070 s1 | P4 | 44-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m073 s0 | D-1 | 5-69 | 0 | HEALED_WITH_PROGRESS | True | True |
| m073 s0 | P4 | 5-68 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m079 s0 | D-1 | 38-200 | 2 | HEALED_WITH_PROGRESS | True | True |
| m079 s0 | P4 | 33-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m082 s1 | D-1 | 17-200 | 2 | HEALED_WITH_PROGRESS | True | True |
| m082 s1 | P4 | 16-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m084 s1 | D-1 | 32-200 | 0 | HEALED_WITH_PROGRESS | True | True |
| m084 s1 | P4 | 26-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m099 s1 | D-1 | 8-200 | 0 | HEALED_WITH_PROGRESS | True | True |
| m099 s1 | P4 | 8-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |
| m110 s1 | D-1 | 6-200 | 0 | HEALED_WITH_PROGRESS | True | True |
| m110 s1 | P4 | 1-200 | side (0,2) | HEALED_WITH_PROGRESS | True | True |

### The headline, restated

| shape | base | α's old headline | HEALED_WITH_PROGRESS | QUIET_BUT_STALLED | WINDOW_ABSENT | STILL_FIRING |
|---|---|---|---|---|---|---|
| D-1 | 27 | healed 18, new 0 | **16** | **2** | **0** | 3 (+6 in unchanged games) |
| P4 | 16 | healed 16, new 0 | **16** | **0** | **0** | 0 |
| **total** | **43** | **healed 34** | **32** | **2** | **0** | 3 |

Three reconciliations, so the table can be checked rather than believed:

- **The detector-silent count reproduces the headline exactly.** 18 D-1 events and 16 P4 events
  are detector-silent under α — the same 18 and 16 the count-subtraction produced, arrived at by
  grading each event's own window instead of subtracting two totals.
- **`new = 0` holds.** 27 base D-1 = 21 in changed games + 6 in unchanged; the candidate's 9
  episodes = those 6 + the 3 still firing. No candidate episode is unaccounted for.
- **WINDOW_ABSENT is 0, and that is a measurement, not an absence of one.** C3 shows the bucket is
  reachable; it simply never fired, because α is a transport change that does not shorten games or
  remove units.

### The two that come off the headline

| event | cells | why |
|---|---|---|
| `m028/s1/D-1@26-32/u0` | `[7,4] [8,4]` | detector silent, **no progress event in the window**; `left_cycle` True — the unit reached a third cell, which is exactly the three-cell no-progress loop codex_1's accepted finding 1 removed from the verdict |
| `m040/s0/D-1@176-200/u0` | `[2,4] [3,4]` | same shape, at the end of the game |

Both are the P1+P2 outcome: *benched → 0 does not mean working.*

### Against the amended G-2 bar

The card's ruling amends "healed − new must be positive" to mean **healed with progress**. On that
bar: **32 − 0 = +32, positive.** α clears the amended bar. This delivery states that arithmetic; it
does not declare G-2 passed — that is the integrator's, and the other G-2 clauses and the three
open questions on `20260821-swap-r1-cure` are untouched here.

### For the owner, in plain words

We asked whether cure α's numbers were the alarm going quiet or the troll going back to work. We
re-checked all thirty-four events one at a time with the stricter test we already owned — the one
that caught the last cure — and **thirty-two of the thirty-four are real work restored.** Two are
the failure we were hunting for: the alarm stopped, the unit still did nothing. So α is not the
flattered cure P1+P2 turned out to be; its headline was about 94% honest, and it is now 32 rather
than 34.

One caution, and it is the reason a reviewer is reading this before you act on it. Sixteen of the
thirty-two rest on a judgement I had to make and could not inherit: the P4 alarm is about the
whole side, and the progress test we own is about one troll. I read "the side made progress" as
"at least one troll made progress", because that is how P4 itself is written — but on every one of
those sixteen, one troll worked and the other did not. Read the stricter way, that half of the
result would be zero instead of sixteen. `codex_1` is being asked to rule on exactly that, and
the D-1 half — 16 of 18 — does not depend on it either way.

## What this delivery does NOT claim

- Not a G-2 pass, not a G-3 or G-4 qualification, and no Arena action.
- No candidate edit, no new cure, no widening, and no change to the accepted predicate.
- No re-ruling of any case, and nothing about the residual 13, P3 applicability, or the cure-arm
  basket criterion — those remain owed elsewhere.
- Nothing about `chatgpt_1`'s position document, which is still unpublished and is not cited.

## Reproduce

```
python3 claude_1/regrade3/panel_adapter_controls.py     # G-1, five controls
python3 claude_1/regrade3/panel_regrade.py              # G-2, the table
```
