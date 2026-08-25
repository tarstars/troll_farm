# Cure C — implementation plan ("fix the first door")

- Author: `claude_1` (named implementer). Written **2026-08-17**, after pool #5 closed.
- Basis: owner preference recorded `local_claude_1/20260817T190221Z`; brief
  `local_claude_1/session-inputs/cure-candidate-C-brief-2026-08-17.md`; mechanism
  `claude_1/hstarve1/mechanism-note-pool5-2026-08-17.md` (codex_1 GATE_ACCEPTED).
- Subject: `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`,
  sha256 `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`.

> **STATUS (superseded 2026-08-18): PLAN EXECUTED. See §6.**
> As written on 2026-08-17 this was **plan only** — codex_1 `20260817T203000Z` and the integrator
> `20260817T190221Z` both held that candidate C was an **owner preference, not a ruling**, and that
> no cure code, resident mutation, Arena action or spec implementation was authorized. The owner
> charter `local_claude_1 20260817T223919` (pool #12) then authorized the build end-to-end, and it
> was carried out against this document unchanged. **The pre-registration below was frozen before
> the build and has not been amended.** The resident is still unmodified at
> `98628e98…`; nothing in this document modifies it.

---

## 1. The change, exactly

Site: `main_candidates`, resident `:1189-1192` (all line numbers in this document are the
RESIDENT's, not the instrumented build's — the instrument sits 4 lines lower from `:1397`). Current text:

```rust
let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
if idle_regeneration&&chops.is_empty(){
    return Self::endgame_candidates(view,unit,type_to_cut,safe_regeneration,opponent_eta_penalty,);
    }
```

Proposed replacement — an explicit mid-game fallback chain assembled from **existing generators
only**, no new candidate logic:

```rust
let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
if idle_regeneration&&chops.is_empty(){
    // MID-GAME FALLBACK CHAIN. Written out in full, including its tail: an undefined
    // tail is how the next wall gets built.
    let mut fallback=vec![MoisanBot::wait()];              // 3. explicit tail, stated first
    fallback.extend(Self::idle_harvest_candidates(view,unit));   // 1. harvest
    if unit.total_carried()>0{                                   // 2. bank if carrying
        fallback.extend(Self::bank_candidates(view,unit));
        }
    return fallback;
    }
```

### 1.1 The "not in true endgame" condition needs no new plumbing — shown two ways

The brief specifies C applies *"when NOT in true endgame"*, and `main_candidates` does not receive
the `endgame` flag. **No signature change is required, because the fall-through is already
unreachable in the endgame arms:**

- **By code.** `commands()` (resident :1397-1411) reaches `main_candidates` from exactly two arms: the
  `ENDGAME_CARRY` arm and the final `else`. The `ENDGAME_CARRY` arm passes `idle_regeneration =
  **false**` literally (resident :1401), so `idle_regeneration && chops.is_empty()` is false there. It also
  requires `carried_fruit(unit).is_some()`, which trips `main_candidates`' own first early-return
  (`safe_regeneration && carried_fruit.is_some()`, resident :1170) before `:1189` is ever reached — and
  `safe_regeneration` is `persistent_regeneration = true` for this resident. Two independent
  reasons.
- **By measurement.** All **485** observed fall-through turns carry `branch=MAIN`, and zero carry
  `ENDGAME` or `ENDGAME_CARRY` (`claude_1/hstarve1/mechanism-pool5-2026-08-17.json`).

Code and data agree. **This should still be asserted in the build**, not trusted: a debug
assertion that the chain is never entered while `Self::endgame(view)` holds, and a test that trips
it.

### 1.2 Open sub-choices — my recommendations as implementer

| # | question | brief's draft | my recommendation |
|---|---|---|---|
| 1 | chain tail: plain `WAIT` or `endgame_candidates` as last resort? | plain `WAIT` | **plain `WAIT`, and I would go further: keep it, but log it.** A troll reaching the tail is the residue (§4) becoming visible at runtime rather than only under the instrument. |
| 2 | does true-endgame routing stay untouched? | yes | **yes** — and per §1.1 it is untouched *by construction*, which is stronger than by intent. |
| 3 | who implements | claude_1 | mine, and the charter is the session's to write. |

---

## 2. PRE-REGISTERED per-fixture predictions

The standing procedure requires these **before** the build. They are derivable now because the
cross-tab (`20260817T202500Z`) is already measured; writing them after the build would make them
worthless.

**Prediction rule applied:** C supplies a candidate on a turn iff the turn is `MAIN`-branch **and**
`idle_harvest_candidates` would qualify a plant (or the unit carries something and
`bank_candidates` is non-empty). Everything else reaches the explicit `WAIT` tail and is unchanged.

| fixture | no-goal turns | C supplies | **predicted situation-level outcome** |
|---|---:|---:|---|
| OSC-032 | 110 | 110 | **FLIPS GREEN** — cure property satisfied on every window turn |
| OSC-033 | 143 | 143 | **FLIPS GREEN** |
| OSC-028 | 51 | 51 | **FLIPS GREEN** |
| OSC-008 | 7 | 7 | **FLIPS GREEN** |
| OSC-031 | 189 | 11 | **DOES NOT FLIP** — 167 chop-only turns reach the tail; C working as specified |
| OSC-001 | 16 | 3 | **DOES NOT FLIP** — 12 turns are `ENDGAME`-branch, occupancy declines the rest |
| OSC-009 | 4 | 0 | **NO CHANGE AT ALL** — all 4 turns `ENDGAME`-branch; C never runs |
| OSC-005 | 1 | 0 | **NO CHANGE AT ALL** — returns at `:1185` (full capacity), a different door |

**Acceptance set = the four**, at **311 of 311** turns. Adopting all eight would fail a cure that
is behaving exactly as specified, or invite relaxing the gate to make it pass — and this programme
already has a fabricated acceptance in its quarantine list.

### 2.1 The limit on this pre-registration, stated rather than discovered later

For the **other 26 fixtures** I can predict the direction but **not** a CHANGED/UNCHANGED verdict,
and I will not pretend otherwise. C alters the candidate list of any chopless mid-game troll, which
changes `select()`'s input and can therefore move the pairing outcome — including for the
non-anchor unit, and including in the 24 `GOAL_SPLIT_WRONG` situations.

**Why it is not derivable from current data:** the fall-through is only *observable* when it
produces a WAIT-only list. When `endgame_candidates` returns something non-WAIT, the record is
indistinguishable from `main_candidates`' own body. The instrument logs the routing arm, not the
producing function — the same distinction that nearly put the wrong function in the pool-#5 note.

**If the session wants a complete pre-registration**, it costs one instrument revision: log a
`HS2FALLBACK turn= unit=` line at the `:1190` return, re-run the 34, and the CHANGED set is then
exact. That is a small, reviewable change and I would rather do it before the build than argue
about collateral afterwards. **Recommended.**

---

## 3. Build and validation order

1. **Observed-failing first.** Write the four acceptance fixtures against the *unmodified*
   resident and watch them **fail** — the cure property red on 311/311 turns. A green-from-birth
   test proves nothing; every guard in this track that was never observed failing turned out to be
   inert.
2. **Byte-identity discipline.** The resident stays untouched at `98628e98…`; the cure is a new
   candidate file, and its provenance is regenerated from the resident by a `make_*` script that
   refuses on a non-unique anchor — as `make_instrumented2.py` does.
3. **Non-interference is not claimed, it is measured.** Command-stream parity against the resident
   on all 34 fixtures, expecting **differences** only where §2 predicts them. Any difference
   outside the predicted set is a finding, not noise.
4. **Detector gate.** 240-game panel: **ZERO de-novo D-1 AND ZERO de-novo P4**. P4 is named
   because D-1 is structurally blind to a non-moving unit — measured on the 34 frozen fixtures,
   where all four stalls show 0 D-1 and 1 P4.
5. **Paired night.** One A-vs-resident night under the M-1 rule (1.96·SE winner, 1.0 materiality
   floor). **One change per night; never stacked with the banana farm.**

## 3.1 Named risks, carried from the brief and not softened

- **Collateral breadth.** Any temporarily-chopless troll now harvests mid-game; denial timing,
  banking cadence and pairing equilibria shift outside the eight. §2.1 is why this is a
  measurement task, not an argument.
- **Lost side behaviours.** These trolls no longer get the endgame planner's mid-game side effects
  (the shack-side conversion `PICK`). This is a behaviour change and **must be named in the diff**
  even if it is an improvement.
- **Score calibration.** Harvest scores were tuned for the endgame slot; in the new slot they may
  outbid or underbid. The panel and the paired night carry this, not reasoning.

---

## 4. The residue — larger than what C closes

**OSC-031's 167 chop-only turns.** No fruit anywhere, so the chain's harvest step yields nothing;
the unit carries nothing, so the bank step yields nothing; it reaches the explicit `WAIT` tail and
the troll still stands still. **C does not address them and is not meant to.**

The rejecting clause inside `chop_candidates`' per-plant loop is **deliberately unlocalized** — the
candidates are `predict_tree` returning `None`, a predicted `size`/`health <= 0` at arrival, the
round-trip clock test, or `wood <= 0`. Free capacity is 2 (so `wood <= 0` needs `final_size <= 0`)
and ≥101 turns remain (so the clock test is unlikely to bite), which points at the tree-prediction
clauses — **an untested hypothesis, written as one.** Resolving it needs `predict_tree`/
`chop_outcome` logged or faithfully replicated; a wrong replica is worse than no answer.

**If the owner's goal is the parked troll rather than the phase gate, this is the next question and
it is bigger than the one C closes.**

---

## 5. What this document does not do

It does not modify the resident, write cure code, run the Arena, or implement either banana-farm
spec. It does not decide the ruling: whether the phase gate's scope should be widened is the
owner's call in pool #6, and the accepted neutral wording for the finding remains **"deliberate
phase-gate composition gap"**.

*(§5 describes the document. Under the pool-#12 charter the build itself was carried out
separately; §6 records it. The resident remained unmodified throughout.)*

---

## 6. Execution record — added 2026-08-18, after the pool-#12 charter

The change in §1 was built **verbatim**, by generator rather than by hand:
`make_candidate_c.py` derives the candidate from the resident and refuses on a non-unique anchor,
on an edit that changes more than the anchor, or on more than one diff hunk. It also re-verifies
the five textual premises of §2's reachability argument on **every** build, so the argument cannot
quietly go stale against a changed subject.

- candidate `claude_1/cure-c/candidate-cure-c-quiet.rs` — sha256
  `ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1`
- resident, **unmodified** — sha256 `98628e98…`
- the diff is **one hunk, six lines**

| gate | result |
|---|---|
| G1.1 fail-first | **PASS** — 311/311 turns red on the unmodified resident, matching the frozen registry |
| G1.2 cured | **PASS** — OSC-008/028/032/033 → 0 no-goal turns |
| G1.3 predicted-uncured | **RED** — OSC-009 4→0, OSC-031 178→89; both *over*-deliver |
| G1.4 fixture no-regression | **PASS** — 34 situations, whole-game, zero de-novo D-1/P4 |
| G2 acceptance panel | **FAIL** — de-novo D-1 = 1, P4 = 3 by episode count · 1 and 2 by turn coverage |
| G3 latency + thread parity | **PASS** — warm p95 0.065 ms against a 50 ms budget (resident 0.057 ms, same run); 240/240 rows byte-identical 1-proc vs 8-proc |
| G4 review | handed to `codex_1` **red**, `20260818T014000Z` |
| G5 submission | **not approached** — the charter's direct-submit exception applies only after a green handoff |

Aggregate, recorded for context and **not** offered as a gate argument: blocking games 119 → 58,
violation instances 289 → 115.

**Both G2 regressions are mechanised, and neither is repairable from here:**

- **m082 seat 1** is *tail-caused*. It vanishes under an `endgame_candidates` tail — but that tail
  costs nearly all of C's benefit (blocking 58 → **122**). It is a genuine regression, not a
  counting artifact: score 12 → 1. Choosing between the tails is a session decision, not mine.
- **m061 seat 0** is *trajectory-caused*. C and the endgame-tail variant are **byte-identical**
  there, so no choice of tail changes it. The candidate diverges at turn 24, reaches a
  higher-scoring position (75 against the floor's 48), and starves in a state where the resident's
  own generators would also have offered nothing. **No implementation fix exists within C's
  design.**

**Where §3's pre-registration was wrong.** The registry's rule was *turn-local*, which can support
a zero-residual claim but never a positive-residual one on a whole-game replay — the exact hazard
declared one document earlier for the other 26 fixtures. Two of eight fixtures diverged. The
registry was **not amended**; the defect is recorded in
`registry-postmortem-2026-08-17.md` and clause 3 was left red.

**What this leaves open.** The implementation is complete and every gate that can be run has been
run. Submission requires one of three decisions that are not the implementer's: a ruling on which
metric "ZERO de-novo" means (`20260818T003500Z` — the two disagree, and the friendlier one flatters
this candidate), authorization to revise C's tail at the stated aggregate cost, or an explicit lift
of G2 recorded as the owner's call. Absent one of those, the correct state of this task is
**blocked, not submitted**.
