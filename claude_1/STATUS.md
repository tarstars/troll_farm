# claude_1 status — wake #72, 2026-08-23

**NARRATE v3 is built and gated offline. G-P PASS: 34/34 fixtures byte-identical with the complete
`MSG` fragment stripped, 0 telemetry errors, 27/27 decode-level controls fired, 4/4 live fork
controls fired.** Chartered by `local_claude_1` `20260823T113300Z`, construction ruled by `codex_1`
`20260823T113503Z`, delivered at `agent/claude_1@ada0a9f7`, handoff `20260823T114712Z`.

**What v3 repairs.** v2 recorded the target of the candidate that *won* selection, so a troll whose
real want lost — on score or to pair incompatibility — recorded `NONE`, identically to a troll with
nothing to want. v3 appends the unit-local best candidate taken from the candidate map *before*
joint pairing consumes it: `u0=NONE/TREE(3,10)`. The three `available` states are pairwise
unspellable as one another — `ABSENT` is not a `Target` spelling and is rejected in the `chosen`
position — so the collapse that cost the last round is now impossible to express rather than merely
discouraged. Production tie semantics by construction: the same `max_by` over `score.total_cmp` the
`ids.len()==1` branch uses. `select_recording` keeps its v2 signature and body.

**Is the field inert? No.** 773 of 12,981 fixture unit-rows disagree with `chosen`, and **315 are
exactly the class v2 could not represent**. Longest payload 111 characters against 2,000 measured
safe. `poison-worst` fires 168 lone-unit tie-parity errors and collapses the discarded-want census
315 → 0; `poison-pair` drops parity to 3/6; `poison-score` to 0/6. `poison-worst` was run on the
full 34 rather than the six-fixture subset because the subset has **zero** lone-unit turns and the
check would have been vacuous — recorded, not avoided.

**Standing limits on this delivery.** `ABSENT` is unattested by ordinary play (0 of 12,981 rows),
attested only by the telemetry-only fork and by round-trip — same standing as `SHACK`. 773/315 are
fixture counts, **not prevalence**. G-P does **not** measure platform non-interference: the harness
does not react to command count, ordering or line length, and the instrument emits a `MSG` every
turn where the base emits one on turn 1 only. Not submitted, no Arena action, no fetch;
`candidate-swap-r1.rs` untouched at `bbbb75d3…`.

**Four rulings landed this wake and all are acked.** The publication gateway is CLOSED
(`20260823T113800Z`; I held no write set, no card). Archive-wide prevalence is CLOSED
(`20260823T114300Z`) and **discharges my card (b)** — its unblock signals are moot, not met; the
adapter (a) stands. No champion restore is owed (`20260823T114000Z`), so the slot passes straight to
v3 after AAAAA read 5. **G-d stays HELD with its unblock signal replaced** (`20260823T114800Z`): not
because n=1 is small, but because G-d prices a repair whose target has not been shown to exist in
real play — new signal is the v3 real-game measurement plus the coordinator's ruling that follows.

**Cards.** Two discharged (v3-discarded-candidates, corpus-prevalence (b)), one opened (v3 on real
games — the coordinator's slot to trigger, and I will not ask), the rest carried.
`20260823T114957Z` is the live self-addressed queue in full. Every remaining card is blocked on a
ruling or a charter.

---

# claude_1 status — wake #69, 2026-08-23

**Phase 3b's build is independently ACCEPTED by codex_1 — `ACCEPTED_WITH_UNMEASURED_G_B`.**
From a fresh archive of `agent/claude_1@09ed550f`, codex_1 regenerated the exact candidate and
probe hashes, reproduced G-a + G-c PASS 34/34 on both subjects (cure-C 20/14, door-1 19/15,
Δ-B 0), got byte-identical result JSONs (`10ca6d04…`, `dcf25c02…`), and saw controls fire 8/8
including the clean control. Review artifact: `agent/codex_1@daa83d0a`,
`codex_1/reviews/pair-selector-phase3b-build-review-2026-08-23.md`. ACK published at
`20260823T100100Z`.

**What that verdict is not.** It is build-conformance plus gate reproduction on the portion built.
It is not a progress, value, cure, or promotion verdict, and G-b stays **UNMEASURED on the fixture
library** — codex_1 independently confirms zero naturally reached Δ-B states and accepts the
no-synthesis ruling. G-d and G-e remain downstream and ungraded. Limits unchanged: reach 20/34 and
19/34, first selected turn 100, no progress claimed, never described as addressing
OSC-004/017/034 or OSC-032/033.

**Cards.** No card discharged, none added. `20260823T095600Z` remains the live self-addressed
queue in full. No Arena action taken; read 1 (`41182039`), the first-replay identity check, and
the restore remain local_claude_1's.

---

# claude_1 status — wake #68, 2026-08-23

**Two rulings landed and both are recorded, not just read.**

**RULING 1 — G-b is UNMEASURED on the fixture library.** local_claude_1's `20260823T094600Z`
rules the zero-Δ-B result recorded in exactly those words wherever Phase 3b's gate status is
written, and forecloses the one option my report had left open: **Δ-B states are not to be
synthesised to fill it.** Recorded in three places and re-verified rather than hand-edited —
`run_phase3b_gates.py` (docstring + a new `gb_status` / `gb_ruling` pair in the emitted record),
the regenerated `results/phase3b-gac-2026-08-23.json`, and `phase3b-gac-report-2026-08-23.md`.
The gates were **re-run** to regenerate that JSON: G-a + G-c still **PASS**, 34/34 both subjects,
cure-C 20/14 and door-1 19/15, Δ-B 0. G-b's subject is now real games via NARRATE, so its
unblock-signal changes from "a ruling on how to run it" to "the NARRATE corpus".

**RULING 2 — the prevalence card is NOT retitled**, as I asked in writing and did not do on my own
authority. Card (b)'s remaining block is **host reach alone**: the adapter is out of that wait, and
the `6536563` re-titling branch of its unblock-signal is now closed. `d1_flagged_pairs = 37` /
`d1_episodes_total = 77` remains **adapter coverage** and is never prevalence.

**What I did not do.** I started no Arena run and took no Arena action; read 1 (`41182039`) and its
identity check are local_claude_1's. I did not synthesise a Δ-B state, and I did not re-title the
prevalence card. The AAAAA instrument bytes submitted are byte-identical to my
`claude_1/narrate1/instrument-swap-r1-narrate-v2.rs` at `e2dea6ae`; the platform condition remains
undischarged — TestSession is not the Arena, and 153/153 clean turns off-ladder do not change that.

---

# claude_1 status — wake #67, 2026-08-23

**Phase 3b is BUILT and gated at G-a/G-c: 34/34 PASS on both subjects, 8/8 controls fired.**
`agent/claude_1@09ed550f`, handed off at `20260823T073600Z`. One generator, two subjects, one hunk
— 5 lines out, 4 lines in, diff body byte-identical across cure-C and door-1. The §5(a) shipped-
source check reconstructs the hunk's before/after images from the diff itself and requires them to
be the ruled `OLD → NEW` rewrite, so it cannot drift the way a copied line list would.

**The number I did not have before, and it changes a gate.** Δ-B — the duplicated bank candidates
— fires **zero times** on 34 fixtures × 2 subjects. §5's G-b says "every naturally reached Δ-B
state"; on this library that set is empty, so the same-state fork would return green over nothing.
I did not run it and I am not reporting Δ-B as inert: counting is not measuring. G-b is BLOCKED on
a ruling about running it over a non-empty state set, with zero states recorded UNMEASURED.

**The reach is not scoped, and the record should say so.** Every EFFECT game's first selected tick
is exactly turn 100 — the replant block's own `view.turn>=100` guard. The scope lock justifies the
change by 101 idle turns in ONE game; the blast radius is 20 of 34 fixtures, two of which
(OSC-004, OSC-034) are games this change must never be reported as addressing. It changes their
streams; it is still not claimed to address them. No progress claimed, none measured — G-d and G-e
are not run, and per the build authorization no fixture-only result promotes this.

**Transport this wake.** ACKed codex_1's G-P review (`ACCEPTED_WITH_PLATFORM_CONDITION`,
`20260823T072259Z`) and their delivery ack. The platform condition is mine to hold and I hold it
unchanged: G-P is offline, so a green G-P and a wrong ladder position are compatible. The AAAAA
block's "delivered and reviewed" signal is now satisfied, but that card is `local_claude_1`'s — I
started no Arena run.

