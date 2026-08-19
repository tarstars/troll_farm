# D2 viewer v2, code appendix, and top-down template re-review — 2026-08-15

Task: `20260815-oscillation-deep-dive`  
Reviewer: `codex_1`  
Subjects: `1f37aba6`, `66a1af0b`, and later owner policies through `321a6600`

## Verdict

**ACCEPTED WITH ONE POLICY-SYNC EDIT.** All findings from the first review are correctly applied.
The owner-redefined top-down adjudication template is coherent and materially better separated
from the descriptive code appendix. The viewer proposal's blind-session ordering is now stale
against the later owner scope ruling and must be updated; it does not block the authorized Phase-1
display build.

## Verified corrections

- Viewer distinguishes verbatim command/target from visibly inferred own positions; opponent
  positions and all stateful panels remain entry snapshots.
- Map alphabet covers `# . 0 1 + ~`, unknown characters fail loudly, `kind` is top-level, and
  the two single-cell stalls are first-class cases.
- Appendix C2/C3 are explicitly endgame-conditional; C3 is carried-fruit conversion, not generic
  regeneration.
- C7 correctly splits raw-distance MINE travel from speed-normalized/wait-aware HARVEST travel.
- C9 correctly calls 2,400 assumption-dependent and notes the 1,950 bound for opponent distance
  at least one.
- Routing, forced candidate replacement, pair scoring, and resolver rewriting are described in
  their actual order around the numeric ladder.

## Top-down template sanity check

L1–L4 forbid using the bot's own scores as normative evidence; step 5 introduces transcript,
Decision Packet, and appendix only after a game-level judgment exists. Step 6 makes rules an
owner-approved output with situation provenance. That separation avoids laundering the current
implementation into the desired policy.

During Phase 1, L4 must state that later-turn board positions are hypothetical/command-derived,
not reconstructed facts; only entry state and recorded commands are exact. The viewer already
encodes this limit, so the session record should carry the same wording.

## Required policy-sync edit

Viewer v2 §2/§6 says blind/reveal must exist before any adjudication session. The later owner
policy `20260815T070500Z…d2-scope-agreed-policy.md` explicitly authorizes the Phase-1 display build
and live sessions while packet overlay/blind mode remain Phase 2 behind a separate gate. The owner
ruling controls. Remove the stale pre-session blind requirement or label it superseded; Phase-1
sessions must still avoid exposing nonexistent packet scores as though they were evidence.

No viewer implementation was reviewed here; `claude_1`'s Phase-1 build has only been claimed.
No Arena action.
