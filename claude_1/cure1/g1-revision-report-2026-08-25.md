# Candidate 1 — the R-A / R-B / R-C rebuild, and what the revision cost

Task `20260825-dance-cure-candidate-1-hold`. Builder `claude_1`. Ordered by the G-1 disposition
ruling `coordination/messages/local_claude_1/20260825T094200Z-…-policy.md`, acked at
`20260825T095000Z`. This report supersedes nothing: `g1-report-2026-08-25.md` is the as-built
record and stays as written.

**The revised arm passes every G-1 clause the ruling names.** It is also a much smaller cure than
the arm it replaces, and that is the finding this report is really about. Section 3 is the number
I would want read first if I were the coordinator.

---

## 0. What changed in the source, and nothing else did

One generator, one source, three arms from one line — unchanged. Three additions:

| | |
| --- | --- |
| source | `claude_1/cure1/cure1-hold-v4.rs`, sha256 `cc4b308705883f10…`, 1,812 lines |
| instrument | `arm-instrument.rs` `cc4b308705883f10…` (HOLD=on, NARRATE=on) — 0 lines differ from the source |
| candidate | `arm-candidate.rs` `be6d1ce9d278cd62…` (HOLD=on, NARRATE=off) — 1 line differs |
| rule-off | `arm-ruleoff.rs` `db68e5ab5856a414…` (HOLD=off, NARRATE=on) — 1 line differs |

**R-A — `const TRANSIENT_ONLY:bool=true;`** The hold fires only when the block is *transient*: the
own unit standing on our landing is itself a mover this turn, **or** that cell was not its cell on
the previous turn; if no own unit stands there, the square was handed to another mover in this same
pass, which is a mover by definition. Anything else — including an **unknown** previous cell, which
fails **closed** — takes the base's regressive detour. The one new memory is
`prev_cells: BTreeMap<i32,Cell>`, written at the end of every call to the stateful entry point from
`view.units`, read only inside the hold branch.

**R-B — `const P3_SCOPING_ENABLED:bool=true;`** plus `fn orchard_eligible(view)`, evaluated once on
the first view and cached in `orchard_inert: Option<bool>`. It mirrors
`fuzz_panel.orchard_eligible_view` gate for gate: ≥ 2 own doors; ≥ 1 live natural plant; every
natural reachable from the own doors with **median** own-door distance ≥ 8 (integer median: for an
even count the panel averages the two middles against 8.0, so the sum is compared against 16); and
a free own door that is water-adjacent with enemy-door BFS distance ≥ 11, a door the enemy BFS
cannot reach counting as far, exactly as the panel's `edist.get(door, BIG)` does. On such a view the
hold is inert for the whole game.

**Why "the whole game", and the control the ruling asked for.** The ruling asks for the hold to be
inert on "the dormancy interval as `fuzz_panel` defines it", with a control showing the hold firing
"one turn after the interval ends". I read the gate before scoping to it: `eval_p3` compares the
**entire** command stream against the parent's whenever `spec["orchard_eligible"]` is true, and that
flag is computed once per map+seat from the initial rows and plants. There is no sub-game interval;
the covered interval is the whole game, and **"one turn after" is not constructible inside a game**.
I did not build a fixture that pretends otherwise. The substitute is in §4: the scoping flag flipped
back, on the identical map, reproducing the identical failure.

**R-C** is measurement, §3 and §5.

Everything else is untouched: the two-phase hold-seeded fixed point, `W = 2`, codex_1's eight
definitions, the three arms, parity both halves, the controls, the poison arm.

## 1. Parity — the gate that says the machinery is behaviour-neutral

| | result |
| --- | --- |
| 34 frozen fixtures, rule-off, stripped of `MSG` | **34/34 byte-identical**, **34/34 identical next referee state** |
| 240-game panel, rule-off, stripped of `MSG` | **240/240 byte-identical**, 0 telemetry errors over 48,000 turns |
| rule-off wire controls on every turn | `pz=1`, `sp=0`, no `H`, no nonzero `b` — hold everywhere |
| candidate arm == instrument arm in play | **240/240** |
| max passes of the fixed point, rule on | 2 (bound is movers+1); stale protections **0**; W-collisions **0** |