---

# claude_1 status — wake #66, 2026-08-23

**The replay→`Trace` adapter (D-1) is BUILT and delivered.** It had slipped one wake with a reason
owed; it did not slip a second. `agent/claude_1@bc814ba536df48e98f34a859b6fbdd7539cf75b4`, handed
off at `20260823T065400Z`, which discharges the card message it came from.

**What it is.** `replay JSON → (transcript text, commands text) → trace_detectors.build_trace →
Trace → detect_d1`. It emits **text**, so every parsing rule stays inside the accepted instrument;
an adapter that built `Trace` objects directly could disagree with it silently and its D-1 would
not be the same D-1. Layout measured over all 290 in-repo replays, not assumed: `frames = 2T+1`,
keyframes = frame 0 plus every even frame, strict seat alternation, `stdout` everywhere — and
`T = 300` in only 266 of them.

**The trap that mattered was not the named one.** The named 301-vs-300 truncation is *correct* by
luck. The dangerous case is a dropped mid-game keyframe: `T` states against `T` commands, the
length note does **not** fire, and every later state is one turn early with nothing on screen. The
adapter asserts `len(states) == T+1` and `resolved_turn == k` instead. Seat is required with no
default — a wrong seat joins our commands to the opponent's units and still prints numbers, and 72
of our lineage's 141 appearances here are at seat 1.

**Panel: 580 of 580 pairs, six controls, exit 0.** Two controls were INERT on first run and I fixed
the controls, not the adapter: a seat mutant that set an already-correct field, and a shift control
run on a game where D-1 fires zero episodes (0 == 0).

**The finding I reported instead of tuning away.** Sliding the *commands* one turn changes D-1 on
only **7 of 37** flagged pairs — D-1 reads positions from states and touches commands only for its
DROP/PICK clause, so **a command misalignment is very nearly invisible in D-1's own output**. The
detector cannot police its own join; only the adapter's assertions can.

**Not a prevalence result, and it must not be quoted as one.** `d1_flagged_pairs = 37` /
`d1_episodes_total = 77` is adapter coverage over 136 pseudonymous players including every
opponent. Our lineage is 141 of 580 pairs (`6536563`×140, `6536359`×1); the resident of record
`6561795` is in **none** of the 290. Plant clocks are reconstructed by `DiffDecoder`, which biases
D-1 toward **false** episodes, so replay counts are an upper bound. P4 stays inapplicable.

**NARRATE arrived mid-wake and took the front.** Owner-directed (`local_claude_1` `20260823T065100Z`):
instrument swap R-1 with intention logging, AAAAA on the ladder. Delivered the construction
proposal at `agent/claude_1@254cfa1581fc22e5766db32f1652538c2efe8604` — reuse PEEK rev 3's
`select_recording` and carry **none** of its displacement predicate; widen the single existing
`MSG` rather than push a second token, because two-`MSG` legality is unmeasured; `N1` grammar with
all five `Target` shapes and `None` printed as `N`, because a unit absent from the payload must be
a decode error, never a `None`. Budget measured against the corpus: maps ≤ 22×11 so one base-36
char per coordinate always fits, worst case 29 characters. **No instrument is built** and
`candidate-swap-r1.rs` is untouched; the build waits on codex_1's ruling plus the length figure.
Said before it passes: G-P runs offline and cannot see a referee reacting to command count or
payload length, so it can pass while the ladder position is still not swap R-1's.

**Second half of the wake: the NARRATE instrument, built and gated.** codex_1's construction r3
(`20260823T070405Z`) froze my readable v2 syntax; I built to it and **G-P PASSES 34/34 with 0
telemetry errors** at `agent/claude_1@e2dea6ae187a54fcb3a718865a6a0fe507d82439`. Three edits to a
copy: `select` → `select_recording` wrapper (lifted from PEEK rev 3, **predicate and resolver
deliberately not carried**), a tick-local target map in `commands()`, and one `MSG` inserted at
index 0 *after* the gameplay tokens exist — so the `if out.is_empty()` → `WAIT` fallback still runs
on gameplay alone and the instrument cannot suppress the base's `WAIT`. `candidate-swap-r1.rs`
re-hashed to `bbbb75d3…` after the work: untouched.

