# Banana-farm two-spec v11 review — 2026-08-17

Verdict: **REVISION_REQUIRED** (two residual executable-schema gaps).

Pinned artifact: `f3d5e5dbb8625eaf7da3a7608ea6cd3c3a95e658`.

V11 correctly makes cell identity permanent after loss, adds the same-cell replacement
GK arm, makes suppression records joinable across run/map/seat/unit/cell, and narrows
the P4 statement to the detector property actually measured on 34 fixtures. Sections
3–8 are byte-identical between Specs A and B. Two requested details remain implicit.

## 1. “Consistent growth” is still not an executable transition relation

The new census rule says observations advance when “CONSISTENT with that same plant's
growth” and cites section 7. Section 7's `Grow` rule uses the same phrase; it does not
define it. The only explicit failures are size reset, kind change, and absence. An
implementer still must invent whether health decreases, fruit decreases, cooldown
changes, and size increases preserve identity, and under what emitted commands.

Specify the allowed `(previous observation, our commands, current observation)`
transitions over kind/size/health/fruits/cooldown. Everything outside that relation
must end membership. This can reuse one concrete reconciliation function for census
members and future tracked crops; it need not claim that indistinguishable same-cell
replacement is observable.

## 2. The trace does not yet contain the full adjudication state or fail closed on a
missing terminal row

The v11 event row has useful join keys and before/after “commitment state,” but the v10
request was commitment **kind and target** before/after reconciliation, plus machine
phase. Name those fields explicitly rather than leaving “state” and “full context” to
an implementation choice. The per-turn rows also need turn/cell (or an explicit rule
that the event keys plus turn identify every row) and the final post-conflict command.

“Until an explicit terminal reason” requires a terminal row, but the fail-closed clause
only voids a record that exists and lacks a key. State that a trace ending without one
of the four terminal reasons is itself void and a panel error; this is the requested
`trace_failure` outcome even if it is represented as an error rather than a terminal
reason.

These are schema/reconciliation definitions only. No new owner decision is required.

