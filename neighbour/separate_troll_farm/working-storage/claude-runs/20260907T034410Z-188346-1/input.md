# Complete the orchard's seed investment, then measure the repaired policy

Budget30minutes. Same orchard family/tests only, archive prior source under this
run. Offline/no platform/agents/commits/newholdouts; parent/canonical/neighbor and
WORKSTATE unchanged. Use apply_patch. Read prior PRIMARY-REVIEW.md in
run20260907T032333Z-123585-1, not historical ledgers.

The last report's suggested unexplained bank-leak hunt is superseded by PRIMARY'S
new trace of CURRENT exact source (primary-trace.rs/log in that run):
No-iron fixture t65 banks1LEMON; t66PICK/t67PLANT(2,3); t68CHOP0 thenWAIT;
t100HARVEST/t101DROP yields1LEMON. Opponent startsfelling plantedtree at94.
t105PICK/t106PLANT samecell; t144PICK/t145PLANT again. Each harvestedseed just
replaces the destroyedtree. PLUMremains3 until181, then bothPICK after target
failure. This is not arbitrary bankleak at74. Your older two traces were built
before final fixes; do not use them as current-source causal evidence.

Concrete implementation: replace immediate 'if current cell is a feasible site,
plant now' with ONE coherent seed-investment/site choice using actual referee
growth schedule, required-fruit harvest cadence, travel+banking costs, remaining
turns and contest exposure. Choose a profitable attainable site/cycle for closing
the missing basket instead of repeatedly replanting a slow contested plot for
one fruit. Existingnearbankarea includes alternative sites; some water-adjacent
sites grow faster on the fixture. NOhardcodedcoordinates, specialfixturebranch,
blanketdryplotban or bank-adjacencyban. Persist a coherent selectedsite/seedjob so
immediate command scores do not undo it. Protect its genuinely growing sapling:
investigate actual CHOP68 emission despite the existing protection, use real
referee seedhealth/growth semantics, not assumed health>0 equivalence.
If no seed cycle can plausibly repay, abandon rather than indefiniteWAIT/mining.
Keep ordinary productive work when waiting does not require physical occupation.

Preserve completefixedspec acquisition, actualMINE/banking/trainreservation,
deficit-kind harvest and same-turn resource correctness. Keep all16 currenttests
and add a proper growth/payback distinction; do not simply weaken the no-iron
fixture until it passes. Its currently attainable alternative sites should be
evaluated by the controller, not granted new fruit/workerstats. Add at least one
post-opening state with actual parent's first-hirestats or known devtrajectory;
two1111syntheticworkers alone is not mapgen-opening coverage. Show a real
seed->growth->neededfruit->bank->paidTRAIN chain for the repaired no-iron map.
Inspect ignoredTRAIN in ironcase; no silent resource errors. Actual banking
profit, recruitment, and legality are separate metrics. The last ironfixture
24vs40 is NEGATIVE profit evidence, not solved by merely hiring earlier.

Within this same ticket, finish ordinary coding/tracing/repairs. Do not return
after15minutes solely on another located local defect if budget remains. If a
proper fixture cannot pass, preserve exact failed evidence; no strategicclaim.

After proper fixtures pass, freeze ONE candidate and execute serial16 exact
readable/compact equality,max<50ms,export<=100000UTF16. Then ONE192dev comparison
9947500..9947507,12adaptive opponents,bothseats,ALLOW_ANY_MAP_SEED=1. Samebaseline
policyflat95ee691e; all192 controlcommands must equal20260906T210944Z-3184968-1.
Use absolute Rust1.90 verifiedpath under working/toolchains/rustup/toolchains/,
explicit runlocalCargo targetdir and actual just-built artifact, frozenhashes,
no competingheavyjob duringtiming. No full160certification thisbatch.
Prospectivegate remains whole-panel W+0.5D>parent AND zero candidateissues for
further evaluation. No new holdout, favourable-map selection, or after-panel tuning.
If the corrected strategy loses, PARKit without anotherparameterpatch; report
the actual result. Do not mistake fixtures for superiority or rankprediction.

RESULT<=400words: exactmechanism/hash changes, realcycle/paidspawn/profitchecks,
16streamruntime/export,192WDL/points/scores/margins/peropponent/allfailures and
adaptiveactivation,limitations,nextaction. Evidencefulltables inrunstorage.
Collect everyjob; if deadline prevents panel, record exact nextcommand honestly.