## 2. The panel, against the matched floor — every clause the ruling names

Floor: the champion base `547fa706` judged against **itself** on the identical 240-game corpus,
re-run in this build and reproducing **43** blocking games exactly. `g2_grade.gate_m` proves the two
panels matched game-for-game before any count is read.

| clause (ruling) | line | revised arm | verdict |
| --- | --- | --- | --- |
| P3 clean | 0 new | **0 new P3 games** | **PASS** |
| idle-with-work per troll | ≤ 1.5 % | **0.6437 %** (base 0.7323 %) | **PASS** |
| blocking games | ≤ 43 | **40** (−3) | **PASS** |
| D-1 episodes down | down | 27 → **25** | PASS, and see §3 |
| regressive detour turns down | down | 1,290 → **1,248** | PASS, and see §3 |
| wood return not slower | not slower | −0.0065 turns paired | **PASS** |
| poison arm caught by the idle clause | caught | **3.9076 %** vs the 1.5 % line | **PASS** |

Named costs, full: no detector total **grew** (D-1 27→25, D-4 **10→7**, D-5/D-6/D-9 unchanged);
**0** de-novo blocks; **0** games where P4 got worse; **0** new R-5 horizon games; 224/240 command
streams byte-identical to the base; 5 named changed games — 3 `HEALED_BLOCK`, 2
`PROPERTY_CHANGE_WITHIN_A_BLOCKED_GAME`. The three `gd_named_costs` controls (null fork, poison
fork, non-vacuity) pass on **these** panels.

**P4 is not cited as a pass anywhere in this report.** The ruling voided it for this family and I
am holding to that: its number appears only in §5, as the evidence that it is still blind.

## 3. THE FINDING — the revision passes, and the cure is now small

This is not a complaint about the ruling. R-A is right about *why* the standing was worthless. It
is also, on this corpus, right about almost every hold the as-built arm took.

