# 20260821-champion-subject-library — fixtures follow the champion

- Status: **OPEN — OWNER-APPROVED 2026-08-21 ~11:15Z ("go")**, from the owner's
  observation that we were measuring with stale baskets (the champion reproduces 11
  of the 34 recorded episodes).
- Record owner: local_claude_1 · Work owner: **claude_1** · Reviewer: **codex_1**
  (instrument-first) · Integrator: local_claude_1
- Priority for claude_1: after cure α's current G-1 remedy step and the identity gate
  (deliverable 1 of `20260821-episode-identity-regrade`), before Phase 3a of the
  benching revision.
- Base: champion of record `547fa706…` (diagnostic copy); the library builder
  `claude_1/banana-restoration-r2/build_subject_library.py` (accepted 2026-08-11,
  hash-pinned — **unmodified**; it already builds a per-subject library).
- Created UTC: 2026-08-21T11:15:00Z

## THE RULE (owner-approved)

**A recorded episode belongs to the bot that produced it.** Fixtures are exhibits for
understanding and for the owner's rulings, and regression checks for *that* bot; they are
regenerated for every kept champion and never outlive it. Cures are graded on the panel
population (see the gate amendments on `20260821-swap-r1-cure` and
`20260820-pair-selector-anti-benching`), not on basket counts.

## Deliverables

1. **Subject library v-champion**: run the unmodified builder with the champion as subject
   over the standing panel configuration (the same `panel_config` the 98628e98 library used,
   so the populations are comparable) → `oscillation-library-547fa706/`, with the same
   schema, detectors (D-1 dance, P4 stall), classification, viewer pages
   (`build_viewer`), and the provenance block naming the subject hash. Episode identity
   (entry board + window commands) is recorded per case so a later bot can be checked
   against it.
2. **Mechanism carry-over table**: for each of the five owner-ruled mechanisms (corridor
   pass → swap; open-map pass → routing; same tree wanted → reservation; single-troll goal
   flip; idle troll parked on a plant) and for the benching class, which new cases
   exhibit it on the champion, by the same classifier vocabulary; and which old rulings
   have no exhibit on the champion any more (stated as "no exhibit", not as "fixed").
3. **The auto-refresh hook, designed not deployed**: a proposal for how the night-runner
   regenerates the subject library after an owner KEEP (command, inputs, where the
   output lands, how the viewer pages are rebuilt, how long it takes on the VM). Deployment
   goes through the VM deploy-card route (`20260819-osc031-vm-runner-deploy-card` shape),
   separately, after codex_1's review of the design.
4. A one-page owner note in plain words: how many cases, which shapes, what changed
   versus the old library, and the viewer links for anything the owner should watch.

## Gates

- G-1 codex_1: builder unmodified (digest), panel config identical to the old library's,
  subject hash correct, detector/classifier versions identical; the identity record per case
  verified on a sample by independent replay.
- G-2 controls: the old subject library rebuilds byte-identically from the same builder
  (the accepted attestation must survive); a deliberately wrong subject hash is refused.
- G-3 the library + the tables + the note.

## Out of scope

No cure, no candidate, no re-ruling of the 34 (their rulings are about mechanisms and
stand), no Arena action, no VM deployment inside this card.
