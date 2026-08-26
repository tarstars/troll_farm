---
schema_version: 2
type: handoff
task_id: 20260826-banana-farm-candidate
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260826T215515Z-20260826-banana-farm-candidate-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260826T212149Z-20260826-banana-farm-candidate-policy.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 5e2294ab901e80a7fe3fdfca1e3b748124dc56e3
artifact_paths: ["claude_1/farm/g1-panel-farm-2026-08-26.md", "claude_1/farm/make_farm_source.py", "claude_1/farm/build_arms_farm.py", "claude_1/farm/farm-v8.rs", "claude_1/farm/arm-instrument.rs", "claude_1/farm/arm-candidate.rs", "claude_1/farm/arm-farmoff.rs", "claude_1/farm/arm-manifest.json", "claude_1/farm/containment_farm.py", "claude_1/farm/results/panel-instrument.json", "claude_1/farm/results/panel-farmoff.json", "claude_1/farm/results/panel-candidate.json", "claude_1/farm/results/containment-farmoff.json"]
created_utc: 20260826T215515Z
---

- To: codex_1 (the one reproduction), local_claude_1 (the board and the slot)
- CC: user
- Task: 20260826-banana-farm-candidate (board row F-2)
- Requires acknowledgement: yes

# handoff: the farm is BUILT and CONTAINED, and it FAILS its own first validity gate — V1, 52 -> 96 blocking games. **Nothing is submitted; ladder slot 3 stays booked and unused.**

Packet: `claude_1/farm/g1-panel-farm-2026-08-26.md`. Read it whole; the summary here is the
four numbers and the two things a repair would have to answer.

**C1 containment PASSES.** Farm-off is byte-identical in play to the champion on **240/240**
panel games and **34/34** fixtures, with `fs=0` and `fp=0` on every turn. The two farm-on arms
(instrument, candidate) are byte-identical in play on 240/240, so the v8 line is behaviour-neutral.

**V1 FAILS.** Blocking games go from **52** (farm-off, the champion's own baseline) to **96**
(farm-on): 50 new, 6 cured. The dominant detector is **D-6 `opp_harvested_ours` on 35 of the 50** —
the opponent walks onto our ring and eats the fruit we grew. V1 is pre-committed as go/no-go, so
this is a BLOCK on my own arm and the slot is not used.

**The latch fired in 0 of 240 games.** The packet §9 pre-registered exactly this as a *suspicion,
not a pass*. The wire says why: `fe` (enemy chop hits on our ring) is ~0 across the corpus while
`fw` runs to the tens. **The latch counts chops; the theft that actually happened is harvests.**
That is one design defect stated twice, and it is the honest headline.

**Own score +3,100 over 240 games**, 89 games changed, best +118, worst −90 — the opposite sign to
the pre-registered expectation of −5 to −20 a game. I checked for the containment bug the packet
told me to check for before celebrating; C1 is 240/240 and the arms are byte-identical in play, so
it is not that. It is a local-bench number under a failed validity gate, and it buys nothing.

Also on the record: **denial is a formality on this corpus** — 509 turns in DENY against 28,239 in
FARM, ending by reason `a` in 141 games (no aim tree to deny when the second troll appears), `b`
in 2, `t` in 1, never `c` or `d`; and **0 telemetry errors** from `narrate8.check_telemetry`
across all 240 instrument games.

Two limits a bounded repair would have to answer, both named in the packet:

1. the latch is pointed at the wrong verb (chops, not harvests), so on this evidence it is
   unreachable code rather than a one-way latch;
2. **W1 cannot bind the emitted stream.** It filters a carrier's candidate list, and
   `resolve_move_conflicts` runs afterwards and may rewrite a MOVE into a regressive detour — on
   m007 seat 1 a full carrier shuttled two cells for nine turns with every candidate it was
   offered having passed the filter. Fixing that means the resolver's hold logic, which the card
   puts under "Do not touch".

Six build resolutions (BR-2, BR-3, BR-4, BR-6, BR-7, BR-8) were made after the design was
accepted, each commented at its site and each listed in the packet — they are fair review targets.
No latch constant was re-tuned, on this corpus or any other; §4's pre-commitment is kept.

**For codex_1:** the one reproduction, if it is worth spending on a blocked arm — the reproduce
block is at the foot of the packet and needs only `make_farm_source.py`, `build_arms_farm.py`
and the three `fuzz_panel` runs. **One instrument finding for you specifically:** the instrument
arm reports 96 blocking games and the candidate arm 92 while the two are byte-identical in play on
240/240 — four games (`m014/0`, `m045/0`, `m054/0`, `m104/0`) block only when the `MSG`
line is present. Some panel detector is reading the diagnostic payload as gameplay.

**For local_claude_1:** F-2's dead condition is met — the validity gates failed on the panel — so
the board row goes to the owner as "built, contained, earns on the bench, not safe to put on the
platform in this form". Slot 3 stays booked and unused unless the owner charters a bounded repair.
