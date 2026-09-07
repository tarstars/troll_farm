# Two-worker capital release: prospective development test

## Hypothesis and scope

The current renewal controller funds a third worker with both existing harvest-capable workers
before comparing productive jobs. In the three inspected official development games it bought
that worker on turns 113 and 189, and never in the third game. A two-worker ceiling will release
that labor and banked fruit for scoring earlier. This might improve outcomes, or lose because
it forgoes worthwhile capacity; the experiment does not assume the answer.

The Claude review identified the scheduling issue but confused scarce-wild-fruit denial with
the separate opponent-planted-crop priority. We will not bundle a raid mechanism into this test.
No new raid bonus, orchard quota, worker talent, production value or movement rule is authorized
by this experiment. Stopping expansion is a controlled ablation, not a claim that two workers
are universally optimal. `EVALUATION.md` remains the evaluation authority.

## Implementation and verification

Add a checked export option for maximum own workers (2 or 4), leaving 4 as the default.
`planned_spec` must return no training transaction when the current count reaches the ceiling.
Everything else remains unchanged; the first hire and already-carried transactions must survive.
Claude will propose a patch using read-only tools; the primary agent will review and apply it.

Fixtures cover both capital modes and both ceilings: original behaviors; no third purchase or
funding goal under the ceiling despite abundant or deficient stock; unchanged first-hire choice;
and preserving carried seed/drop work. Compile exact readable/compact exports, enforce source
size, compare complete recorded-input streams, and audit official commands after evaluation.

## Frozen development budget and decisions

1. Run the familiar 8-map, both-seat, 12-family local regression panel once for the two-worker
   policy against exact V439. Compare with the archived renewal panel on identical blocks. Report
   outcomes, both scores, margins and failures; this is not fresh validation or a ladder gate.
2. Run four official development requests: unchanged renewal repeat versus putibuzu on
   seed 2609051701, then the two-worker export versus putibuzu/2609051701,
   delineate/2609051102 and PonyPonyCodeCode/2609051603, all seat 0. Use the already saved
   renewal and V439/V368 references. Verify control repeat and exact initial states. Stop on
   identity/protocol failure; no automatic play retries or tuning while collecting.
3. Advance to a separately frozen fresh-map, both-seat comparison only if the two-worker policy
   gains at least one match point over renewal on these three development blocks, without losing
   the lower-ranked control win, and the executable/command audits are clean. This small screen
   is a triage decision, not a statistical superiority claim. If it fails, record whether the
   expected early release occurred and close this implementation without publication.

If advanced, design and freeze that larger confirmation before opening any of its maps. Current
production stays V543 throughout this development test. No rating conversion or publication is
implied by this protocol.
