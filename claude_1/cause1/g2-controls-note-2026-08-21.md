# G-2 controls — `20260821-osc032-033-cause-attribution`

- Task: `20260821-osc032-033-cause-attribution` (coordinator-chartered at the owner's request)
- Work owner: claude_1 · **Reviewer: codex_1** · Integrator: local_claude_1
- Base: champion `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`,
  clause probe `64094f36fa70...`, subject `door1-clause`
- G-1 verdict: **ACCEPTED** by codex_1, 2026-08-21, at commit `2764db56`
  (`coordination/messages/codex_1/20260821T081645Z-20260821-osc032-033-cause-attribution-ack.md`)

**Measurement only.** No fix, no candidate, no hypothesis verdict, no harm/benefit judgment, no
class-wide claim. G-3 is a separate gate and nothing here opens it.

## What this gate is, and why it is not `cause_attribution.py` re-reading its own flags

The card's G-2 names three requirements: parity, coverage, both ways. `cause_attribution.py`
already gates on all three internally, and it is now G-1-accepted. But its G-2 evidence would be
its own booleans, and this instrument has already been caught once with exactly that shape — four
control checks that accumulated into a `failures` list and were never raised, disclosed at G-1
rev 2. So `g2_controls.py` recompiles both binaries, re-runs both fixtures, and **re-derives each
of the three requirements from the raw streams**, recording digests and turn sets rather than
`true`.

## 1. Parity — recorded as digests, not as a boolean

| fixture | uninstrumented command stream | instrumented | bytes |
|---|---|---|---|
| OSC-032 | `84b88f49f9ad…` | `84b88f49f9ad…` | 1531 |
| OSC-033 | `660ad1e38eff…` | `660ad1e38eff…` | 1142 |

Byte-identical on both. An empty pair of streams is refused: equality between two empty streams
is not parity, and it is the way this check would silently succeed if the runner broke.

## 2. Coverage — subject-derived, and honestly vacuous in-window

The window is read from each fixture's own situation record (`turn_start`/`turn_end`), never from
a constant borrowed from another population — the 4c Amendment-1 lesson.

| fixture | window | window turns | chop calls | idle-harvest calls | plants on board | plant rows |
|---|---|---|---|---|---|---|
| OSC-032 | 91–200 | 110 | 110 | 110 | `{0: 110}` | 0 |
| OSC-033 | 58–200 | 143 | 143 | 143 | `{0: 143}` | 0 |

Exactly one call group per audited-unit window turn for both taps, no gaps and no duplicates; each
`ENTERED` call emits one clause row per entry of the `view.plants` count **that call itself
printed**; a call that returned at the function guard emits none; no cell twice.

**The honest limit, stated first rather than buried:** on every audited window turn of both
fixtures `view.plants` is empty, so "one clause row per plant" is satisfied by *zero* plants. The
in-window per-plant direction of this gate is **vacuous**. The non-vacuous coverage evidence is
outside the window (OSC-032 turns 35–90) and corpus-wide in `clause-control-2026-08-21.json`, and
the per-plant checks are exercised against real boards in the negative control on turns 41–52.

## 3. Both ways — set equality against the same run's own route rows

The card names OSC-032 turns 35–90, `main:CHOPS` ×29, as the accept-side evidence. That number is
**re-derived, then compared**, never used as a threshold to match:

- OSC-032: `main:CHOPS` on **29** turns — 41–52 and 65–81. The clause tap reported an ACCEPTED
  tree on **exactly those 29 turns**: containment holds in both directions, `main:CHOPS \ accepted`
  and `accepted \ main:CHOPS` are both empty. The card's 29 agrees with the measurement, and a
  disagreement would have failed the run rather than being quietly absorbed.
- OSC-033: **`main:CHOPS` on zero turns of the whole game.** The card's named accept-side evidence
  **does not exist on this fixture**. Its accept side comes instead from the early branch's chop
  calls on turns 1–12 (12 accepted plant rows). That is a weaker instance of the same direction,
  not the card's own, and it is recorded as such rather than reported as if the card's evidence
  had been found.

Zero accepted rows *inside* either audited window, which is the measurement, not a gate failure —
and it is why the accept side has to be demonstrated outside the window at all.

## 4. The gates are shown to be capable of failing

`g2_negative_control.py` runs OSC-032 once and feeds the very same check functions deliberately
corrupted copies of the real streams: **12 corruptions rejected, 5 clean streams accepted, 17/17**,
and every rejection was for the gate under test rather than an adjacent one (checked by reading the
recorded rejection messages, not by trusting the pass).

| gate | corruptions it must reject |
|---|---|
| parity | one changed command byte; both streams empty |
| coverage | deleted window call (gap); duplicated call group; call claims more plants than rows; claims fewer; **same cell named twice, count-preserving**; plant row under a guard return |
| both ways | every ACCEPTED row stripped (constant-"rejected" tap); acceptance stripped from one `main:CHOPS` turn; two different routes in one turn |
| card cross-check | one `main:CHOPS` route row dropped, so the measured count drifts from the card's |

Two notes on the construction, because both are places a negative control lies to itself:

- The duplicate-cell case is **count-preserving** — the second plant row's cell is rewritten to
  the first's rather than the row being duplicated. A duplicated row also changes the count, the
  count check fires first, and the cell-identity gate would never have been exercised. This is
  codex_1's same-count/wrong-cell class applied to my own control.
- The per-plant cases run on turns 41–52, outside the audited window, because the audited window
  has no plants to corrupt. That is a control over the *check*; it claims nothing about the window.

`g2_controls.py` now **requires** the negative-control artifact, requires every case to have
behaved, and requires a corruption against each of the four gates, raising **before** the artifact
is written. Verified by removing the artifact and re-running: exit 1, no report. This is the G-1
rev-2 defect applied as a lesson rather than repeated.

## A defect this gate found in itself

The first run of `g2_controls.py` **failed**: `no fixture routed through main:CHOPS on any turn`.
The cause was in my new reader, not the bot — I matched the route regex's bare `route=` group
(`CHOPS`) instead of the `fn:route` name (`main:CHOPS`) that `route_table.py` composes, so the
join found nothing. Had the cross-fixture check been an existence test on accepted turns instead
of a demand that the card's named evidence actually exist, this would have passed green with the
both-ways join silently matching nothing. Recorded because the near-miss is the argument for the
check.

## What is NOT claimed

- **No hypothesis verdict.** H-A / H-B / H-C are the G-3 deliverable. Nothing here rules on them,
  and the numbers above must not be read as supporting any of them.
- No claim that any measured route or clause is right or wrong. Bug-versus-correct-caution is the
  owner's ruling, after G-3.
- No claim about any situation other than OSC-032 and OSC-033; no class-wide claim.
- No claim that the in-window per-plant coverage direction was exercised. It was not; there were
  no plants.
- The §5 question raised at G-1 — that the card's "the oracle said it had work every turn" premise
  is refuted by `oracle.py` returning the empty set 110/110 and 143/143 because `view.plants` is
  empty — remains **raised to local_claude_1 and unacted-on**. It bears on what G-3 should be
  asked, and that is the coordinator's and the owner's call, not mine.

## Reproduce

```
python3 claude_1/cause1/g2_negative_control.py   # 17/17, ~10s
python3 claude_1/cause1/g2_controls.py           # parity + coverage + both ways, ~10s
python3 claude_1/cause1/cause_attribution.py     # the G-1-accepted run, unchanged output
git status --short                               # accepted probes and manifests UNCHANGED
```

## What G-2 is being asked to rule

1. Are parity, coverage and both-ways adequately evidenced given that the in-window per-plant
   direction is vacuous on both fixtures?
2. Is OSC-033's early-branch accept side (turns 1–12) acceptable as its both-ways evidence, given
   that the card's named `main:CHOPS` evidence does not exist on that fixture — or does G-2 fail
   for OSC-033 until a fixture that carries it is added?
3. Is the negative control's case set the right one, and are the two construction notes above
   (count-preserving duplicate, out-of-window per-plant cases) the right handling?
