# Replay-to-Trace adapter G-1 review

Task: `20260821-corpus-prevalence`
Reviewed handoff: `coordination/messages/claude_1/20260823T065400Z-20260821-corpus-prevalence-adapter-handoff.md`
Pinned artifact: `agent/claude_1@bc814ba536df48e98f34a859b6fbdd7539cf75b4`
Verdict: **G-1 ACCEPTED**

The handoff is transport-valid: the full pinned commit is reachable from
`origin/agent/claude_1`, and all four declared paths exist in it. I independently ran
`python3 claude_1/adapter1/run_adapter_panel.py` from a detached worktree at that commit. It
exited 0 and reproduced 580/580 adapted game-seat pairs, zero refusals, all structural controls
firing, 37/37 D-1-flagged pairs changing under the state-shift control, and the reported result
digest `dfe9ca5d42deaf39f0d307082ed3aafbe8b813d3170060b128f320ba9690bad7` (JSON bytes before the
trailing newline).

The construction is accepted. It emits the exact transcript and command text consumed by
`trace_detectors.build_trace`, keeps seat normalization explicit and mandatory, checks the
`2T+1` frame/keyframe/alternation shape, rejects unknown decoder updates, proves contiguous
`resolved_turn` values, aligns pre-turn state `k` with command row `k`, and handles the one
observed trailing-empty command row without allowing `CommandParser` to shorten the join
silently. The corrupt-keyframe, alternation, missing-stdout, unknown-token, seat, and state-shift
controls exercise the claimed seams rather than merely sweeping valid inputs.

The command-shift measurement is correctly non-gating: only 7/37 flagged pairs change because
D-1 mostly consumes positions. It strengthens the requirement for structural alignment; it is
not evidence against the adapter.

Scope remains narrow. The printed 37 flagged pairs / 77 episodes are adapter coverage, not a
prevalence estimate. The corpus contains no resident `6561795`, reconstructed plant clocks can
create false dancing episodes, and P4 is not supplied by this replay path. G-1 accepts the
adapter as a review object; it does not unblock or retitle the resident-prevalence question and
does not grade any candidate.
