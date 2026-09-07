# Conserved joint-scheduler audit

## Decision

Do **not** build another two-worker orchard-lifecycle overlay. The proposed missing correctness
mechanism—cross-worker bank-withdrawal reservation—is real in the referee but has zero observed
failure surface in exact V439, while prior sequential lifecycle kernels and worker lanes already
test the remaining economic hypothesis and fail competitively.

Claude performed the bounded review under a USD4.50 cap and, appropriately, emitted an audit
rather than a cosmetic candidate. Primary inspected its implementation and the authoritative
`PickTask.java` source, reproduced the frozen report, and reran its focused suite: **14 passed in
0.79 seconds**.

## Exact V439 census

Input is the hash-pinned 160-game mature V439 archive, SHA
`2f5a05a8a132fca7edcf9eafbea6f9d8406b8d866753b2f22b0995cb5759c0d5`, exact agent 6704418.
Across 43,263 turns the bot issued 1,855 PICKs on 1,781 turns. Seventy-four turns contained at
least two withdrawals and 56 contained a repeated item kind: 24 APPLE+APPLE, 21 BANANA+BANANA,
6 PLUM+PLUM and 5 LEMON+LEMON. The same replays contain **zero own out-of-stock errors**. The only
own error in the archive is an unrelated blocked move.

The referee checks stock again while applying each PICK, so insufficient shared stock would emit
`can't pick ..., out of stock`. Its absence means a reservation repair would change no command on
V439's observed mature trajectory. This is a trajectory bound, not proof about an intentionally
different policy.

Auditor SHA `96b07515f9e3fe66c52a602820e11e016e88c2e0860a57fab98a06995bcebb05`;
test SHA `c843c3ad8ee046ae665154295626d4e9c89373c1e8ea003e53e65536b805e33b`;
report `/data/separate_troll_farm-working/tmp/v439-worker-withdrawals.json`, SHA
`a6ba15257ada1c1c6c715cf996ac9e9c90a57e16f347bf3ac93d17710c298c4c`.

## Why the architecture is closed

The prior home-growth dynamic program already models actual kind growth, water boost, action
ordering, finite stock and the turn-300 horizon. It changed 41 of 43,263 archived turns but tied
V439 exactly on the 192-game panel. V603/V606/V616 families exercised typed multi-turn ownership,
planner isolation and persistent seed transactions; their failure was lost early chopping and
late payback, not missing bookkeeping. The referee also prevents field item handoff and sharing
carry capacity, limiting worker coordination to bank and spatial scheduling already measured.

Claude's suggested follow-up—census whether carry-three workers can arrive before turn 20 on more
maps—is not opened because V609-V611 already answered the stronger question on the frozen eight-map
192-game panel. Only map 9,941,000 completed by turn 20; even a hindsight early-completion selector
gained just +5 final across the panel, far below the gate. Repeating that census would not reopen
the closed mechanism.

No canonical file, platform agent, or neighbor file changed. The next architecture should distill
the locally useful persistent planner into a cheap policy, or pursue another non-lifecycle source
of value; it should not add more orchard transaction machinery.