**The parity number is not trivially true** — base emits 1 `MSG` per game, instrument 200, and the
199 extra tokens per fixture are stripped before the byte comparison. 6,800 turn-lines were decoded
back and checked for roster completeness against the live own units in each state. **11 of 11
controls fired**, including the clean case and the two that would have manufactured the result: a
stripper that removes too much, and one that prefix-matches so `MSGX 1` would be eaten.

**And what G-P does not establish, said before the 34/34:** platform non-interference. This harness
does not react to command count, ordering or line length. A green G-P is compatible with the ladder
position not being swap R-1's, and I have not treated it otherwise.

**A blocker I raised and withdrew in the same wake.** codex_1's r2 grammar separated units with
`;` — the character the bot joins commands on and the referee splits them back on; our own panel
raises `unsupported_verb` on such a payload, which I measured rather than argued. r3 had already
frozen a `;`-free grammar before I published, so we crossed in flight. The measurement is kept, the
request withdrawn in the G-P handoff.

**Phase 3b is authorized and unblocked** (codex_1's r2 ruling `75085260…` — my card had named r1
`802e1388`, which the coordinator corrected — plus `20260823T063300Z`), and queued behind NARRATE.
No fixture-only result promotes it.

**Cards:** three, at `20260823T071201Z` — **Phase 3b is next and unblocked**, prevalence (b)
blocked, swap R-1 cure blocked. Both of the wake's build cards were delivered: the adapter (G-1
ACCEPTED) and the NARRATE instrument (G-P 34/34). **Open, and both codex_1's:** the G-P
parity-package review, and — not mine and not started by my delivery — the coordinator's AAAAA
block, whose signal is G-P delivered *and reviewed*.

# claude_1 status — wake #62, 2026-08-22

One review verdict inbound, acted on the same wake: **G-f REVISION_REQUIRED**, revised design out.

**Inbound.** `codex_1` `20260822T171000Z` (ack, no ack back) and `20260822T171001Z` (handoff,
ack-required) — pre-build design review of the Phase 3b proposal at `802e1388`, published at
`b8ce2a9e`. Verdict REVISION_REQUIRED, do not build. Two blocking findings, one required
clarification, one required extra falsifier. The ruled edit, the delta enumeration, the Δ-B
disclosure and the stateful-inertness argument were all accepted.

**The defect was real and mine.** r1's inertness gate required byte identity *through* the first
tick on which a candidate was rescued — but the intended success case is that the rescued `PICK`
is selected on exactly that tick, so the gate would have failed at the thing it was built to test,
and it contradicted r1's own falsifier 1. Second: r1 compared Δ-B turn-aligned across a paired
closed-loop run, which stops being a comparison once an earlier selected Δ-A moves the trajectory.

**Delivered.** `claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md` at `75085260`, handed
back at `20260822T171601Z` (supersedes the r1 handoff), with the ack at `20260822T171600Z`
accepting every item without dispute. Four repairs: (1) formation and effect boundaries separated,
per-game class keyed on `first_delta_a_selected_tick` — NO-EFFECT requires whole-game identity even
when Δ-A is *formed* and never selected, EFFECT requires identity strictly before the tick plus
recorded provenance on it; (2) Δ-B tested by a same-state fork on the recorded argument tuple plus
routing-branch id — sound because `main_candidates` is an associated fn with no `&self`, and chosen
over a memory clone because `YamoBot` does not derive `Clone` and adding one would edit the pinned
source; (3) the overloaded `rescued` label replaced by five explicit counters, with §2's
mutual-exclusion claim now a run-failing runtime assertion; (4) falsifier 5 — Δ-A selected, local
progress, new or worse P3/P4/r5-horizon event elsewhere is a stop, decided by the named-cost table
and not the panel mean.

**Added beyond the review:** a probe-shim inertness gate. The probe binary links a second generator
variant and recorders the shipped candidate must not, so the shipped source is diffed byte-for-byte
against the pinned source plus exactly the ruled hunk, and the panel arm is built from that source,
not from the probe. This programme has already shipped instruments that measured their own
instrumentation.

**Nothing built.** No candidate compiled, no probe, no panel, no Arena action, no candidate source
edited. Build stays DEFERRED behind two signals: codex_1's G-f acceptance of r2 **and** separate
written build authorization from local_claude_1. The corpus-prevalence card stays host-bounded and
untouched this wake.

# claude_1 status — wake #61, 2026-08-22

Two coordinator policies inbound, **both actionable** — the first substantive-work wake since the
standing cards went to UNBLOCK-SIGNAL format. Two of three named signals moved.

**Inbound.** `local_claude_1` `20260822T165022Z` (policy, ack-required): extend-versus-replace is
ruled — the `idle_regeneration && chops.is_empty()` fallback in `main_candidates` must EXTEND `out`,
not rebuild it; the Phase 3b design proposal is unblocked, the build is not. `local_claude_1`
`20260822T165627Z` (policy, ack-required, arrived mid-wake and caught by `--mark`): the corpus is
ruled and pinned — 21,496 games, 8,590 ours, `sha256 a882e528…`, on `project_host`; my
"resident not in the corpus" premise was true of the 290 git-tracked games and false of that corpus.

**Delivered.** `claude_1/picker3/phase3b-design-proposal-2026-08-22.md` at `802e13883faa`, handed to
codex_1 for the pre-build design ruling at `20260822T165801Z`. It adopts the ruled snippet verbatim,
enumerates the deltas exhaustively from the function's own guards (Δ-A the intended `PICK` rescue,
Δ-B a bank-candidate duplication the ruling did not name, mutually exclusive by the `carried`
split), and sharpens the inertness gate: selecting a rescued `PICK` writes `regeneration_commitments`
and reroutes the unit to `endgame_candidates`, so whole-game byte-identity is unsatisfiable by
construction on the games the change touches — restated as identity up to the first rescuing tick
plus whole-game identity where no rescue occurs, with a partition gate. Four named falsifiers, each
a stop rather than a patch. **Nothing built**; no candidate compiled, no probe, no panel, no Arena.

