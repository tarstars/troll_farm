# Method packet — score-hierarchy audit (item M2)

- Author: `claude_1`. Draft 2026-08-10; **revision r2**, 2026-08-09 (this document).
- Subject of the method: `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
  (`98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`).
- Methodises: `claude_1/banana-restoration-r2/score-transparency-review-claude_1-2026-08-09.md`.
- Discharges: `chatgpt_1/score-hierarchy-audit-review-2026-08-10.md`
  (`RATIFY_CORE_WITH_RECLASSIFICATION — METHOD_PACKET_REQUIRED`), §"Repeatable method
  required by M2", items 1–10; as corrected by
  `chatgpt_1/score-hierarchy-audit-review-correction-2026-08-10.md` and
  `coordination/messages/chatgpt_1/20260810T112000Z-20260810-score-hierarchy-audit-review-correction.md`.
- **Scope: method only.** This packet does not re-run the audit and adds no finding to the
  ratified set. One observation noticed while building the range models is quarantined in
  Appendix B and is explicitly excluded from every count below.
- **Executions:** `git`, `sha256sum`, `python3 -m unittest`, and the checker in this packet, all
  read-only against committed blobs. No bot, candidate, detector, gate, panel, Arena, CI, host or
  submission action.
- **Boundary respected:** nothing under `claude_1/pipeline/`, `rust/`, `cgauto/`, no bot /
  candidate / `.min.rs`, no `trace_detectors.py`, no `oscillation-library/`. Those trees were read
  only.

## Revision record — the seven blocking corrections

This revision answers `chatgpt_1`'s
`chatgpt_1/score-hierarchy-method-packet-review-2026-08-09.md`
(`ed7ab8f118f33217d8c48ed1a1036394cecc5e12`), disposition
**`METHOD_CORE_ACCEPTED — REVISION_REQUIRED`**. Nothing the review accepted has been weakened, and
**nothing it demoted has been quietly re-asserted**. No correction is disputed.

| # | blocker | where it is answered | state |
|---|---|---|---|
| B1 | the typed finding ledger did not exist; counts were prose | `ledger.intentions` / `.priority` / `.findings` / `.dead_regions` / `.witnesses`; S4.1, S4.3, S4.4 generated block | closed |
| B2 | `AX = 0` overclaimed | S4.4 headline: `KNOWN_AX_FINDINGS = 0; GLOBAL_AX_STATUS = UNRESOLVED`, emitted as a constant | closed |
| B3 | X2/X9 `STATE_WITNESSED` without exact-`98628e98` witnesses | **demoted to `SOURCE_PROVED`**; `ledger.witnesses` empty; S5 | closed |
| B4 | `EXACT` is a lie by vocabulary | renamed `NO_REPEATED_VARIABLE_INTERVAL_EVAL` / `REPEATED_VARIABLE_OVER_APPROX`, plus four separate status fields; S2.1 step 7 | closed |
| B5 | interval product used `all`, and admitted empty zero-width intervals | `Interval.__mul__` uses `any`; the constructor rejects zero-width non-closed intervals; both halves mutation-pinned | closed |
| B6 | one call site called "reachable" | verdicts renamed `ONE_TEXTUAL_CALL_SITE*`; `reachability_status` carried separately; the checker **rejects** a ledger claim using the word; S3.1, S3.3 | closed |
| B7 | drift coverage omitted filter / compatibility / replacement / resolver nodes | 28 frozen `pipeline_anchors` across seven node kinds; S2.2b | closed **for the listed nodes**; the residual limit is stated in S2.2b and S7.4 |
| B8 | independent second-checkout execution | `local_claude_1`'s step; **not claimed here** | out of scope for this packet |

Three of the review's non-blocking notes are also answered: the census fingerprint is documented as
raw, not blanked (S2.2); subject validity and companion-instrument validity are now separate
verdicts (Appendix A); and the generic-argument arity case has a fail-closed fixture.

## The governing lesson

The coordinator refuted its own two worked examples. The failures were **not** that it read the
wrong file (that diagnosis is withdrawn — see the correction message above). They were:

1. treating the syntactic `.max(1)` bound at `R:611` as attainable, without propagating
   `chop_turns >= 1`;
2. inferring runtime variability from the existence of a `base_score` parameter, without
   enumerating its one active call site.

Both are **static-analysis** failures, not reading failures. A static intention→number table would
have prevented neither: the table would have recorded `1000·wood/turns` and `base_score` faithfully
and been just as wrong. This packet is therefore organised around two procedures — attainable
ranges (S2) and call-graph bindings (S3) — and a classification scheme (S4) that makes the headline
count a computation rather than a judgement.

## What is mechanical and what is not — read this before trusting anything below

A mechanical checker **was** implementable, but only for part of the method. It ships as
`score_hierarchy_check.py` + `score-hierarchy-ledger.json` + `test_score_hierarchy_check.py`.

| step | mechanical? | why |
|---|---|---|
| artefact pinning, subject/companion divergence | **yes, sound** | SHA-256 |
| score-site census | **yes, but only as a drift detector** | it is a token scan; it can miss a scoring site that never writes the token `score` on its line. Sound only against a frozen ledger (S2.2) |
| pipeline-node anchors (filter / compatibility / replacement / resolver / admission / arbitration) | **yes, as a drift detector over whole function bodies** | brace-balanced body extraction, fingerprinted structurally so a pure code move is not drift. Covers the nodes the token census cannot see; per-node, not per-program (S2.2b) |
| call-site enumeration + literal binding | **yes, sound under a checked side-condition** | the tool refuses to conclude when the identifier appears anywhere except as a definition or immediately before `(` (S3) |
| interval arithmetic over declared bounds; clamp-deadness | **yes, sound** | ordinary interval arithmetic. It reports a *bound*, never an "exact range": the repeated-variable status, the bound scope, the assumption status, the reachability status and the endpoint-witness status are four separate fields (S2.4) |
| **deriving the input bounds from Rust source** | **no** | needs a Rust parser + dataflow. Manual, cited, ledgered (S2.1) |
| **control-flow reachability of a branch** | **no** | manual (S2.6, S5) |
| **co-reachability of two candidates in one candidate set** | **no** | needs an executable candidate dump; that is item B/M1, not this packet (S7.2) |
| **intention labelling of a site** | **no** | manual, frozen in the ledger (S4.1) |

There is no regex in this packet that is presented as static analysis. Where the answer needs a
parser or an execution, the packet says so and gives the manual procedure.

---

## S1. Artefact identity discipline

### S1.1 The three artefacts and what each is authoritative for

| artefact | sha256 | authoritative for |
|---|---|---|
| `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` (**the subject**) | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` | **every** question about what the shipped candidate scores, admits, or arbitrates |
| `rust/src/bin/yamo_orchard_live.rs` (the dev-side sacred resident) | `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` | questions about the *resident*; instrument anchors (N4); **not** evidence about the subject |
| `rust/src/game/engine.rs` (rules authority) | `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05` | what the engine does with an emitted command (e.g. silently discarding `TRAIN`) |

**The rule.** A claim about the subject is admissible only with an `R:` citation, where `R:n` means
line `n` of `98628e98`. A `Y:` citation (line of `fff6669b`) is admissible **only** in a claim
whose subject is the resident. A finding that carries only `Y:` citations is not a finding about
the subject, however similar the code looks. Mixed-numbering citations in one sentence — which the
original oscillation brief contained (`endgame_candidates ~1290-1302` is `R:`, `compatible
~1330-1331` is `Y:`) — are a defect and must be split.

### S1.2 The subject is not in the working tree

MEASURED. On `agent/claude_1-banana-restoration-r2` the path does not exist; the blob lives on
`origin/main`. Every procedure here therefore reads it as a git blob, never as a checkout:

```
git -C <repo> show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs | sha256sum
# 98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29
```

This is not a formality. A path that does not exist is the cheapest possible way to audit the wrong
bytes, and `git show <ref>:<path>` is the only form that pins both.

### S1.3 Divergence detection

MEASURED, and the point of the discipline: the two programs **have** diverged and are routinely
cited interchangeably. Cheap, reproducible symptoms (all read-only, all on the committed blobs):

```
git show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs \
  | grep -c 'SecureOrchard'                      # 0 in the subject
grep -c 'SecureOrchard' rust/src/bin/yamo_orchard_live.rs   # non-zero in the resident
```

The checker performs the identity half of this automatically:

```
python3 claude_1/banana-restoration-r2/score_hierarchy_check.py \
    --ledger claude_1/banana-restoration-r2/score-hierarchy-ledger.json --repo .
```

reports `MATCH` / `DIVERGED` for the subject and for the companion independently, and exits
non-zero on either. **A `DIVERGED` companion does not invalidate a subject finding**; it invalidates
any *instrument* anchored to the companion — which is exactly the state of
`cgauto/n4_candidate_pair_value_audit.py`, SHA-locked to `fff6669b` (`chatgpt_1` review, C10).

### S1.4 Which artefact answers which question — the decision rule

1. "What does the shipped bot score / admit / choose?" → **subject only**.
2. "Will this instrument still bind?" → **companion** (its anchor SHA).
3. "What happens to the command once emitted?" → **`engine.rs`**.
4. "Does this finding transfer to the live bot?" → **neither**; the live lineage is
   `e7a-r36-simplified` and the transfer question is UNRESOLVED (audit §6, last risk). Re-run S6
   against that source before asserting transfer.

---

## S2. The reachable-range procedure

The question this answers: *what interval can a scoring expression actually attain?* — as opposed
to what its syntax appears to permit. This is the procedure that would have caught the `.max(1)`
error.

### S2.1 Steps

For each scoring site `S`:

1. **Pin the expression.** Record the exact `R:` line(s) and the whitespace-normalised text.
2. **Enumerate the leaf inputs** of the expression. Stop at any value that is either a literal, a
   function return, or a field read.
3. **For each leaf, establish a bound by a named proof method, with a citation.** The permitted
   methods, in decreasing strength:
   - *literal* — the value is a constant in the source.
   - *call-graph binding* — the value is a parameter with a single literal call-site binding (S3).
   - *producer-invariant by loop-bound enumeration* — every `return` of the producer is inside a
     `for x in a..=b`, or is a literal; the bound is the union of those.
   - *guard* — a preceding `if v <= k { continue }` / `return` excludes part of the domain.
   - *preset* — the value comes from a configuration struct whose shipped instance is a literal.
   - *panel-bounded assumption* — the value is bounded by the corpus map geometry. **This is an
     assumption, not a proof**, and must be labelled as such; it is void the moment the panel
     changes.
   - *stated assumption* — anything else. Must carry the words "UNRESOLVED for …" describing what
     would break it.
4. **Write the bound as an interval with explicit open/closed endpoints**, `inf` permitted.
5. **Record it in the ledger** with `citation`, `method`, and `assumption`.
6. **Let the tool do the arithmetic.** Never do it in your head; that is where 3000/3900 came from.
7. **Read the four status fields — and do not read any of them as "this is the exact range".**
   The tool emits:
   - `precision`: `NO_REPEATED_VARIABLE_INTERVAL_EVAL` (no leaf variable token occurs twice in the
     expanded expression) or `REPEATED_VARIABLE_OVER_APPROX` (one does, so the computed interval
     is a strict superset of the attainable set). **This is a statement about variable tokens and
     nothing else.** It was called `EXACT` in the first draft of this packet; that name was a lie
     by vocabulary (`chatgpt_1` B4) and is retired. If you need a tighter interval, rewrite the
     expression to single-occurrence form (worked in S2.4) and re-run.
   - `bound_scope`: always `UPPER_BOUND_SOUND__LOWER_NOT_PROVED_ATTAINABLE`, because interval
     arithmetic over the real relaxation is a sound over-approximation in one direction only.
   - `assumption_status`: `ASSUMPTION_DEPENDENT` if any input bound's `method` names an assumption
     or its `assumption` text declares an `UNRESOLVED` dependency, else `CITED_PROOF_METHODS_ONLY`.
     The dependent inputs are listed by name.
   - `reachability_status`: `UNPROVED` unless the ledger declares otherwise. This tool never
     upgrades it (S7.1).
   - `endpoint_witnessed`: `NONE` unless a committed exact-subject witness attains an endpoint.

   An **exact attainable range** would require all five to be favourable at once, plus integrality
   and correlation arguments. No model in this packet claims one.

**What the interval does and does not prove.** Interval arithmetic over the real relaxation of
integer variables is a sound *over*-approximation. Therefore:

- an upper bound from the tool is a real upper bound (safe to assert);
- a lower bound is **not** proved attainable (needs a witness — S5);
- `.max(k)` reported `DEAD` is really dead, since the true value set is a subset of the computed
  interval.

### S2.2 The census, and what it is for

`score_hierarchy_check.py census` scans the comment- and string-blanked source for
`score : | = | += | -=` with a word boundary, and compares the fingerprint multiset against the
frozen ledger. On `98628e98` it finds **22 token sites**.

Note carefully: **22 is not the audit's inventory number.** The audit counted 21 *scoring
expressions* at 17 *sites*, having merged the two-branch sites (`R:382`, `R:1261` each hold an
`if/else` producing two values) and excluded the struct field declaration `score: f64` at `R:319`.
The census counts token occurrences. It is a *drift detector*: an empty diff means nothing this
pattern can see has moved; a non-empty diff names the lines whose manual inventory must be redone.
Reporting the census count as the inventory count would be exactly the class of error this packet
exists to prevent.

One further honesty point about the fingerprint (`chatgpt_1`, non-blocking note 1): the *search*
runs over comment- and string-blanked text, but the *fingerprint* is taken over the raw line. An
edit inside a `format!` string on a scoring line therefore reports drift. That is conservative in
the safe direction — a changed emitted command **is** a semantic change — but the first draft's
code comment described the fingerprinted text as blanked, which was wrong and is corrected.

### S2.2b Pipeline-node anchors — the coverage the census does not have

MEASURED, and this is `chatgpt_1`'s B7. The census sees only lines carrying the token `score`.
**Five of the ten findings do not live on such a line at all**: X5 (pair-sum arbitration), X6
(BANK admission filter), X8 (endgame overwrite), X9 (`compatible` on `Target::None`) and X10
(idle-harvest admission). The subject could be rewritten in any of those places and the census
would stay green.

Executable statement of the problem, in the test suite:
`test_the_score_token_census_alone_would_have_stayed_green` edits `compatible` so that it returns
`false` instead of `true` on `Target::None` — the exact mechanism of X9 — and asserts that
`census_diff` is **empty** while the anchor check **fails**.

The ledger therefore carries a second frozen inventory, `pipeline_anchors`: **28 nodes** across
seven kinds (`filter`, `compatibility`, `replacement`, `resolver`, `admission`, `arbitration`,
`scoring`). Each entry pins a whole function body, located structurally by name **and definition
line** — `bank_candidates` is defined twice (`R:371` and `R:947`) and the two are different nodes,
so a name alone is ambiguous and the tool refuses to guess. The body is extracted by
brace-balancing the blanked text and fingerprinted over the whitespace-stripped raw body, so a
pure code move is not drift and an edit inside the body is.

Each anchor lists the findings it carries. **Drift in a node invalidates exactly those findings**:

```
== pipeline-node anchors (structured drift detector) ==
  28 nodes frozen, kinds ['admission', 'arbitration', 'compatibility', 'filter',
                          'replacement', 'resolver', 'scoring'] -> NO DRIFT
```

and, on a node that moved, the run fails with e.g.
`DRIFTED PN-07 compatible (compatibility) invalidates ['X5', 'X9']`.

**The limit, stated.** This is coverage *of the nodes listed*, not of the program. A load-bearing
node that nobody added to the ledger is not covered, and adding one is a manual step (S6, step 5).
The claim this packet makes is therefore bounded: *every one of the ten ratified findings and all
three dead regions is carried by at least one frozen node anchor* — pinned by
`test_every_ratified_finding_is_covered_by_a_pipeline_anchor` — **not** that every decision node in
the subject is frozen.

### S2.3 Worked example A — the chop bound, and the `.max(1)` error

Site `R:611` and `R:615-623` (audit S16, HARVEST-WOOD).

```rust
let turns=(travel_turns+chop_turns+return_turns+1).max(1);      // R:611
...
let wood=final_size.min(unit.free_capacity());                  // R:615
if wood<=0{ continue; }                                         // R:616
let mut score=1000.0*wood as f64/turns as f64;                  // R:619
if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{
    let opponent_distance=manhattan(plant.cell,view.shacks[1]); // R:621
    score+=900.0/(1+opponent_distance)as f64;                   // R:622
}
```

Step 2 gives leaves `travel_turns`, `chop_turns`, `return_turns`, `wood`, `opponent_distance`.
Step 3:

| leaf | interval | method | citation |
|---|---|---|---|
| `travel_turns` | `[0, inf)` | producer-invariant (`ceil_div` of a BFS distance) | `R:595` |
| `chop_turns` | `[1, 100]` | producer-invariant by loop-bound enumeration | `R:566-570`, single call site `R:607` |
| `return_turns` | `[0, inf)` | producer-invariant | `R:603-606` |
| `wood` | `[1, 3]` | guard (`R:616`) + preset (`max_carry_capacity:3`, `R:327`; `clamp(1,3)`, `R:850`) | `R:615-617` |
| `opponent_distance` | `[0, inf)` | producer-invariant (`manhattan >= 0`) | `R:621` |

The load-bearing row is `chop_turns`. `chop_outcome` returns `Some((turns, size))` **only** at
`R:569`, inside `for turns in 1..=100` (`R:566`); every other path returns `None`, and the caller's
`let Some((chop_turns, final_size)) = … else { continue }` at `R:607` discards it. Hence
`chop_turns >= 1`, hence `turns >= 0+1+0+1 = 2`.

Result (`RM-1`, reproduced by the checker):

```
RM-1:  computed (0, 2400]  claimed (0, 2400]  [NO_REPEATED_VARIABLE_INTERVAL_EVAL]
       assumptions ASSUMPTION_DEPENDENT ['wood']; reachability UNPROVED; endpoint_witnessed NONE
       clamp .max(1) at R:611: operand [2, inf) -> DEAD
RM-1r (opponent_distance >= 1): computed (0, 1950]  [NO_REPEATED_VARIABLE_INTERVAL_EVAL]
       assumptions ASSUMPTION_DEPENDENT ['opponent_distance', 'wood']
```

`2400` is an **upper bound under stated assumptions**, not a proved attainable maximum
(`chatgpt_1` B4): it holds while the shipped preset caps carry capacity at 3 — the ledger's own
`wood` entry says the bound rises to 2000 above that — and it permits `opponent_distance = 0`,
which requires a tree standing on the enemy shack cell and may be unreachable in legal engine
states. Both facts are now in the machine output, not only in this prose.

**Two things a reader must take from this, and the second is the important one.**

First: the corrected bound is `(0, 2400]`, not `3900` — matching the audit and `chatgpt_1`'s A2.

Second, and this is a correction to how the audit told the story: **the `.max(1)` is dead either
way, so clamp-deadness is not what catches the error.** The `+ 1` literal alone already forces the
operand `>= 1`. Re-run the model with `chop_turns` weakened to `[0, 100]` — i.e. the invariant not
propagated — and the tool still says `DEAD`, but the site range becomes `(0, 3900]`, which is
*exactly the original manifest's number*. This is regression-tested at
`test_score_hierarchy_check.py::TestRangeModel::test_dropping_the_producer_invariant_reproduces_the_manifest_error`.

So the discriminating artefact is **the propagated attainable interval of `turns`**, not the
presence or absence of a clamp. An auditor who checks clamps and skips ranges reproduces the error.

### S2.4 Worked example B — the fruit-equipment site, and where interval arithmetic loses

Site `R:479` (audit S15, EQUIP → MOVE toward a fruit tree). This example is chosen because it
demonstrates (a) the precision label doing real work and (b) the procedure independently
reproducing `chatgpt_1`'s correction C3, which a reading of the same lines missed.

```rust
let travel=Self::ceil_div(dist[&plant.cell],unit.stats.movement_speed);   // R:476
let wait=(Self::ticks_until_fruit(view,plant)-travel).max(0);             // R:477
... score:base_score-(travel+wait)as f64 ...                              // R:479
```

Leaves: `base_score`, `travel`, `ticks_until_fruit`.

- `base_score` → `[6000, 6000]`. **Method: call-graph binding** — this is S3's output feeding S2's
  input, and it is why the two procedures are one method and not two.
- `ticks_until_fruit` → `[0, 100]`, producer-invariant by loop-bound enumeration: `return 0` at
  `R:411`, or `return turns` at `R:426` from `for turns in 1..=100` at `R:416`, or the literal
  `100` at `R:430`.
- `travel` → `[0, 83]`, **panel-bounded assumption**: corpus maps are ≤ 14×6
  (`claude_1/banana-restoration-r2/fuzz/failures/m085-s0/candidate-transcript.txt:1-6`), so a BFS
  distance is ≤ 83 cells and `movement_speed >= 1`. Labelled an assumption; void if the panel
  changes.

Naive form — the expression as written:

```
RM-2n: computed [5817, 6000]  [REPEATED_VARIABLE_OVER_APPROX]
       clamp .max(0) at R:477: operand [-83, 100] -> NOT_PROVED_DEAD
```

`REPEATED_VARIABLE_OVER_APPROX` because `travel` occurs twice. `5817` is a **bound**, not an attained value. (Note
the contrast with S2.3: the same syntactic shape `.max(k)`, one dead, one live, distinguished
mechanically by the operand interval.)

Rewrite to single-occurrence form. Algebraically,
`travel + max(ticks - travel, 0) == max(ticks, travel)`:

```
RM-2x: computed [5900, 6000]  [NO_REPEATED_VARIABLE_INTERVAL_EVAL]
       assumptions ASSUMPTION_DEPENDENT ['travel']; endpoint_witnessed NONE
```

Note what the rewrite did and did not buy. It removed the repeated-variable loss. It did **not**
make `[5900, 6000]` an exact attainable range: `travel <= 83` is a panel-bounded assumption, and
no endpoint has a witness.

Compare the iron site `R:501`, `base_score - *d` with `base_score = 6100` (S3) and `d` in raw BFS
cells:

```
RM-3:  computed [6017, 6100]  [NO_REPEATED_VARIABLE_INTERVAL_EVAL]
       assumptions ASSUMPTION_DEPENDENT ['d']
```

**What this establishes, mechanically:** the fruit-equipment site attains values **below 6000**
(down to 5900 under the panel assumption), so the audit's "upper tier `[6_000, 20_000]`" is not a
closed lower boundary and the 100-point iron/fruit separation is not protected by map diameter
alone. That is `chatgpt_1`'s C3, re-derived by procedure rather than by argument, in one command.
The two-tier *observation* survives; the numeric boundary does not. Publish proved site ranges, not
tier endpoints.

### S2.5 Failure modes of this procedure

- **A leaf with no honest bound.** Then write `[-inf, inf)` and let the result be useless. Do not
  invent a bound to make the table tidy.
- **Correlated leaves.** Interval arithmetic assumes independence *between* declared variables.
  `ticks_until_fruit` and `travel` both depend on `plant`; `NO_REPEATED_VARIABLE_INTERVAL_EVAL`
  means "no repeated-variable loss", not "no modelling assumption" and not "exact range". Record
  correlation in the model's `note`.
- **Branch unions.** An `if/else` scoring site is two models, not one (see `RM-A1a`/`RM-A1b`). Do
  not model a branch condition as an interval.
- **Integers.** The real relaxation is a superset. Fine for upper bounds; never claim an endpoint
  is attained from it.

### S2.6 What is manual here

Steps 1–3 and 5. The tool cannot read `R:566-570` and conclude `chop_turns >= 1`; a human must, and
must write the citation and the method name. The ledger is the audit trail: a wrong bound is
visible as a wrong `assumption` string next to a line number, which is reviewable. That is the
whole design.

---

## S3. The call-graph binding procedure

The question: *is this scoring parameter genuinely variable, or bound to a single literal?* This is
the procedure that would have caught the band error.

### S3.1 Steps

1. Blank comments and string/char literals (the tool does this; by hand, be careful of `//` inside
   `format!` strings — the subject is minified and dense).
2. Enumerate **every** occurrence of the identifier with word boundaries.
3. Classify each occurrence: **definition** (preceded by `fn`), **call** (immediately followed by
   `(`), or **bare use** (anything else).
4. **If there is any bare use, stop: the result is `INCONCLUSIVE`.** A bare use means the function
   may be taken as a value (function pointer, closure capture, method reference) and textual call
   sites no longer bound the real call set. This side-condition is checked mechanically and is what
   makes the enumeration sound rather than merely suggestive.
5. For each call, split the argument list by balanced-paren scanning (not by comma-splitting) and
   classify the argument at the parameter's index as a numeric literal or not.
6. Report the verdict:
   - `ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING` — one *textual* call, the parameter is a literal at
     that occurrence. **The parameter is not variable.** Its interval is a point, usable as a leaf
     bound in S2.
   - `ONE_TEXTUAL_CALL_SITE` — one textual call, argument non-literal. Recurse into the argument.
   - `MULTIPLE_TEXTUAL_CALL_SITES` — genuinely parameterised; the parameter's interval is the union
     of the bindings and the site must be modelled once per binding.
   - `INCONCLUSIVE` — see step 4.

   Every verdict name says **textual** on purpose (`chatgpt_1` B6). None of them asserts that the
   occurrence executes. Each binding additionally carries `reachability_status`, which this tool
   only ever emits as `UNPROVED`; the checker *rejects a ledger* whose binding `claim` or `note`
   uses the word "reachable" at all, so the mislabelling cannot recur silently.

**Stated side conditions, not proved by the tool** (re-confirm by hand when the code moves): no
macro-generated calls; no trait-object dispatch to the name; no `use … as` renaming. The subject is
a single file of inherent `impl`s, which is why these hold today.

### S3.2 Worked example — `fruit_candidates` / `iron_candidates`

The manifest's property (b) claimed these "take the band as a **parameter** … the same function
therefore emits scores into different bands depending on who called it." The procedure:

```
$ python3 claude_1/banana-restoration-r2/score_hierarchy_check.py \
      --ledger claude_1/banana-restoration-r2/score-hierarchy-ledger.json --repo .
== call-site bindings ==
  fruit_candidates: def@[463] calls@[455] bare@[] -> ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING (ok)
      reachability_status: UNPROVED
      line 455 literals {3: '6_000.0'}
  iron_candidates:  def@[485] calls@[448] bare@[] -> ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING (ok)
      reachability_status: UNPROVED
      line 448 literals {2: '6_100.0'}
```

Reading it: each identifier occurs exactly twice in the whole file — once as a definition, once as
a call — and `bare@[]` is empty, so step 4's side-condition holds and the enumeration is sound. The
parameter is bound to a literal at the single call site. **The band is not variable; it is a
constant four lines from its use.** The opacity is latent, not actual. This is `chatgpt_1`'s A3 and
the coordinator's error (2), reproduced by command.

Contrast, from the same run:
`ticks_until_fruit: def@[409] calls@[477, 821] -> MULTIPLE_TEXTUAL_CALL_SITES`.
Two call sites; only `R:477` feeds a scoring expression, and *that* narrowing is a manual reading
step the tool does not perform. It reports the call set; you decide which calls matter.

### S3.3 What this procedure cannot tell you

That a call site is **reachable**. `ONE_TEXTUAL_CALL_SITE` means one *textual* occurrence of the
identifier immediately before `(`; whether the guard above it can hold is a control-flow question
(S7.1). The procedure bounds variability from above, which is all the band question needed.

This is not a pedantic distinction. The first draft of the ledger recorded "one **reachable** call
site" for `fruit_candidates` and `iron_candidates` — a claim the checker cannot make and does not
make (`chatgpt_1` B6). It now reads "one TEXTUAL call site under the bare-use side condition", and
`validate_ledger` fails the whole run if any binding claim reintroduces the word.

---

## S4. Intention and boundary-crossing — definitions and classification

This section exists so that two auditors independently produce the same count. It replaces the
audit's single undifferentiated "10 crossings" with a decision procedure.

### S4.1 Definitions

- **Scoring site.** A program point that assigns a value to a `Candidate`'s `score` field.
  Enumerated manually; drift-detected by S2.2.
- **Intention.** A label attached to a scoring site by a human and **frozen in the ledger** —
  literally, in `ledger.intentions`, one record per label with its `R:` sites and a gloss. Two
  auditors agree because they read the same ledger, not because they judge alike. Disagreement
  about a label is resolved by amending the ledger (and re-running), never by re-arguing in prose.
  The subject's labels are the audit's §3.1 table: `UNBLOCK`, `COMMIT-CHOP`, `REGENERATE`, `BANK`,
  `SEED`, `CONVERT`, `EQUIP` (sub-goals `EQUIP-IRON` / `EQUIP-FRUIT`), `CLEAR-FOR-TRAIN`,
  `HARVEST-WOOD`, `IDLE-HARVEST`, `NOTHING` — **eleven**, which is the count the audit's prose
  should have carried (`chatgpt_1` C5; the audit wrote "nine" and then listed eleven).

  *The first draft of this packet said these were frozen in the ledger when they were not*
  (`chatgpt_1` B1). They are now. `test_it_freezes_eleven_intentions` fails if that stops being
  true.
- **Declared priority.** A partial order over intentions, declared in `ledger.priority`. Absent a
  declaration, two intentions are *incomparable* and no crossing between them can be claimed.

  **For this subject the relation is `declared: false`, and that is load-bearing.** No priority
  order over the eleven intentions is declared by the subject, by the audit, or by the owner.
  Every finding below is therefore a statement about *mechanism and range*, never about a violated
  ordering — and no sentence anywhere may say "J outranks I" on this ledger's authority. Declaring
  a relation is an owner action. The checker rejects a ledger that sets `declared: true` with an
  empty relation.
- **Boundary crossing (generic).** A state, or a pair of states, in which the pipeline's realised
  preference contradicts the declared priority — whether the contradiction is expressed by scores,
  by admission, by arbitration, or by time.

The last definition is deliberately broad, because the audit's central result is that most of the
subject's boundary problems are *not* score comparisons. The classes below make the breadth
tractable.

### S4.2 The classes

| code | class | defining test |
|---|---|---|
| `AX` | **arithmetic crossing** | two co-emitted candidates of intentions `I > J`, and accumulation of terms *within one expression* lets `J`'s attainable range reach or exceed `I`'s |
| `TX` | **temporal crossing** | one site's price changes discontinuously as a function of a clock input, all else held fixed; the branches' ranges lie in different declared bands |
| `SX` | **state/position discontinuity** | one site's price or target set changes discontinuously as a function of the agent's own position or a null-progress transition |
| `UX` | **unit/scale incommensurability** | two sites of different intentions produce overlapping numeric ranges from different physical units, with no declared separator |
| `MX` | **admission suppression** | an intention label is absent from the candidate set by control flow, so it cannot lose a comparison |
| `BX` | **arbitration crossing** | the post-scoring stage (pair-sum, compatibility, move rewrite) can realise a lower-priority outcome without any score expressing it |
| `DX` | **duplicate-mechanism inversion** | one intention with one goal implemented at two distinct sites with different magnitudes or admission mechanisms |
| `ZX` | **dead scoring code** | a scoring sub-expression or branch that cannot execute, or cannot change the value. **Counted separately from crossings.** |

### S4.3 The decision procedure (apply in order; first match wins)

Applying the tests in a fixed order is what makes the classification reproducible; without an
order, `X8` is arguable as either `MX` or `DX` and two auditors diverge.

The order is **mechanised**, and this is the part of S4 the tool actually enforces. Each finding
record in the ledger carries `rule_answers`: the human's answer to each of the eight predicates,
with citations. The checker applies the fixed first-match order to those answers and **rejects the
ledger** if the declared `class`/`rule` is not what the order produces. So the *order* is machine-
checked and auditable — which is what made `X8` arguable as either `MX` or `DX` — while the
*predicates* remain human judgements, and nothing here pretends otherwise. A finding with a missing
predicate answer is an error, not a silent "no".

1. Can the code not execute, or not change the value? → **`ZX`**. Stop. (Not a crossing; counted
   separately.)
2. Is the *intention label itself* absent from the candidate set by control flow? → **`MX`**.
   (Restricting a target set while keeping the label present is **not** `MX`; that is rule 6.)
3. Does the discontinuity live in the post-scoring stage rather than at a scoring site? → **`BX`**.
4. Is one intention-and-goal priced at two distinct sites with different magnitudes or mechanisms?
   → **`DX`**.
5. Does one site's price branch on a clock input into different bands? → **`TX`**.
6. Does one site's price or target set branch on the agent's own position / a null-progress
   transition? → **`SX`**.
7. Do two intentions' ranges overlap because of accumulation within one expression? → **`AX`**.
8. Do they overlap because of incommensurable units or scale factors? → **`UX`**.
9. Otherwise: not a crossing. Record as an observation.

### S4.4 The ten, classified

| id | class | one-line reason | evidence state (S5) |
|---|---|---|---|
| X1 | **`TX`** | rule 5 — `R:1291-1295` / `R:1323-1327` branch on `view.turn > 250`; `(0, 187.5]` vs `7_000 − priority` | `SOURCE_PROVED` |
| X2 | **`SX`** | rule 6 — `R:1290` on-door branch prices only `unit.cell`; `R:1303` off-door branch prices every door. Label `CONVERT` present in both, so not rule 2 | `SOURCE_PROVED` (**demoted** from `STATE_WITNESSED`) |
| X3 | **`SX`** | rule 6 — one site `R:1261-1265` branching on `at_target`: `9_000` in place vs `8_000 − dist` | `SOURCE_PROVED` |
| X4 | **`UX`** | rules 4 and 7 fail (different goals `EQUIP-IRON` / `EQUIP-FRUIT`; no accumulation); rule 8 — raw cells `R:501` vs turns `R:479` | `SOURCE_PROVED` |
| X5 | **`BX`** | rule 3 — `R:683` maximises `a.score + b.score` over compatible pairs | `REACHABILITY_HYPOTHESIS` |
| X6 | **`MX`** | rule 2 — `YamoBot::bank_candidates` (`R:947-955`) can empty a guaranteed-non-empty set; `BANK` absent | `REACHABILITY_HYPOTHESIS` |
| X7 | **`DX`** | rule 4 — `CLEAR-FOR-TRAIN` as a soft `6_500` candidate (`R:1422`) and as a forced `20_000` list replacement (`R:962`/`R:987`) | `SOURCE_PROVED` (the six-outranker claim is separately `REACHABILITY_HYPOTHESIS`) |
| X8 | **`MX`** | rule 2 — `R:1282-1286` overwrites to `10_000` and `return`s, so every other label is absent | `SOURCE_PROVED` + `OWNER_POLICY_QUESTION` |
| X9 | **`BX`** | rule 3 — `compatible` (`R:643-646`) returns `true` on `Target::None`, so the only cross-unit constraint vanishes | `SOURCE_PROVED` (**demoted** from `STATE_WITNESSED`) |
| X10 | **`MX`** | rule 2 — `R:1413` admits idle harvest only when every candidate is `Target::None` | `SOURCE_PROVED` |

**Counts under this scheme.** They are **generated**, not typed. The block below is rendered by
`score_hierarchy_check.py` from `score-hierarchy-ledger.json` and embedded here verbatim;
`TestReportAgreesWithTheLedger.test_the_reports_generated_block_is_exactly_what_the_ledger_generates`
compares the two byte for byte. **Editing this table by hand fails the suite. Editing the ledger
without re-rendering this table fails the suite.** That is the whole point of `chatgpt_1` B1: in the
first draft these counts were prose maintained beside a tool that could not see them — the same
drift mode M2 exists to remove.

<!-- BEGIN GENERATED: score-hierarchy-ledger.json -->
```
GENERATED FROM score-hierarchy-ledger.json BY score_hierarchy_check.py
  ledger_version        2.0.0
  subject_sha256        98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29

  intentions frozen     11
  priority declared     NO  (no crossing may be claimed between incomparable intentions)
  score census sites    22
  pipeline node anchors 28
  committed witnesses   0

  pipeline findings     10
    ZX          0   --
    MX          3   X6, X8, X10
    BX          2   X5, X9
    DX          1   X7
    TX          1   X1
    SX          2   X2, X3
    AX          0   --
    UX          1   X4
    OBSERVATION 0   --

  dead scoring regions  3   ZX-1, ZX-2, ZX-3

  evidence states
    REACHABILITY_HYPOTHESIS  2
    SOURCE_PROVED            8
    +OWNER_POLICY_QUESTION   X8

  KNOWN_AX_FINDINGS = 0
  GLOBAL_AX_STATUS = UNRESOLVED
    because site discovery is an under-approximating token census plus a hand-maintained node list; only a subset of scoring expressions has a range model; co-reachability is unproved
```
<!-- END GENERATED -->

Regenerate with:

```
python3 claude_1/banana-restoration-r2/score_hierarchy_check.py \
    --ledger claude_1/banana-restoration-r2/score-hierarchy-ledger.json --repo . --emit-generated
```

### The headline — and what it does *not* say

> **`KNOWN_AX_FINDINGS = 0; GLOBAL_AX_STATUS = UNRESOLVED`.**
>
> Of the ten already-known pipeline findings on `98628e98`, **zero classify as arithmetic
> crossings**: one temporal, two state/position, one unit-scale, three admission suppressions, two
> arbitration, one duplicate mechanism; plus three dead scoring regions counted separately. Eight
> are `SOURCE_PROVED`, two are `REACHABILITY_HYPOTHESIS`, and **none is `STATE_WITNESSED`** —
> no witness packet pinned to this subject exists.
>
> **Whether the program contains an arithmetic crossing at all remains `UNRESOLVED`.**

The second sentence of that headline is the correction. The first draft wrote "`AX = 0` is not a
null result — it is the answer to the owner's point 6", and that does not follow (`chatgpt_1` B2).
The owner's worry was "enough small increments outvote a higher-tier intention". What has been
established is that *none of a preselected ten* instantiates it inside a scoring expression. That
is not the same as *no arithmetic crossing exists*, and this method cannot close the gap, because
by its own admission:

- the score census is an **under-approximating token scan**, not a complete scoring-site discovery
  (S2.2, S7.4);
- the pipeline-node anchors cover a **hand-maintained list of 28 nodes**, not the program (S2.2b);
- only **seven scoring expressions** have a range model at all;
- **co-reachability is unproved** (S7.2) — and an `AX` claim is by definition a claim about two
  candidates in *one* candidate set;
- the method **cannot discover** temporal, positional or admission discontinuities in the first
  place (S7.3), so "we did not find one" carries little weight about what is there.

Settling the global question needs an exhaustive scoring-site registry plus co-reachable candidate
packets — item B / M1's Decision Packet. `GLOBAL_AX_STATUS` is emitted by the checker as a
**constant**, deliberately: no future ledger edit can promote it by relabelling findings, because
counting labels on a preselected set is not how that question is answered.

What *does* survive, and is worth stating positively: the subject's known boundary problems are
**structural, not arithmetic**. What gets admitted, what gets re-priced by the clock or by where the
unit is standing, and what the arbitrator does afterwards. That is the same conclusion `chatgpt_1`
reached ("ten pipeline findings, not ten measured score-boundary crossings"), reached here by a
procedure a second auditor can re-run.

Two ratified statements that are **not** crossings under this scheme and should stop being counted
as if they were:

- **The lower tier.** "Three intentions in one continuous interval `(0, 2400]`" is a `UX`-shaped
  *observation about the tier*, not a crossing: a crossing needs a co-reachable candidate packet
  (`chatgpt_1` C4). The ratified form is: *lower-tier intentions use different units and scale
  factors (1000 / 750 / 1) without a typed priority boundary.*
- **The upper tier's floor.** `[6_000, 20_000]` is refuted as a closed boundary by S2.4. The
  ratified form is: *publish per-site proved ranges; do not name 6_000 as a tier endpoint.*

### S4.5 Reproducibility of the scheme — honest limits

The scheme makes *classification* reproducible, not *discovery*. Two auditors handed the same ten
findings and the same ledger will produce the same table. Two auditors handed the source will not
necessarily find the same ten — that depends on the inventory (S2.2), which is manual. And a novel
finding still needs a human to name its intention labels and its discriminating input before rule 1
can be applied.

---

## S5. Evidence standard

Adopted from `chatgpt_1` C1, with promotion rules added. The audit's "MEASURED end-to-end" label is
retired: it conflated source deduction with observation.

| state | means | admissible for |
|---|---|---|
| `SOURCE_PROVED` | derived from the pinned subject by S2/S3, every leaf bound cited with a method | the mechanism exists; the range is bounded |
| `STATE_WITNESSED` | a committed literal input state, the complete candidate surface, the selected result, and the identity (SHA) of the tool that produced them | the mechanism fires in a specific state |
| `CORPUS_MEASURED` | `STATE_WITNESSED` plus a count over a regenerated corpus, with the regeneration command | frequency claims |
| `REACHABILITY_HYPOTHESIS` | the mechanism is `SOURCE_PROVED` but no state is known in which it fires | must be labelled in every sentence; **never counted as observed** |
| `OWNER_POLICY_QUESTION` | the mechanism is proved and its desirability is not an agent's call | terminal until the owner rules |

**Promotion rules** (what it takes to move a finding up):

- `REACHABILITY_HYPOTHESIS → SOURCE_PROVED`: exhibit the guard chain admitting the construct, with
  citations. For a *co-reachability* claim (two candidates in one set) this requires the candidate
  surface, i.e. tooling item B / M1 — it cannot be done by reading.
- `SOURCE_PROVED → STATE_WITNESSED`: commit an input state file, the full candidate dump at that
  state, the selection result, and the tool SHA. Nothing less. A transcript excerpt without the
  candidate surface is not a witness for a *scoring* claim, because it shows what was chosen and
  not what was compared.
- `STATE_WITNESSED → CORPUS_MEASURED`: the regeneration command plus the count. Note the corpus
  caveat: the committed 34-episode corpus was produced by the pre-repair referee (audit §4.2a);
  re-run first or the count freezes a referee bug.
- Anything `→ REACHABILITY_HYPOTHESIS`: a demotion, and it should be routine. It is the honest
  landing place for most mechanism findings.

**Re-labelling of the audit's claims:** its "8 MEASURED end-to-end" becomes **8 `SOURCE_PROVED`
(X1, X2, X3, X4, X7, X8, X9, X10)**; its "2 MEASURED-mechanism / SUSPECTED-reachability" becomes
**2 `REACHABILITY_HYPOTHESIS` (X5, X6)**. X8 additionally carries `OWNER_POLICY_QUESTION`. Nothing
in the audit reaches `STATE_WITNESSED` or `CORPUS_MEASURED`.

**X2 and X9 are demoted, and this is a correction to the first draft** (`chatgpt_1` B3). That draft
labelled them `STATE_WITNESSED` on the strength of the episode names `m085-s0` and `m014-s1`. A
report citation to an episode name is not a witness packet, and this project's saved transcripts
elsewhere carry *different candidate identities* — so those episodes are not admissible evidence
about `98628e98` at all. `ledger.witnesses` is **empty**, and the checker fails the run if any
finding claims `STATE_WITNESSED` without a witness record whose `subject_sha256` is the pinned
subject. Each of X2 and X9 carries `demoted_from` and `promotion_requires` fields naming exactly
what would restore the label: a committed literal input state, the full candidate surface at that
state, the selection result, the candidate identity, the extraction method, and a content hash —
all pinned to `98628e98`. That is item B / M1 output, and it does not exist yet.

Every claim in *this* packet carries `MEASURED` (executed here), `INFERRED` (derived from cited
source), or `UNRESOLVED`, per the task rules; the five-state ladder above governs claims about the
*subject* specifically.

---

## S6. Re-run checklist

Run in order. Each step's output is an input to the next. All read-only.

**0. Pin the workspace.** MEASURED command:

```
cd /home/tarstars/prj/troll_farm-claude_1
git pull -q && git rev-parse HEAD origin/main
```

**1. Re-pin the artefacts.** Recompute and compare all three SHAs of S1.1:

```
git show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs | sha256sum
sha256sum rust/src/bin/yamo_orchard_live.rs rust/src/game/engine.rs
```

If the subject's SHA changed, **the audit is stale** — continue. If only the companion changed, the
subject findings stand and any companion-anchored instrument (N4) must be re-anchored.

**2. Run the mechanical checker.**

```
python3 claude_1/banana-restoration-r2/score_hierarchy_check.py \
    --ledger claude_1/banana-restoration-r2/score-hierarchy-ledger.json --repo .
echo $?     # 0 = no drift
```

Its sections are ledger validation, S1 (identity), S2.2 (census drift), S2.2b (pipeline-node
anchors), S3 (bindings), S2 (ranges). Read the census diff first: `added`/`removed` name the lines
whose manual inventory must be redone; `moved` means the same expression changed line number and
only citations need updating. Then read `INVALIDATED FINDINGS` from the anchor section: those
records may not be restated until they are re-derived.

**3. Run the checker's own tests.**

```
cd claude_1/banana-restoration-r2 && python3 -m unittest test_score_hierarchy_check -v
```

127 tests, of which 17 run against the real subject blob and skip cleanly if it is unreachable.
Do this **before** trusting step 2 on a moved file.

**4. Redo the manual inventory for every drifted line** (S2.2). For each: `R:` citation,
normalised text, intention label. Update `census` and the labels in the ledger.

**5. Redo S3 for every parameterised scoring generator, and re-anchor every pipeline node.** Add a
`bindings` entry per generator; a generator that has gained a second call site changes from
`ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING` to `MULTIPLE_TEXTUAL_CALL_SITES` and its dependent range
models must be split, one per binding. For `pipeline_anchors`: re-derive every finding the drifted
nodes carried, and **add an anchor for any decision node a new or amended finding cites** — anchor
coverage is a manual list (S2.2b) and this is the step that maintains it.

**6. Redo S2 for every drifted site.** Re-establish each leaf bound with citation and method. Do
not carry a bound forward across a code move without re-reading its producer — the producer is
where the invariant lives.

**7. Re-classify with S4.3.** Apply the decision procedure to each finding in order. Produce the
S4.4 table and the count table. If a count changed, say which rule fired differently and why.

**8. Re-state evidence per S5.** `ledger.witnesses` is currently empty and no finding is
`STATE_WITNESSED`; if M1/M3a later commits a witness packet pinned to the subject SHA, add it there
and promote the finding by setting `witness_id` — the checker verifies the subject identity and
refuses the promotion otherwise. A finding whose guard chain disappeared is closed.

**9. Regenerate the ledger's `attainable` fields from the tool, not by hand.** The ledger's claimed
intervals were produced by `range_model_report` and re-checked by the same code; hand-editing them
reintroduces exactly the transcription risk this packet is about.

**10. Record what you could not settle** as `REACHABILITY_HYPOTHESIS` or `UNRESOLVED`, with the
settling evidence named. Do not let an unsettled item quietly acquire a stronger label by being
restated.

---

## S7. Known limits — what this method cannot catch

Stated plainly, because a method presented as complete is the failure mode this programme keeps
hitting.

### S7.1 It cannot prove reachability

Every range model presupposes that the site executes. Nothing here decides whether the guard chain
above a site can hold. `X5` and `X6` are `REACHABILITY_HYPOTHESIS` for precisely this reason and
this method cannot promote them. What it would take: an executable candidate dump at a chosen state
(item B / M1's Decision Packet).

### S7.2 It cannot prove co-reachability

"Intention `J` outranks intention `I`" needs both candidates in **one** candidate set. Range
overlap does not establish that — it is necessary, not sufficient. This is why `AX = 0` in S4.4:
not one of the ten was shown to be a *comparison* between co-emitted candidates. It is also why
`X7`'s six-outranker claim is demoted (`chatgpt_1` C7). Settling requires the candidate surface.

### S7.3 It cannot find a temporal discontinuity — X1 is the worked case

This is the important one.

`X1` is the largest finding in the audit and **no part of this method would discover it**. Walk it
through: the range procedure (S2) computes `(0, 187.5]` for `R:1295` and `7_000 − priority` for
`R:1292`. Both are correct. Both are *within* their own site's bounds. There is no clamp to prove
dead, no accumulation to overflow a band, no repeated variable, no bound to tighten. Every check in
S2 passes on both branches, and the finding — that these are the **same intention on consecutive
turns** — is invisible to all of them.

What actually found it was a human noticing that `view.turn > 250` selects between two expressions
labelled with the same intention. S4.3 rule 5 *classifies* that as `TX` once you have it; it does
not *find* it. The nearest mechanisable form would be: "flag every scoring site whose expression
branches on a clock-derived input, and compare the branches' ranges" — implementable, and
deliberately not implemented here, because enumerating "clock-derived inputs" is a dataflow
question and a token scan for `view.turn` would be a regex pretending to be static analysis. It is
recorded as the highest-value extension in S7.7.

Generalise the limit: **arithmetic bounds checking is blind to any discontinuity whose
discriminating input is not an argument of the arithmetic.** Time (`X1`), own position (`X2`,
`X3`), and candidate-set membership (`X6`, `X8`, `X10`) are all such inputs. That is six of the ten.

### S7.4 The census can miss a scoring site, and the anchors can miss a node

The census is a token scan (S2.2). A score written through a helper, a builder, or a macro would
not appear. Its guarantee is one-directional: no drift means nothing *it can see* moved.

The pipeline anchors (S2.2b) close the specific gap `chatgpt_1` B7 named — filter, compatibility,
replacement and resolver nodes — but they have the same shape of limit one level up: they cover
**28 named nodes**, chosen by hand because a finding cites them. A new decision node, or an
existing one nobody listed, is invisible to them. Anchor coverage is a claim about a list, and the
list is manual. What the anchors do guarantee is that none of X1–X10 or the three dead regions can
change silently, because each is tied to at least one frozen body.

### S7.5 The bindings check has unproved side conditions

Macro-generated calls, trait dispatch, and `use … as` renaming would each defeat it. They do not
occur in the subject today; the tool cannot tell you when that stops being true. The one condition
it *does* check — no bare uses of the identifier — is checked, and it refuses to conclude when it
fails.

### S7.6 Panel-bounded assumptions expire

`travel ∈ [0, 83]` is a fact about the current corpus maps, not about the program. Every model that
uses it is void if the panel changes, and `X4`'s "inert at map scale" verdict goes with it. The
ledger labels these `panel-bounded assumption` so they can be grepped and re-examined in one pass.

### S7.7 What would extend the method, in value order

1. **Clock-branch detection** (S7.3) — needs dataflow over `view.turn`, not a token scan.
2. **A candidate-surface dump at a literal state** — promotes `SOURCE_PROVED` to `STATE_WITNESSED`
   and is the only route to `AX` claims at all. This is item B; note `chatgpt_1` C10, that the
   existing N4 machinery is anchored to `fff6669b` and must be retargeted before it can serve.
3. **A null-progress successor check** — `V(s) >= V(s')` for a null-progress step would catch the
   `SX` class automatically. Needs the candidate surface, nothing more.
4. **A guard-chain extractor** — would let `REACHABILITY_HYPOTHESIS` be discharged statically for
   simple cases. Needs a Rust parser; out of reach in stdlib Python.

---

## Appendix A — the shipped checker

| file | purpose | sha256 |
|---|---|---|
| `claude_1/banana-restoration-r2/score_hierarchy_check.py` | the mechanical checks and the ledger generator | `2c016e3722e0d24919a7aee92491a709394d2d2f18dca2c0a5b394924015daee` |
| `claude_1/banana-restoration-r2/score-hierarchy-ledger.json` | v2.0.0: frozen census, 28 pipeline-node anchors, bindings, cited range models, 11 intentions, priority, X1–X10, dead regions, witnesses | `d240f661b9196368933f36f030189fd98a93f95a05478012e64120eb8339bfca` |
| `claude_1/banana-restoration-r2/test_score_hierarchy_check.py` | 127 tests, stdlib `unittest` | `f09a3b7979e7469aececfea42922b97f4775f618a1575b6a5c3f07926537582c` |

The two code SHAs above are recomputed at commit time; they pin *this* revision, not the draft
`chatgpt_1` reviewed at `129974c3`. Recompute with `sha256sum` on the three paths.

MEASURED. Expected output on the pinned subject, in full:

```
== ledger validation ==
  no schema/vocabulary problems
== identity ==
  subject cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs
    expected 98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29
    actual   98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29   MATCH
  companion rust/src/bin/yamo_orchard_live.rs: MATCH
== census (drift detector) ==
  22 sites now, 22 frozen -> NO DRIFT
== pipeline-node anchors (structured drift detector) ==
  28 nodes frozen, kinds ['admission', 'arbitration', 'compatibility', 'filter',
                          'replacement', 'resolver', 'scoring'] -> NO DRIFT
== call-site bindings ==
  fruit_candidates: def@[463] calls@[455] bare@[] -> ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING (ok)
      reachability_status: UNPROVED
      line 455 literals {3: '6_000.0'}
  iron_candidates: def@[485] calls@[448] bare@[] -> ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING (ok)
      reachability_status: UNPROVED
      line 448 literals {2: '6_100.0'}
  chop_outcome: def@[556] calls@[607] bare@[] -> ONE_TEXTUAL_CALL_SITE (ok)
      reachability_status: UNPROVED
  ticks_until_fruit: def@[409] calls@[477, 821] bare@[] -> MULTIPLE_TEXTUAL_CALL_SITES (ok)
      reachability_status: UNPROVED
== computed range bounds ==
  RM-1   (S16 chop):             computed (0, 2400]     [NO_REPEATED_VARIABLE_INTERVAL_EVAL]
      assumptions ASSUMPTION_DEPENDENT ['wood']; reachability UNPROVED; endpoint_witnessed NONE
      clamp .max(1) at R:611: operand [2, inf) -> DEAD
  RM-1r  (S16, oppdist >= 1):    computed (0, 1950]     [NO_REPEATED_VARIABLE_INTERVAL_EVAL]
  RM-2n  (S15 fruit, naive):     computed [5817, 6000]  [REPEATED_VARIABLE_OVER_APPROX]
      clamp .max(0) at R:477: operand [-83, 100] -> NOT_PROVED_DEAD
  RM-2x  (S15 fruit, rewritten): computed [5900, 6000] [NO_REPEATED_VARIABLE_INTERVAL_EVAL]
  RM-3   (S13 iron):             computed [6017, 6100] [NO_REPEATED_VARIABLE_INTERVAL_EVAL]
  RM-A1a (S17 convert, loop):    computed [7.25155339806, 187.5]
  RM-A1b (S17 convert, sentinel):computed [0.044977506748, 0.074977506748]
== generated classification summary ==
  (the block reproduced verbatim in S4.4)
== verdicts: subject PASS | companion-anchored instruments PASS ==
== overall: PASS ==
```

Every model additionally reports `bound_scope UPPER_BOUND_SOUND__LOWER_NOT_PROVED_ATTAINABLE`.
Subject validity and companion-instrument validity are reported as **separate verdicts**
(`chatgpt_1`, non-blocking note 2): a diverged companion invalidates any instrument anchored to it
(N4), never a finding about the subject. The run still exits non-zero on either, fail-closed.

Tests: `Ran 127 tests … OK` (MEASURED, `python3 -m unittest test_score_hierarchy_check`). The suite
includes negative tests — SHA divergence, an added score site, a second call site appearing, a
mismatched range claim, a drifted pipeline node, an untyped ledger, a ledger asserting reachability,
a finding whose declared class contradicts the rule order, a `STATE_WITNESSED` claim with no witness
packet, and a report whose generated block has been hand-edited — because a checker that only ever
passes is not evidence.

**Coverage of `chatgpt_1`'s ten method-packet requirements:** 1 → S1; 2 → S2.2 (with its stated
limit); 3 → S3; 4 → S2; 5 → S4; 6 → S5 (the standard; the witness packets themselves are
item B and do not exist yet, so `ledger.witnesses` is empty and X2/X9 are demoted accordingly —
stated, not claimed); 7 → S4.4 + S5, with the counts **generated** from the typed
`intentions` / `priority` / `findings` / `dead_regions` / `witnesses` sections rather than written
by hand; 8 → S2.2 census drift **plus S2.2b
pipeline-node anchors**: 28 frozen function bodies across `filter`, `compatibility`,
`replacement`, `resolver`, `admission`, `arbitration` and `scoring` kinds, with drift invalidating
the findings each node carries. This was `partial` in the first draft and is the substance of
`chatgpt_1` B7; it is now closed **for the listed nodes**, which is a bounded claim (S7.4);
9 → S6 step 2; 10 → the checker's default text report.

---

## Appendix B — one observation noticed while building the range models

**Separated deliberately. It is not a new finding, it changes no count in S4.4, and it is not
ratified.**

`conversion_chop_turns` (`R:1207`) returns the **sentinel `10_000`** on two paths: `R:1209` when
`chop <= 0`, and `R:1231` when the tree survives 100 chop turns. The audit's range for the
pre-turn-250 conversion site (`R:1295`) is `(0, 187.5]` with a stated floor of `7.28` at
`conversion_turns = 100`. Under the sentinel the same expression attains
`750/10003 ≈ 0.0750` (models `RM-A1a` / `RM-A1b` in the ledger; `[7.2516, 187.5]` and
`[0.0450, 0.0750]` respectively, both `EXACT`).

Status: `SOURCE_PROVED` for the arithmetic; **`REACHABILITY_HYPOTHESIS`** for whether the sentinel
branch can reach this scoring site — a unit with `chop_power <= 0` reaching `endgame_candidates` is
exactly the sort of guard-chain question S7.1 says this method cannot settle. If it is reachable it
tightens nothing and widens the `X1` ratio discussion (`chatgpt_1` C2) in the direction C2 already
warns about, which is a further reason to leave the ratio unstated until there is a paired boundary
witness.

Recorded here so that it is not lost, and kept out of §S4.4 so that it cannot silently become an
eleventh finding.

---

## Provenance of this packet

- Repository `/home/tarstars/prj/troll_farm-claude_1`, branch `agent/claude_1-banana-restoration-r2`.
- Subject read as `git show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`,
  sha256 `98628e98…` verified at time of writing (MEASURED).
- Every `R:n` citation in this document was read from that blob.
- Every numeric interval in S2 was produced by `score_hierarchy_check.py`, not by hand.
- UNRESOLVED, repeated here so the method is not mistaken for a closure:
  **whether the subject contains any arithmetic crossing at all (`GLOBAL_AX_STATUS`)**; whether
  X1–X10 survive into the live lineage `e7a-r36-simplified`; whether X5 and X6 fire in play;
  whether the turn-250 constant is deliberate; whether D161's resident-anchoring requirement is
  waived for item C; whether the `select` `>=3` branch (`ZX-2`) is genuinely dead, which depends on
  a roster size this packet does not establish.
- Not disputed, and recorded as such: every one of `chatgpt_1`'s seven blocking corrections is
  accepted. Nothing the review demoted has been re-asserted here in weaker words — in particular
  `AX = 0` is nowhere restated as an answer to the owner's point 6, and neither X2 nor X9 is
  described as witnessed. `chatgpt_1`'s eighth item, independent second-checkout execution, is
  `local_claude_1`'s and is not claimed by this packet.
