# Best current submission candidate selection — frozen 2026-07-19

## Objective

Identify the strongest upload-ready Troll Farm source supported by evidence available now.  The
result is a prepared candidate and a documented decision, not an Arena submission.  The current
resident remains agent `6560353`, submission `41012883`, unless a later explicit submission
instruction is given.

The principal ambiguity is resolved explicitly: historical peak rank is evidence about one Arena
snapshot, not a directly comparable policy score.  In particular, the original Yamo/Orchard
agent's rank 6 at 26.3 must be considered together with its later same-source 20.8--21.1 bracket
and the promoted resident's controlled 24.1 bracket.

## Frozen action list

1. Preserve and hash the exact resident and confirm its saved platform identity.
2. Inventory every source in `cgauto/submissions`, recording artifact class, size, checksum, and
   whether a matching sidecar exists.
3. Build an evidence ledger from prospective local gates, controlled `TestSession` panels,
   Arena A/A controls, Arena candidate trials, runtime checks, and explicit verdict documents.
4. Classify every artifact as resident, promotion-qualified challenger, local-only research,
   diagnostic, superseded, or rejected.
5. Disqualify sources that exceed 100,000 bytes, fail standalone compilation, contain diagnostic
   output, failed their frozen local/field/Arena gate, or lack a live-compatible continuation.
6. Shortlist only policies with a reproducible source and positive evidence at the strongest
   available transfer level.  Include the historical rank-6 Yamo/Orchard source explicitly.
7. Normalize historical Arena evidence against same-code controls, comparable game counts, and
   platform-capacity observations; do not rank candidates by their best transient position.
8. Revalidate finalist checksums, standalone compilation with warnings denied, source size, and
   deterministic behavior.  Use behavior-equivalent slim encodings when available.
9. Compare finalists on existing paired/common-seed evidence.  Run a new read-only or controlled
   common-seed discriminator only if the existing evidence leaves more than one credible winner.
10. Select by this precedence: safety/integrity, prospective transfer verdict, controlled field
    result, normalized Arena result, robust paired outcome, then code headroom.  A stronger tier
    cannot be overturned by an uncalibrated lower-tier simulator mean.
11. If no challenger clears the resident, select the exact resident rather than manufacture a
    change.  If evidence is genuinely tied, retain the resident and document the missing
    discriminator.
12. Compile, hash, and behavior-smoke the selected exact source; write an upload-ready manifest
    with rollback artifact and remaining byte budget.
13. Stop before any Arena write.  Submission and post-submit monitoring require an explicit next
    instruction.

## Prospective decision gates

A candidate is eligible only if all integrity checks pass and no later frozen verdict rejects its
mechanism.  Among eligible candidates, a challenger must have either:

- a successful controlled Arena promotion against a healthy same-code bracket; or
- replicated controlled-field evidence with no contradictory Arena result and a clearly stated
  reason that a new Arena trial is the remaining discriminator.

Local self-play, teacher imitation, Monte Carlo value, or curriculum success alone cannot replace
live-compatible transfer evidence.  Neural curriculum checkpoints are not submission candidates
until inference, opponent interaction, timing, packaging, and source-size gates exist.

## Initial high-evidence cohort

- current pre-seed + secure-orchard-coverage slim resident;
- behavior-identical slim form of the original rank-6 Yamo/Orchard policy;
- CompactGold rollout candidate, which received an Arena trial;
- opponent-crop `b100_e6` and dual-value candidates, which received controlled/Arena evidence;
- standalone Norxondor three-worker candidate, which received a controlled-field test.

All other sources enter through the ledger and may advance only if their recorded evidence is at
least as strong as this cohort.  Diagnostics are never eligible.

## Required outputs

- complete artifact/evidence inventory;
- finalist comparison and exclusion reasons;
- selected exact source with verified size and checksum;
- upload-ready manifest naming the resident rollback;
- no platform mutation.