**Measured this wake, not recalled.** Storage preflight FAIL exit 2, unchanged; and new —
`hostname` is `compute-vm-4-16-20-ssd-1785607330087`, `data/processed/` holds only the three
git-tracked manifests here **and** in the sibling main checkout, no `games.jsonl`. The ruled corpus
is not reachable from my host, so the prevalence denominators are host-bounded even though the
corpus question is settled.

**Cards.** `20260822T165802Z` replaces `20260821T190413Z`. Anti-benching: design discharged, the
**build** stays deferred pending codex_1's design ruling **and** a separate build authorization.
Corpus-prevalence: **split** — (a) the replay→`Trace` adapter design is NEXT UP with no blocker and
no unblock-signal, first item of the next wake; (b) the prevalence measurement is blocked on host
reach, not on the corpus. Swap-r1: unmoved, and both of this wake's rulings say so explicitly.
Method rule adopted: count corpus membership by parsing, never by grep.

**Queue after this wake:** drained and pushed.

---

# claude_1 status — wake #57, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two messages — an `ack` on `20260821-corpus-prevalence`
(`20260821T183201Z`), `requires_ack: false`, receipting my carried card `20260821T182722Z` and
confirming it read the whole message including my receipts of both prior codex_1 messages, the
re-measured storage failure, the missing processed-corpus paths, the replay-adapter and P4
findings, the three cards, the unblock conditions and the cadence note; and a `progress` on
`20260821-standing-deferrals` (`20260821T183202Z`), `requires_ack: false`, addressed to
local_claude_1 with me cc'd, re-issuing codex_1's own two deferrals unchanged. The ack states
explicitly that it is a receipt only, claims no task, changes no gate, grants no authority and does
not take ownership of my card. Nothing is authorized: no corpus adapter, prevalence run, parser
rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena action.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous twenty-four wakes.

**Published:** `20260821T183601Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, twenty-fourth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T183601Z`.

---

# claude_1 status — wake #56, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two messages — an `ack` on `20260821-corpus-prevalence`
(`20260821T181331Z`), `requires_ack: false`, receipting my carried card `20260821T180848Z` and
confirming it read the whole message including my receipts of both prior codex_1 messages, the
re-measured storage failure, the missing processed-corpus paths, the replay-adapter and P4
findings, the three cards, the unblock conditions and the cadence note; and a `progress` on
`20260821-standing-deferrals` (`20260821T181332Z`), `requires_ack: false`, addressed to
local_claude_1 with me cc'd, re-issuing codex_1's own two deferrals unchanged. The ack states
explicitly that it is a receipt only, claims no task, changes no gate, grants no authority and does
not take ownership of my card. Nothing is authorized: no corpus adapter, prevalence run, parser
rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena action.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous twenty-three wakes.

**Published:** `20260821T182722Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, twenty-third consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T182722Z`.

---

# claude_1 status — wake #55, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two messages — an `ack` on `20260821-corpus-prevalence`
(`20260821T180129Z`), `requires_ack: false`, receipting my carried card `20260821T175649Z` and
confirming it read the whole message including my receipts of both prior codex_1 messages, the
re-measured storage failure, the missing processed-corpus paths, the replay-adapter and P4
findings, the three cards, the unblock conditions and the cadence note; and a `progress` on
`20260821-standing-deferrals` (`20260821T180130Z`), `requires_ack: false`, addressed to
local_claude_1 with me cc'd, re-issuing codex_1's own two deferrals unchanged. The ack states
explicitly that it is a receipt only, claims no task, changes no gate, grants no authority and does
not take ownership of my card. Nothing is authorized: no corpus adapter, prevalence run, parser
rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena action.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous twenty-two wakes.

**Published:** `20260821T180848Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, twenty-second consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T180848Z`.

---

# claude_1 status — wake #54, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two messages — an `ack` on `20260821-corpus-prevalence`
(`20260821T174916Z`), `requires_ack: false`, receipting my carried card `20260821T173146Z` and
confirming it read the whole message including my receipts of both prior codex_1 messages, the
re-measured storage failure, the missing processed-corpus paths, the replay-adapter and P4
findings, the three cards, the unblock conditions and the cadence note; and a `progress` on
`20260821-standing-deferrals` (`20260821T174917Z`), `requires_ack: false`, addressed to
local_claude_1 with me cc'd, re-issuing codex_1's own two deferrals unchanged. The ack states
explicitly that it is a receipt only, claims no task, changes no gate, grants no authority and does
not take ownership of my card. Nothing is authorized: no corpus adapter, prevalence run, parser
rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena action.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous twenty-one wakes.

**Published:** `20260821T175649Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, twenty-first consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T175649Z`.

---

# claude_1 status — wake #53, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two messages — an `ack` on `20260821-corpus-prevalence`
(`20260821T172731Z`), `requires_ack: false`, receipting my carried card `20260821T172259Z` and
confirming it read the whole message including my receipts of both prior codex_1 messages, the
re-measured storage failure, the missing processed-corpus paths, the replay-adapter and P4
findings, the three cards, the unblock conditions and the cadence note; and a `progress` on
`20260821-standing-deferrals` (`20260821T172732Z`), `requires_ack: false`, addressed to
local_claude_1 with me cc'd, re-issuing codex_1's own two deferrals unchanged. The ack states
explicitly that it is a receipt only, claims no task, changes no gate, grants no authority and does
not take ownership of my card. Nothing is authorized: no corpus adapter, prevalence run, parser
rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena action.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous twenty wakes.

**Published:** `20260821T173146Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, twentieth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T173146Z`.

---

# claude_1 status — wake #52, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two messages — an `ack` on `20260821-corpus-prevalence`
(`20260821T170915Z`), `requires_ack: false`, receipting my carried card `20260821T170417Z` and
confirming it read the whole message including my receipts of both prior codex_1 messages, the
re-measured storage failure, the missing processed-corpus paths, the replay-adapter and P4
findings, the three cards, the unblock conditions and the cadence note; and a `progress` on
`20260821-standing-deferrals` (`20260821T170916Z`), `requires_ack: false`, addressed to
local_claude_1 with me cc'd, re-issuing codex_1's own two deferrals unchanged. The ack states
explicitly that it is a receipt only, claims no task, changes no gate, grants no authority and does
not take ownership of my card. Nothing is authorized: no corpus adapter, prevalence run, parser
rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena action.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous nineteen wakes.

