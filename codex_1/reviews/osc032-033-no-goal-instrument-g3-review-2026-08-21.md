# OSC-032 / OSC-033 no-goal instrument — G-3 review

- Task: `20260821-osc032-033-no-goal-instrument`
- Reviewer: `codex_1`
- Reviewed handoff: `coordination/messages/claude_1/20260821T065107Z-20260821-osc032-033-no-goal-instrument-g3-handoff.md`
- Artifact commit: `50fa5a8e40d91f22c2848dc5eb7abe943e319dd4`
- Verdict: **ACCEPTED**

## Scope and charter compliance

The delivery supplies the G-3 route table in JSON and short Markdown, names the route
distribution across every audited turn, states what was formed and discarded, and includes a
plain-language owner brief. It preserves the charter boundary: no fix, candidate, harm/value
judgment, class-wide claim, P1/P2 extension, or Arena action is proposed.

The bounded finding is supported by the accepted instrument: every recorded-window turn in
both fixtures returns through `main:IDLE_REGEN_FALLBACK`; all three real sub-generators are
empty; the only discarded item is the seeded `WAIT`, so `discarded_real=0`. The delivery does
not carry Phase 3's real-candidate discard finding across. It explicitly leaves the false
conjunct in the post-turn-100 replant block unmeasured, as previously ruled.

## Independent reproduction

I checked out the pinned artifact commit in a detached temporary worktree and ran:

```text
python3 claude_1/picker2/make_route_probe.py --subject door1-champion \
  --manifest claude_1/nogoal/route-probe-manifest-2026-08-21.json
python3 claude_1/nogoal/no_goal_census.py
python3 claude_1/nogoal/route_table.py
```

All commands exited 0. The reproduced census reported OSC-032 at 110/110 and OSC-033 at
143/143 window turns on `main:IDLE_REGEN_FALLBACK`, with `discarded=1`,
`discarded_real=0`, and zero-valued harvest/bank/chop generators throughout. Both fixtures
supplied their own employed control (90 and 20 named turns), and the route reporter named
200/200 full-game turns in each fixture with the published contiguous spans.

## Verdict

**ACCEPTED.** G-3 is delivered within scope. Bug-versus-correct-caution remains the owner's
ruling; this review accepts the measurement and presentation only.

DEFERRED: none for `codex_1`.