| | as built | revised (R-A) |
| --- | --- | --- |
| hold turns on the panel | 1,279 | **22** |
| idle-with-work share | 2.28 % | **0.64 %** (below the base's 0.73 %) |
| D-1 episodes | 27 → **1** | 27 → **25** |
| regressive detour turns | 1,290 → 618 | 1,290 → **1,248** |
| blocking games | 43 → 41 | 43 → **40** |
| D-4 episodes | 10 → 102 | 10 → **7** |
| command streams identical to the base | 200/240 | **224/240** |

**98 % of the hold turns the as-built arm took were against a blocker that was not going to move**,
and with them went the D-1 cure. What remains is real and is all in the right direction — three
blocking games healed with none created, two D-1 episodes and three D-4 episodes gone, forty-two
fewer regressive detour turns, no property worse anywhere — but it is a −2 D-1 cure, not a −26 one.
The dominant case is the never-moving worker, and the ruling assigned that tail to Candidate 2.
**The coordinator should decide with this number in front of them whether the Arena read is worth
spending on a −2, or whether the read belongs to Candidate 2.** I am not making that call and I am
not recommending against it this time: unlike the as-built arm, nothing here forecasts a kill.

**A structural consequence worth carding.** With the base resolver, a blocker whose square is
*reserved* is necessarily a **non-mover** this turn; and a non-mover that stood on the same square
last turn is *permanent* by R-A. So for a fixed blocker that stays put, the hold can fire **at most
once**, and consecutive holds require the blocking square to keep changing hands. It does happen —
the panel's longest consecutive run is 2 — but `HOLD_WINDOW` is close to inert now: §5 shows
`W = 255` and `W = 1` producing a **byte-identical** panel to `W = 2`. The bound the charter argued
about is no longer the lever; R-A is.

## 4. The revision controls — each revision flipped back, one line at a time

`revision_controls.py`, on the identical corpus. None of these is a candidate; none is in
`arm-manifest.json`.

| fork | one line changed | blocking | P3 | idle-with-work |
| --- | --- | --- | --- | --- |
| revised arm | — | 40 | **none** | **0.6437 %** |
| **F1** `TRANSIENT_ONLY=false` | R-A off | 41 | none | **2.1746 %** — over the line |
| **F2** `P3_SCOPING_ENABLED=false` | R-B off | 40 | **`m004` seat 0, first divergence turn 7** | 0.6463 % |
| **F3** both false | the as-built policy | **41** | **`m004` seat 0, turn 7** | **2.2815 %** |

Read the last row first: **F3 reproduces the as-built arm exactly** — 41 blocking games, 2.28 %
idle, the same P3 break on the same map at the same turn — from the revised source with two lines
flipped. That is the strongest single check in this build: it shows the rebuild did not quietly
change anything except the two clauses it was ordered to change.

And "exactly" is checked rather than inferred from three matching totals. `asbuilt_reproduction.py`
extracts `arm-candidate.rs` and `arm-instrument.rs` from `agent/claude_1@abeda52a` — the commit the
G-1 handoff pinned — with `git show`, runs both on the identical corpus, and compares every command
stream: **240/240 byte-identical to F3 on the candidate arm and 240/240 on the instrument arm**
(`results/as-built-reproduction.json`). The as-built branch census read off that reproduction is
`H 1,279 / R 618 / L 158 / W 472 / P 8,444 / N 65,777`, which is where §3's "1,279" and the earlier
report's "regressive detours 1,290 → 618" both come from.

And the two revisions are **separately necessary**: F1 shows R-A alone is what brings the idle share
under the line (R-B off changes it by 0.003 pp), and F2 shows R-B alone is what makes P3 clean —
with R-A on and R-B off the hold *still* fires on `m004` seat 0 at turn 7. Neither is redundant, and
the substitute R-B control the ruling's original wording could not have is delivered here: same map,
same turn, scoping the only difference.

## 5. Controls

**Resolver controls, 12 of 12** (`results/resolver-controls.json`, driven by `control-probe.rs`,
generated from the instrument arm by *adding* a driver — no resolver line edited):

- **new, R-A red** — a blocker that stood on the same cell last turn and is stationary now yields
  `R` on every turn, rule-on and rule-off **identical**. This is the control that would catch R-A
  being silently absent;
- codex_1 #1 — the counter cycle `H(b=1) → H(b=2) → R(b=0) → H(b=1)` on a **transient** blocker:
  exact. Labelled **SYNTHETIC** in the artifact: the probe declares the blocker to have arrived on
  each turn, because under R-A a real blocker that stays put stops being transient after one turn;
- codex_1 #2a, #3, #3b, #4, #5, #6a — improving detour `L0`, no-detour `W0`, self-target `W0`, free
  primary `P0`, non-MOVE `N0`, rule-off cannot emit `H`: all hold;
- codex_1 #2b — **NOT CONSTRUCTIBLE**, unchanged and still not counted as a pass;
- claude_1's contention control — one unseeded pass hands the holder's square to an earlier-order
  mover; the fixed point refuses. Unchanged by R-A;
- **the charter's positive control, rebuilt.** The as-built fixture used a teammate that merely
  stood still — R-A calls that permanent and would measure nothing. The transient block as it
  occurs in play is a teammate that has just **arrived** and is busy this turn, then leaves:
  rule-on holds once and is at the target on turn 3; rule-off steps **backwards** to (0,0) first and
  arrives on turn 4. The cure produces progress, not a polite standstill.

**The poison arm — the control for the control** (`results/poison-arm.json`), graded by the idle
clause, because P4 is void:

| variant | what | idle-with-work | longest park | P4 |
| --- | --- | --- | --- | --- |
| **P-A** | the charter's poison: `W=255` **and** R-A off — holds on every blocked step forever | **3.9076 %** | **194 turns** | 16, = the base's 16 |
| **P-B** | `W=255` with R-A still on | 0.6437 % | 2 turns | — |

P-A is **CAUGHT** — 2.6× the line — by the clause that replaced P4, on the same run where **P4 stays
blind**: 16 violations against the base's 16 while a troll is parked for 194 consecutive turns. The
gate defect the ruling recorded as standing is reconfirmed rather than assumed.

P-B is the more interesting row: with R-A on, `W = 255` produces a panel **byte-identical to the
revised arm** — same branch census, same blocking count, same idle share. So does `W = 1`
(`panel-named-costs-diag-w1.json`: 43→40, D-1 27→25, D-4 10→7). The window bound is inert under
R-A on this corpus, which is §3's structural point measured rather than argued.

**Per-troll distribution, and a defect in the obvious stricter reading.** The graded number is the
panel aggregate, which is what the ruling's `H + W` over own troll-turns and its 1.5 % line
describe. The per-troll distribution is reported beside it and it does **not** support a per-troll
maximum as a gate: the worst troll is at **95 %** idle-with-work in **both** arms — including the
base — and **28** of the base's 384 trolls are already above 1.5 %, against the candidate's 26. That
95 % is all `W`, the base's own forced WAITs. A per-troll-max clause would fail the champion. Named
here rather than left for someone to discover after it is written into a gate.

**v4 decode controls: 38/38 fired.** Grammar, round trip, `strip_msg` scope — unchanged.

**Frozen fixture library** (`claude_1/t1/fixture_harness.py`): base 0 FIXED / 11 graded / 23
NOT_REPRODUCIBLE_ON_BASE; revised arm 0 FIXED / **10 graded** / 24. The as-built arm left only 1 of
11 reproducible. The revised arm barely disturbs the library — which is another way of saying §3.

## 6. The wood-return delay (R-C / disposition 3)

D-4's proxy, measured directly (`wood_return.py`): commitment start is `detect_d4`'s own A5/I-19/I-21
rule, read from the same trace object, so the two cannot disagree about "committed"; the interval
ends when the cargo reaches zero; anything else is **UNRESOLVED** and reported separately rather
than folded into a mean with an invented duration.

| | base | candidate |
| --- | --- | --- |
| completed intervals | 695 | 691 |
| unresolved | 7 | 7 |
| mean turns, commitment → bank | 5.2878 | **5.2764** |

Paired by (map, seat) over 221 games: mean delta **−0.0065 turns**, slower on 4 games, faster on 7.
**No named cost.** D-4 itself fell 10 → 7.

## 7. Scope

No Arena action, submission, fetch, TestSession or sealed-data access in any phase of this build.
Nothing written outside `claude_1/cure1/**`, `claude_1/narrate4/**`, my status file and my message
namespace. The resident is untouched.

Not proven anywhere here, and repeated rather than footnoted: **platform non-interference**. The
instrument emits a `MSG` token every turn where the base emits one on turn 1. No harness in this
report reacts to command count, ordering or line length; if the live referee does, every parity
green above is still true and still says nothing about the ladder.

## 8. Everything here, and how to re-run it

```
python3 claude_1/cure1/make_cure1_source.py        # base -> the one source
python3 claude_1/cure1/build_arms.py              # -> the three arms + manifest, each compiled
python3 claude_1/cure1/alpha_parity.py            # 34 fixtures, rule-off, both halves
python3 claude_1/cure1/alpha_parity.py --arm instrument --rule-on \
        --out claude_1/cure1/results/fixtures-instrument.json
python3 claude_1/pipeline/fuzz_panel.py --config claude_1/cure1/cure1-{ruleoff,candidate,instrument,floor}-config.json ...
python3 claude_1/cure1/panel_parity.py            # 240-game alpha parity + rule-off wire controls
python3 claude_1/cure1/arm_equivalence.py         # candidate == instrument in play
python3 claude_1/cure1/panel_costs.py --controls  # named costs vs the matched floor
python3 claude_1/cure1/idle_share.py              # R-C: the clause that replaced P4
python3 claude_1/cure1/wood_return.py             # R-C: what D-4 is a proxy for
python3 claude_1/cure1/revision_controls.py       # R-A and R-B flipped back, F1/F2/F3
python3 claude_1/cure1/asbuilt_reproduction.py    # F3 == the as-built arm, 240/240 streams
python3 claude_1/cure1/d4_attribution.py
python3 claude_1/cure1/diagnostic_w1.py           # W=1, diagnostic only
python3 claude_1/cure1/make_control_probe.py && python3 claude_1/cure1/run_controls.py
python3 claude_1/cure1/poison_arm.py              # P-A (graded) and P-B
python3 claude_1/narrate4/controls.py             # v4 decode controls
python3 claude_1/t1/fixture_harness.py --candidate claude_1/cure1/arm-candidate.rs
```
