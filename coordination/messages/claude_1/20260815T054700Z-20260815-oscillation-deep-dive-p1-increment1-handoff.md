---
schema_version: 2
type: handoff
task_id: 20260815-oscillation-deep-dive
from: claude_1
to: ["local_claude_1"]
cc: ["user", "codex_1"]
message_id: coordination/messages/claude_1/20260815T054700Z-20260815-oscillation-deep-dive-p1-increment1-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: ef76ab5440da91b1d0a6aa8d99d561a82f12f819
artifact_paths: ["claude_1/decision_packet/registry.py", "claude_1/decision_packet/source-registry-frozen.json", "claude_1/decision_packet/source-registry.md"]
created_utc: 2026-08-15T05:47:00Z
---

- To: local_claude_1
- CC: user, codex_1
- Task: 20260815-oscillation-deep-dive
- Requires acknowledgement: yes

# handoff: P-1 increment 1 delivered — identity frozen and the drift guard armed. No packet exists yet.

## For the owner, in plain terms

The Decision Packet is the tool that will explain, for one single turn of our bot, *why* it chose
what it chose — which options it saw, which it threw away and on what grounds. It does not exist
yet. What I built today is the **foundation stone**: a machine-checked record of exactly which
version of the bot we are studying and exactly where in its source each decision step lives.

Why that first, rather than something you could look at? Because the failure this project keeps
hitting is analysing one thing and reporting it as another. If the source file shifts by three
lines and nothing notices, every later explanation quietly describes the wrong code. This
increment makes that impossible to do silently: it pins 22 places in the source and refuses to
proceed if any of them moves.

**It also refuses to overstate what it knows.** The generated document opens with a "known gaps"
section that says, in numbers, what is *not* covered yet. I would rather hand you an honest
incomplete thing than a complete-looking one.

## What was delivered

Artifact commit `ef76ab5440da91b1d0a6aa8d99d561a82f12f819` on `agent/claude_1`, pushed and
verified on the remote before this message was written.

This is **rollout step 1** of the frozen contract `chatgpt_1/decision-packet-spec-2026-08-10.md`
— *"freeze schema, source registry and exact candidate SHA"* — which is also acceptance item 1,
*"exact subject SHA and registry drift guard"*. Nothing beyond step 1 is claimed.

- **§4 identity and trust envelope, as code.** `ENVELOPE_CONTRACT` + `check_envelope()`. The
  exact-SHA rule is enforced *by shape* — a 12-character abbreviation is refused as
  `SUBJECT_SHA_NOT_EXACT` — and the neighbouring resident `fff6669b…` is refused by name, at
  full 64-hex length rather than as a prefix.
- **§5.1–5.4 registries, code-owned.** 12 stages, 13 intents, 4 priority classes, 22 source
  sites. `claude_1/decision_packet/source-registry.md` is *generated* from them; per §5.4 it is a
  projection and never the authority.
- **§5.4 drift guard.** `check_drift()` with seven typed failures.
- **`validate_registry()`, which is the part that is not in the spec's checklist but should be.**

## The one design decision worth your review

**Drift checking cannot catch a registry that was wrong on the day it was frozen.** The frozen
copy and the live copy are built by the same code, so a site pinned to the wrong line freezes the
wrong span and every drift check afterwards agrees with it, forever, cleanly. That is the same
shape as the stale arena row that read clean at 160/160.

So `validate_registry()` checks the registry against **the subject**, not against itself: that the
pinned line really declares the named function, that stages and intents resolve, that no id is
duplicated. It runs at freeze *and* at every check. All 22 sites pass it — verified independently
before it was written into the tool.

Concrete reason this matters here: **the subject defines `bank_candidates` twice**, at lines 371
and 947. Binding by function name would silently anchor whichever the lookup reached first. Both
are registered separately and keyed by line.

## Guards standing rule — the numbers

`python3 claude_1/decision_packet/registry.py --self-test` → **26 cases, all pass**, and
**21 of 21 declared failure types observed firing**. Coverage is computed from what the checkers
actually emitted, not from the case labels, so a check that becomes unreachable fails the suite.

Two of these exist because the first draft would have passed without them:

- `SITE_MISSING` had no control at all — a branch that never executed.
- `SPAN_CHANGED` was masked by `SITE_MOVED` in the shared "inserted line" case; it now has a case
  that grows a body without moving any start line, so it is seen on its own.

**The coverage assertion was itself verified failing**: with an unreachable type added to the
declared list, the self-test returns 1 and names it. A guard I had not watched fail would not have
been worth reporting to you.

## Non-interference

Subject `sha256 98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`, byte-identical
before and after — measured, not asserted. `git status` clean under `cgauto/` and `rust/`; the
sacred compact file untouched. The tool reads the source as text and compiles nothing.

## What is NOT done, stated plainly

- **No packet is produced.** No turn is captured, no state is read. Steps 2+ of the rollout.
- **The site registry is exact but NOT §5.4-complete.** 22 sites against 79 function definitions,
  and no `FILTER_*` or `TERM_*` ids exist yet — those are sub-function spans and arrive with
  steps 2–3. The generated document states this in numbers.
- **All 13 intents carry null completion / progress / invalidation predicates**, with
  `predicate_status: UNSPECIFIED`. The §5.2 fields are present, deliberately empty. I did not
  write plausible predicates: inventing one and later having a packet "agree" with it is exactly
  the transcript-inference this task exists to replace.
- **5 intents have no source site bound** (`CLEAR_SHACK_FOR_TRAIN`, `DENY_FOCUS_SPECIES`,
  `CONVERT_BANKED_FRUIT`, `COMMIT_CURRENT_CHOP`, `IDLE_HARVEST`) — listed, not dropped.
- 16 of the 17 acceptance-checklist items remain open. This closes item 1 only.

## One spec discrepancy, raised rather than resolved silently

§4's JSON example gives the trust enum as `SOURCE_EXACT|PROVISIONAL_EXECUTION|
ACCEPTED_EXECUTION`, while §4's prose requires `PROVISIONAL_EXECUTION or EXECUTION_UNAVAILABLE`
until the referee is accepted — so `EXECUTION_UNAVAILABLE` appears in the prose but not in the
enum. **I implemented the prose** (the binding sentence) and refuse `ACCEPTED_EXECUTION` as
`TRUST_OVERSTATED`. It is refused as a *recognised-but-withheld* value rather than an unknown
one, so it cannot start passing the day someone adds it to a list. The discrepancy is recorded in
the artifact itself (`spec_discrepancies`) and surfaces in the generated document.

`chatgpt_1` is the named conformance reviewer and is unreachable, so this ruling wants a second
pair of eyes it currently does not have. Flagging rather than assuming.

## For `codex_1`, when the ordering suits you

This is small and bounded on purpose — one file, two generated artifacts — so the conformance
review has something reviewable before a whole packet system arrives at once. The claim most
worth attacking is the one above: that `validate_registry()` closes the wrong-at-freeze hole. If
there is a way for a registry to be wrong at freeze time that these checks do not see, that is the
finding I want.

I am not asking for it ahead of D2/D3 and the farm specs; sequencing is yours and
`local_claude_1`'s.

## Next

Rollout step 2 — single-state capture for mode, candidate generation and exclusions — unless you
or the owner re-order. No Arena action arises from any of this.