**Published:** `20260821T172259Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, nineteenth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T172259Z`.

---

# claude_1 status — wake #49, 2026-08-21

One inbound, non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's `20260821T162322Z` `ack`, `requires_ack: false`. Shape changed this wake —
one message, not the per-wake pair of the previous sixteen wakes. codex_1 folded its own
standing-deferrals re-issue into this ack on task `20260821-corpus-prevalence`, so **no cross-task
marker was needed** in my `ack_for` and its absence is not an omission. The ack receipts my carried
card `20260821T161850Z`, confirms it read the whole message including my receipts of both
`20260821T160504Z` messages, the re-measured storage failure, the missing processed-corpus paths,
the replay-adapter and P4 findings, the three cards, the unblock conditions and the cadence note;
it carries codex_1's own two deferrals (`20260821-swap-r1-cure`,
`20260820-pair-selector-anti-benching`) unchanged; and it states explicitly that it is a receipt
only, claims no task, changes no gate, grants no authority and does not take ownership of my card.
Nothing is authorized: no corpus adapter, prevalence run, parser rewrite, storage bypass, G-3,
widening, candidate edit, pre-build or Arena action.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous sixteen wakes.

**Published:** `20260821T162738Z`, self-addressed, ack-required, lint clean, acking codex_1's ack
and my own predecessor card, and carrying all three DEFERRED cards forward unchanged —
corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict → G-3 → G-4
chain, and the anti-benching Phase 3b design proposal. The coordinator note on the re-issue cadence
is restated once, sixteenth consecutive wake, not escalated, with codex_1's consolidation credited
as a real reduction in inbound volume but not a fix to the loop itself.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T162738Z`.

---

# claude_1 status — wake #47, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two `20260821T155251Z` messages — an `ack`, `requires_ack: false`,
receipting my carried card `20260821T154815Z` and confirming it read the whole message including my
receipts of both codex_1 messages, the re-measured storage failure, the missing processed-corpus
paths, the replay-adapter and P4 findings, the three cards, the unblock conditions and the cadence
note; and a `progress`, `requires_ack: false`, addressed to local_claude_1 with me cc'd, re-issuing
codex_1's own two standing deferrals unchanged. Neither authorizes anything or asks anything of me:
no corpus adapter, prevalence run, parser rewrite, storage bypass, G-3, widening, candidate edit,
pre-build or Arena action. The ack states explicitly that it is a receipt only, claims no task,
changes no gate and grants no authority.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous fourteen wakes.

**Published:** `20260821T160016Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, fourteenth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T160016Z`.

---

# claude_1 status — wake #46, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two `20260821T154102Z` messages — an `ack`, `requires_ack: false`,
receipting my carried card `20260821T152319Z` and confirming it read the whole message including my
receipts of both codex_1 messages, the re-measured storage failure, the missing processed-corpus
paths, the replay-adapter and P4 findings, the three cards, the unblock conditions and the cadence
note; and a `progress`, `requires_ack: false`, addressed to local_claude_1 with me cc'd, re-issuing
codex_1's own two standing deferrals unchanged. Neither authorizes anything or asks anything of me:
no corpus adapter, prevalence run, parser rewrite, storage bypass, G-3, widening, candidate edit,
pre-build or Arena action. The ack states explicitly that it is a receipt only, claims no task,
changes no gate and grants no authority.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous thirteen wakes.

**Published:** `20260821T154815Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, thirteenth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T154815Z`.

---

# claude_1 status — wake #45, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two `20260821T151921Z` messages — an `ack`, `requires_ack: false`,
receipting my carried card `20260821T151424Z` and confirming it read the whole message including my
receipts of both codex_1 messages, the re-measured storage failure, the missing processed-corpus
paths, the replay-adapter and P4 findings, the three cards, the unblock conditions and the cadence
note; and a `progress`, `requires_ack: false`, addressed to local_claude_1 with me cc'd, re-issuing
codex_1's own two standing deferrals unchanged. Neither authorizes anything or asks anything of me:
no corpus adapter, prevalence run, parser rewrite, storage bypass, G-3, widening, candidate edit,
pre-build or Arena action. The ack states explicitly that it is a receipt only, claims no task,
changes no gate and grants no authority.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous twelve wakes.

**Published:** `20260821T152319Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, twelfth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T152319Z`.

---

# claude_1 status — wake #44, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two `20260821T150051Z` messages — an `ack`, `requires_ack: false`,
receipting my carried card `20260821T145700Z` and confirming it read the whole message including my
receipts of both codex_1 messages, the re-measured storage failure, the missing processed-corpus
paths, the three cards, the unblock conditions and the cadence note; and a `progress`,
`requires_ack: false`, addressed to local_claude_1 with me cc'd, re-issuing codex_1's own two
standing deferrals unchanged. Neither authorizes anything or asks anything of me: no corpus
adapter, prevalence run, parser rewrite, storage bypass, G-3, widening, candidate edit, pre-build
or Arena action. The ack states explicitly that it is a receipt only, claims no task, changes no
gate and grants no authority.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous eleven wakes.

**Published:** `20260821T151424Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, eleventh consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T151424Z`.

---

# claude_1 status — wake #43, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's two `20260821T144850Z` messages — an `ack`, `requires_ack: false`,
receipting my carried card `20260821T144415Z` and confirming it read the whole message including
the re-measured storage failure, the missing processed-corpus paths, the three cards, the unblock
conditions and the cadence note; and a `progress`, `requires_ack: false`, addressed to
local_claude_1 with me cc'd, re-issuing codex_1's own two standing deferrals unchanged. Neither
authorizes anything or asks anything of me: no corpus adapter, prevalence run, parser rewrite,
storage bypass, G-3, widening, candidate edit, pre-build or Arena action. The ack states explicitly
that it is a receipt only, claims no task, changes no gate and grants no authority.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous ten wakes.

**Published:** `20260821T145700Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. A cross-task marker records why
`ack_for` names the standing-deferrals progress. The coordinator note on the re-issue cadence is
restated once, tenth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T145700Z`.

---

# claude_1 status — wake #42, 2026-08-21

One inbound, non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's `20260821T143638Z` — an `ack`, `requires_ack: false`, receipting my carried
card `20260821T142035Z` and confirming it read the whole message including the re-measured storage
failure, the missing processed-corpus paths, the three cards, the unblock conditions and the
cadence note. It authorizes nothing and asks nothing of me: no corpus adapter, prevalence run,
parser rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena action. It states
explicitly that it claims no task, changes no gate and grants no authority, and restates all three
of my blocks as still blocked on the same three written rulings.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous nine wakes.

**Published:** `20260821T144415Z`, self-addressed, ack-required, lint clean, acking codex_1's
message and my own predecessor card, and carrying all three DEFERRED cards forward unchanged —
corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict → G-3 → G-4
chain, and the anti-benching Phase 3b design proposal. The coordinator note on the re-issue cadence
is restated once, ninth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T144415Z`.

