# Independent review — NARRATE G1 idleness

Verdict: **ACCEPTED WITH AN INSTRUMENT-BOUND HEADLINE** for
`agent/claude_1@c563e449860473d290ed000e2f7989cdbe6a6b21`.

I rebuilt the idleness probe and independently reran the panel over the same 149-game corpus. It
reproduced exactly: six exhaustive classes over 76,305 rows, 109 `WANT_SILENT_*` rows, 120
intention/command divergences, 54 adjudicable rows split 45 rewritten to WAIT and 9 manufactured,
66 parity-refused and not extrapolated, and 8/8 controls.

The six-way taxonomy is mechanically sound, exhaustive, and fixed without a post-hoc
intent-kind/verb value judgement. `commanded` is not an outcome measure: a commanded MOVE may make
no progress. Therefore the defensible wording is **109 rows had a selected non-NONE intention but
received no unit command**, not an unrestricted count of all trolls that "wanted something and
achieved nothing." The report acknowledges this directional limitation.

I also inspected the v2 production path. `narrate_chosen` is populated only from the winners in
`select_recording`; `narrate_message` maps an absent unit to `Target::None`. No other v2 field
preserves discarded candidates. Thus the claimed boundary is real: the 3,504 `NO_WANT_SILENT_*`
rows conflate no candidate with candidates discarded before selection. A v3 grammar is required
to split them and remains correctly DEFERRED absent a charter.

This is neither prevalence nor cure evidence. The seven `blocked-no-detour` rows are resolver-site
observations, not contention prevalence. The delivery also correctly discharges the prior 120-row
divergence card while leaving 66 rows explicitly unverified.

