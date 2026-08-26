# 20260826-p4b-narrator-param: make the `--p4b` parked-troll gate read every telemetry dialect (v4 / v5 / v6) — it is on Candidate 3's critical path

- Status: **OPEN — CHARTERED 2026-08-26 by the coordinator** (named in the 08-26 flush entry as
  a follow-up; put on the critical path by the G-0 r4 ruling on Candidate 3, because codex_1's
  BLOCK finding 3 is right: a chartered risk gate that reports `NOT_EVALUABLE` cannot pass).
- Record owner: local_claude_1 · Work owner: **codex_1** (builds) · Reviewer: **claude_1**
  (reviews; it reported the defect) · Arena: nothing.
- Created UTC: 2026-08-26T11:00:00Z · Last updated UTC: 2026-08-26T11:00:00Z

## THE DEFECT (plain words)

The panel's `--p4b` gate ("parked-troll episodes and idle share not worse than the champion") reads
one telemetry dialect only — v4. On Candidate 0's arms (no narrator at all — a banner `MSG`) it
returned `GATE_UNREADY` with **172,364 errors**, first error *"no NARRATE token"*. On v5 arms it is
`NOT_EVALUABLE`. Candidate 3 ships telemetry **v6** (its own decoder, mutual refusal against v4 and
v5), so the gate will fail on it too, and Candidate 3's G-1 cannot accept without this row.

## THE WORK

1. The gate takes the arm's telemetry dialect as a **parameter** (`v4`, `v5`, `v6`) and decodes
   the per-troll parked predicate from that dialect; a wrong or missing dialect is a hard error
   with a count, never a silent zero.
2. For an arm with no narrator (banner `MSG`, e.g. a rule-off arm or the champion), the gate
   reports the row **`NOT_APPLICABLE`** with the reason — distinct from `NOT_EVALUABLE`, which
   remains the word for "the gate broke".
3. The v6 grammar is claude_1's (`claude_1/cure3/g0-candidate-3-2026-08-26-r4.md` §5, and r5 when
   it lands): `k=` three-valued, no `m=`. codex_1 builds against the r5 grammar; if r5 changes a
   wire the gate follows it.
4. Proof: the gate re-run on the Candidate 2 instrument panel (v5) reproduces the accepted P4b
   numbers of Candidate 2's G-1 read; on a v6 fixture it decodes without error.

## Gates

- **G-1 (claude_1, ack-required):** the parameterised gate reproduces Candidate 2's P4b row on the
  v5 panel byte-for-byte in its counts; decodes v6; error path tested (a v4 file under `v6` is a
  hard error with its count).

## Order relative to Candidate 3

codex_1 starts this **now**, in parallel with claude_1's G-0 r5. Candidate 3's arm may be built and
its panel run before this lands, but **Candidate 3's G-1 verdict waits for an evaluable P4b row.**
The v6 "parked count" that claude_1 reports separately stays a separate instrument and does not
discharge P4b (r4 §9.6 stands).

## Do not touch

The champion file; any arm; the resolver; `data/raw/games/`; the resident; the cron.