---

# claude_1 status — wake #41, 2026-08-21

Two inbound, both non-actionable, nothing unblocked, no new work started.

**Inbound:** codex_1's `20260821T141456Z` — an `ack`, `requires_ack: false`, receipting my carried
card `20260821T141022Z`; and codex_1's `20260821T142025Z` — a `progress`, `requires_ack: false`,
addressed to local_claude_1 with me cc'd, re-issuing codex_1's own two standing deferrals
unchanged. Neither authorizes anything or asks anything of me: no corpus adapter, prevalence run,
parser rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena action. The ack
states explicitly that it does not discharge my cards. Their swap-r1 verdict stays
`PACKAGE_REPRODUCED; BLOCKED AT G-1` with the 13 residual OSC-011 re-swaps still failing the
fail-first condition.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous eight wakes.

**Stamp note:** codex_1's `20260821T142025Z` carries a `created_utc` ahead of this host's clock at
the time I read it (14:19:40Z). My replacement card is stamped after that instant so it never
claims to ack a message that had not yet been created on my clock; the drift itself is recorded,
not corrected.

**Published:** `20260821T142035Z`, self-addressed, ack-required, lint clean, acking both of
codex_1's messages and my own predecessor card, and carrying all three DEFERRED cards forward
unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict →
G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. The coordinator note on the
re-issue cadence is restated once, eighth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T142035Z`.

---

# claude_1 status — wake #40, 2026-08-21

One inbound, nothing unblocked, no new work started.

**Inbound:** codex_1's `20260821T135719Z` — an `ack`, `requires_ack: false`, receipting my carried
card `20260821T135149Z`. It authorizes nothing and asks nothing of me: no corpus adapter,
prevalence run, parser rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena
action. It states explicitly that it does not discharge my cards. Their swap-r1 verdict stays
`PACKAGE_REPRODUCED; BLOCKED AT G-1` with the 13 residual OSC-011 re-swaps still failing the
fail-first condition, and they re-issue their own two deferrals self-addressed.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous seven wakes.

**Published:** `20260821T141022Z` (commit `8b4dfdc5`), self-addressed, ack-required, lint clean,
acking both codex_1's message and my own predecessor card, and carrying all three DEFERRED cards
forward unchanged — corpus-prevalence (all four deliverables and both gates), the swap-r1
G-2-verdict → G-3 → G-4 chain, and the anti-benching Phase 3b design proposal. The coordinator note
on the re-issue cadence is restated once, seventh consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T141022Z`.

---

# claude_1 status — wake #38, 2026-08-21

One inbound, nothing unblocked, no new work started.

**Inbound:** codex_1's `20260821T133453Z` — an `ack`, `requires_ack: true`, receipting my carried
card `20260821T131800Z`. It authorizes nothing and asks nothing of me: no corpus adapter,
prevalence run, parser rewrite, storage bypass, G-3, widening, candidate edit, pre-build or Arena
action. It states explicitly that it does not discharge my cards. Their swap-r1 verdict stays
`PACKAGE_REPRODUCED; BLOCKED AT G-1` with the 13 residual OSC-011 re-swaps still failing the
fail-first condition, and they re-issue their own two deferrals self-addressed.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, condition 2 unanswered, condition 3 holds — parked, not degrading. Byte-identical to the
previous five wakes.

