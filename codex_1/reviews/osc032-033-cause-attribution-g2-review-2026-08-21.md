# OSC-032 / OSC-033 cause-attribution instrument — G-2 review

- Task: `20260821-osc032-033-cause-attribution`
- Reviewer: `codex_1`
- Reviewed handoff: `coordination/messages/claude_1/20260821T082911Z-20260821-osc032-033-cause-attribution-g2-handoff.md`
- Artifact commit: `58ea9a72da51c3ec63584eb69ffa720d4c3fe1fd`
- Verdict: **ACCEPTED**

## Gate ruling

The delivery satisfies the card's three G-2 controls. Command streams are non-empty and
byte-identical between the champion and tap for both fixtures. Coverage uses each situation's
own window, observes exactly one chop and idle-harvest call per audited turn, and verifies the
row count and cell uniqueness against the plant count printed by that same call.

The in-window per-plant coverage direction is structurally complete but vacuous: both boards
have zero plants throughout their audited windows. That is the measured state, not a missing
call. The check itself is exercised non-vacuously on planted OSC-032 turns and by the negative
control; the accepted G-1 package separately established clause identity and direction across
real boards.

The card's both-ways requirement names OSC-032 turns 35--90 and `main:CHOPS` x29 as its control.
The delivery re-derives 29 turns (41--52 and 65--81), and the set of routed turns equals the set
with an accepted tree exactly. The card does not require every fixture to route through
`main:CHOPS`. OSC-033's 12 accepted early-branch rows therefore supplement the named control;
their different route provenance does not fail G-2 and must not be represented as the card's
named evidence.

The 17-case negative control is adequate. It rejects 12 corruptions and accepts five clean
streams, exercises parity, coverage, both-ways, and the card cross-check, and verifies the
intended check rather than an adjacent failure. The count-preserving duplicate-cell mutation is
the right construction. Running per-plant corruptions on planted turns 41--52 is also correct,
provided it remains described as a control of the checker rather than evidence about the empty
audited windows; the delivery does so.

## Independent reproduction

In a detached worktree at the pinned commit I ran:

```text
python3 claude_1/cause1/g2_negative_control.py
python3 claude_1/cause1/g2_controls.py
python3 claude_1/cause1/cause_attribution.py
```

All commands exited 0. Results reproduced as 17/17 negative-control cases; parity digests
`84b88f49f9ad...` and `660ad1e38eff...`; coverage 110/110 and 143/143; and OSC-032
`main:CHOPS` / accepted-tree set equality at 29 turns.

## Verdict

**G-2 ACCEPTED.** G-3 is unblocked under the coordinator's amended question. This accepts the
controls only: no hypothesis, bug/caution judgment, fix, candidate, class-wide claim, or Arena
action is accepted or authorized.

DEFERRED: none for `codex_1`.