**Published:** `20260821T134259Z`, self-addressed, ack-required, lint clean, acking both codex_1's
message and my own predecessor card, and carrying all three DEFERRED cards forward unchanged —
corpus-prevalence (all four deliverables and both gates), the swap-r1 G-2-verdict → G-3 → G-4
chain, and the anti-benching Phase 3b design proposal. The coordinator note on the re-issue cadence
is restated once, fifth consecutive wake, not escalated.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T134259Z`.

---

# claude_1 status — wake #36, 2026-08-21

One inbound, nothing unblocked, no new work started — plus one correction of record.

**Inbound:** codex_1's `20260821T125445Z` — an `ack`, `requires_ack: false`, receipting my
replacement card `20260821T124754Z`. It confirms from their side that all four corpus-prevalence
deliverables and both gates stay blocked, that no adapter / prevalence run / P4 column / parser
rewrite / storage bypass is authorized or started, and that the swap-r1 alpha stays
`PACKAGE_REPRODUCED; BLOCKED AT G-1` with no G-3 and no widening. It asks nothing of me.

**Re-measured this wake, not recalled:** `cgauto/check_external_storage.py --intent read` →
`storage preflight: FAIL` (exit 2), no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, no ruling on condition 2, condition 3 holds — parked, not degrading.

**Correction of record:** `20260821T122510Z` carried the two swap-r1 alpha deferrals but was
addressed to codex_1 and local_claude_1, not to myself. codex_1's `20260821T123322Z` acked it, so
this wake's sweep no longer lists it — the two cards were discharged as a handoff-ack while the
work is still blocked and undelivered. Both are re-issued self-addressed in this wake's message,
unchanged in substance: the G-2-verdict → G-3 → G-4 chain (blocked on the unanswered cure-arm gate
amendment and the residual 13 OSC-011 re-swaps) and the anti-benching Phase 3b design proposal
(blocked on the owner's extend-versus-replace ruling on `idle_regeneration`).

**Published:** `20260821T125938Z`, self-addressed, ack-required, lint clean, carrying all three
cards, plus a note to the coordinator proposing — not adopting — a signal-keyed re-issue cadence,
since three consecutive wakes have produced a byte-identical measurement and a fresh card.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force, all in
`20260821T125938Z`.

---

# claude_1 status — wake #35, 2026-08-21

One inbound, nothing unblocked, no new work started.

**Inbound:** codex_1's `20260821T124255Z` — an `ack`, `requires_ack: false`, acknowledging my
re-measured deferral of `20260821-corpus-prevalence`. It confirms from their side that the task
stays wholly deferred, that no adapter / prevalence run / P4 column was started, that the
instrument-first and exact-P4 concerns remain open rather than silently resolved, and that codex_1
is starting neither G-3 nor any swap-r1 widening. It asks nothing of me.

**What I owed:** a peer ack cannot discharge a self-addressed `DEFERRED:` card — only a delivery or
a replacement card can. The block is unchanged, so I published the replacement at
`20260821T124754Z` (`ack_for` my own `20260821T124100Z`, self-addressed, ack-required, lint clean).

**Re-measured this wake, not recalled:** `check_external_storage.py --intent read` →
`storage preflight: FAIL`, no `medium_data` label and no `troll-farm-data:archive` mount;
`data/processed/games.jsonl` absent; `data/processed/trajectories/` absent. Unblock condition 1
unmet, no ruling on condition 2, so condition 3 holds — parked, not degrading.

**Swap-r1 alpha:** unchanged at `PACKAGE_REPRODUCED; BLOCKED AT G-1`. Question 3 (what replaces
"005/012/001 must turn FIXED" for a cure arm) is an owner/coordinator gate amendment and is still
unanswered, so the G-2-verdict → G-3 → G-4 chain and the anti-benching Phase 3b proposal stay
parked under their existing cards in `20260821T122510Z`; this wake did not duplicate or replace
them.

**Queue after this wake:** drained and pushed. Three DEFERRED cards in force — corpus-prevalence
(`20260821T124754Z`), and the two in `20260821T122510Z`.

---

# claude_1 status — wake #33, 2026-08-21

One message in, no ack owed by me (codex_1's Phase 3a acceptance is `type: ack`), and the wake's
work was the ruling that had been sitting unexecuted since 11:05: **codex_1 approved the P5
narrowing at `20260821T110533Z` two minutes after I published an ack still describing alpha as
"awaiting their ruling".** It is executed now.

**Task `20260821-swap-r1-cure` — cure alpha rev 2 built, G-1 rev 2 and the amended G-2 measured**
(`20260821T122510Z`, commit `65c716b3`). The build is one predicate line, and the builder refuses
to write unless rev 2 equals rev 1 with exactly that substitution; rev 1 rebuilds byte-identically.

- **G-1 rev 2:** four gates PASS, ruling 4 FAILS at **13** (was 111). Fires 52 → 25, all yield-path.
  **OSC-006 never fires and its whole game is byte-identical to the base.** The residual 13 are all
  OSC-011 — the widening case, still owner-blocked. Controls **11/11**, with the deleted
  working-partner path **asserted** by inverting `T4b` rather than deleting it.
- **Amended G-2, primary bar: PASSES.** Matched 240-game panel, **D-1 27 → 9, P4 16 → 0, zero new**
  of either shape, 210/240 games byte-identical, 20 changed games all named. The base P4 column is
  the accepted mode, not the reduced one — the floor panel was run beside it and **Gate M** proves
  all 240 games are byte-identical on the base arm before a count is printed.
- **Amended G-2, baskets: NOT met.** OSC-005 is a substantive miss (alpha fires at turn 52, the
  episode is turns 7–18). OSC-001/012 are **unanswerable**: the identity gate asks whether a run
  replays the recorded window, so it rejects exactly the fixtures a cure reached — measured
  **7 for 7** over the 11 that reproduce on the base. Not worked around; handed back.
- One other panel shape grew (P3, m004 seat 0) and the explanation is computed, not asserted: the
  floor's P3 column is 0 **by construction**, so the comparison is vacuous.

**Three questions handed back** — the residual 13 vs ruling 4, P3 applicability, and what replaces
"005/012/001 must turn FIXED" for a cure arm.

**Queue after this wake:** drained and pushed. Two DEFERRED cards in force, both in
`20260821T122510Z`: the α G-2 verdict → G-3 → G-4 chain, and the anti-benching Phase 3b design
proposal (blocked on the owner's extend-vs-replace ruling on `idle_regeneration`).

---

# claude_1 status — wake #30, 2026-08-21

Two deliveries this wake, both handed off and both requiring codex_1.

**1. Task `20260821-swap-r1-cure` — the G-1 remedy diagnostic (`20260821T104500Z`).** Built to
codex_1's ruling: probe only, no candidate edit, no cooldown, no widening. The candidate and both
controls are byte-unchanged; only `probe-swap-r1.rs` gained a line. Three findings.
**Pass-through viability is INVERTED here** — it keeps 27/27 OSC-006 dance fires and rejects both
clean working fires (005, 012), which are arrive-and-stay and can never pass through. **98 of the
111 re-swaps are the no-detour/working-partner path, and that path fires nowhere else in the
34-fixture corpus**, so a yield-only predicate kills them with no measured cost — but it deletes
an accepted behaviour, so codex_1 rules. **OSC-011's 13 are not separable at the seam**: its dance
fires share a bucket with OSC-005/012 on every recorded seam field. Minimum widening named
(planner targets for WAIT units), not built. Artifacts at `c9b78245`.

**2. Task `20260821-episode-identity-regrade` — all four deliverables (`20260821T105300Z`).** The
two-part identity gate is lifted byte-identically into `claude_1/t1/fixture_harness.py`; `grade()`
now REFUSES to run without an identity verdict and returns `NOT_REPRODUCIBLE_ON_BASE` for a run
that is not the recorded episode. Champion re-grade: **8 FIXED → 0**, 11 NOT_FIXED, 23
NOT_REPRODUCIBLE — the 11 reproducing fixtures are exactly the ones local_claude_1 named, reached
independently. Two of the 23 (OSC-032/033) are caught by the entry board ALONE, which is the
non-vacuity evidence for the second half. 17/17 self-test, 11/11 controls. Artifacts at `5d54a723`.

**Queue after this wake:** anti-benching Phase 3a, deferred with a self-addressed replacement card
(`20260821T105500Z`) and one correction already attached — 013/017 reproduce on the champion,
004/034 do not.

---

# claude_1 status — wake #29, 2026-08-21

Task `20260821-swap-r1-cure`: **G-0 rev 2 ACCEPTED by codex_1, α BUILT, G-1 BLOCKED by its own
re-swap gate.** Package `claude_1/swap1/g1-package-2026-08-21.md`, handoff `20260821T103200Z`
(requires_ack). Five G-1 gates pass — probe parity, shadow inertness on 6,800 ticks, whole-game
identity on the 18 zero-fire fixtures, pre-first-fire identity everywhere, and a non-zero trigger
count. The sixth, ruling 4's re-swap detector, **fails at 111**: OSC-006 trades the pair {0,2} on
27 consecutive ticks, OSC-011 on 6. I did not invent a cooldown; three remedies are named, a
progress conjunct is recommended, and the ruling is codex_1's. **DEFERRED card in force:** G-1
rev 2 then G-2..G-4.

Secondary, and it bounds G-2: **OSC-027 never fires** (its recorded stall does not reproduce under
the base — the re-run problem measured at wake #27), and the card's "back on the tree within 2
ticks" is **untested**, because all 27 work-displacing fires sit inside OSC-006's dance.

---

# claude_1 status — wake #26, 2026-08-21

Task `20260821-osc032-033-cause-attribution`: **CLOSED — all three gates ACCEPTED.** codex_1
returned **G-3 ACCEPTED** this wake (`20260821T090757Z`), reproduced from a detached worktree at
`e8034b79`, all three generated JSON artifacts byte-identical to the pin. Their `ack_for` names my
G-3 handoff exactly, which retires my r3 card; they declared **no deferrals and no replacement
card**. Queue drained: 1 new, 0 ack-required, no card of mine outstanding.

Task `20260815-oscillation-deep-dive`: the one item I carried open from wake #25 is now
**dispositioned and published** (`20260821T091400Z`, commit `3a690980`).

## What arrived

One message, not ack-required, read in full:

- **codex_1 `20260821T090757Z` — G-3 ACCEPTED.** The amended questions are answered and the
  controls bite. They record, explicitly, that the accepted scope is **measurement only**: it does
  not decide bug versus correct caution, does not explain OSC-032's unbanked reachable plum, and
  authorizes no fix, no candidate, no class-wide claim and no Arena action. Their review is
  `codex_1/reviews/osc032-033-cause-attribution-g3-review-2026-08-21.md`. One thing to carry: they
  state the opponent-independent grace-only bound as **at most 5/110 and 0/143** real window
  turns; my note states the same bound as 105/110 and 143/143 turns *excluded*. Same measurement,
  complementary phrasing — 110 − 5 = 105. No discrepancy.

## The carried-open item, closed by DETECTION rather than a source fix

`build_oscillation_library.py:808` defaults `--out` to the **STALE** parent-lineage tree.

**I did not change the default, and that is the substantive decision.** The file's SHA-256
`4b9fce4c…` is pinned in the artifact tables of `oscillation-library-2026-08-10.md` and
`oscillation-library-subject-correction-2026-08-11.md`, and the **authoritative**
`oscillation-library-98628e98/` tree rests its provenance on that builder being *unmodified*
(`oscillation-library-98628e98/README.md:28`; `build_subject_library.py` imports it and reuses
`harvest`/`dedupe`/`write_library` verbatim). Making `--out` required would falsify an attestation
two already-accepted artifacts depend on — a worse defect than the hazard. Builder verified
byte-identical to the pin after this wake's work.

**The hazard, measured.** Both other arguments are `required=True`, so a bare invocation is
impossible; the trap needs `--games`/`--panel-config` supplied and `--out` omitted. `write_library`
unlinks `*.json` **only**, so README.md *survives* the overwrite and is left describing 33 cases
that are gone — a false document at the exact path the marker exists to protect.

**Detection was already two-thirds built.** `TestParentLineageIsLabelled` already pinned
`library_sha256` to `5858d351…` and asserted the index's `WRONG SUBJECT` note (which a rebuild
drops, since `write_library` never writes that field). Neither covers the README. I added
`test_the_stale_readme_still_describes_the_tree_it_sits_in`, which ties the README's ID-map rows to
the `OSC-*.json` files actually present.

**Three controls executed against throwaway `tempfile` copies — the real tree was never written:**

| control | expected | observed |
|---|---|---|
| untouched copy | all 4 pass | all 4 pass, hash matches pin, 33 cases |
| default-run overwrite (5 cases) | tree tests **and** README test fire | all 3 fire: `8bd2a0f4…` ≠ pin, `subject_note` KeyError, ID map 5 ≠ 33 |
| README deleted, tree intact | **only** the new test fires | exactly the new test fires |

The third is the one that earns the test: it proves the new leg is not redundant with the two that
already existed. Full suite **95 tests OK, 2 skipped** (opt-in `rustc` replay); the two
`INTEGRITY FAILURE` lines in that output are fail-closed tests passing.

**Scope, stated honestly.** This is containment, not prevention. The overwrite remains possible;
it can no longer happen quietly. The stale README now carries the trap and the reason the default
was not fixed, at its head.

## Standing limits that survive this wake

- G-3's accepted scope is **measurement only**. Bug versus correct caution is the owner's ruling,
  not mine and not codex_1's.
- The eleven unobserved plant-rejection clauses, and OSC-032's 52 turns where H-C's generator was
  never entered, remain UNOBSERVED — not refuted.
- OSC-032's unbanked reachable plum is **not measured and not claimed**.
- `items_the_shack_never_held_enough_of` and `items_no_live_source_ever_existed_for` stay strictly
  apart; collapsing them overstates H-A.

## Open

Nothing. No card outstanding, none deferred, none requested. Queue drained and pushed.
