---
schema_version: 2
type: handoff
task_id: 20260815-oscillation-deep-dive
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260815T193500Z-20260815-oscillation-deep-dive-p1-increment2a-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260815T154500Z-20260815-oscillation-deep-dive-four-message-ack.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: e43d000b20fbf78965566cf262609e8b028fcc93
artifact_paths: ["claude_1/decision_packet/inventory.py", "claude_1/decision_packet/required-site-inventory.json"]
created_utc: 2026-08-15T19:35:00Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260815-oscillation-deep-dive
- Requires acknowledgement: yes

# handoff: P-1 increment 2a — the registry names 53% of what the contract requires. Measured against the source, not against itself.

## For the owner, in plain terms

Last time a reviewer showed that my "completeness check" was circular: it compared my list of
important places in the bot's code against *the same list*. Of course it passed.

This increment fixes that by counting the important places **from the code itself**. The result:
the contract requires ids for about **249** places; my registry currently names **132** of them —
**53%**. So the honest answer to "is the foundation complete?" is no, and now there is a number
instead of an impression.

**The most useful thing it found:** the registry does not mention `endgame_candidates` at all —
the part of the bot that the goal-doctrine appendix says contains the two biggest score rules
(C2 and C3). We have been discussing that code all day and my registry never named it.

## What was delivered

Artifact `e43d000b20fbf78965566cf262609e8b028fcc93` on `agent/claude_1`, pushed and remote-verified.

`codex_1`'s review named the requirement exactly: *"an independently curated required-site
inventory … not comparison with the same `SITES` list used to build the registry."* This is the
first half — the derivation. **`enumerate_sites()` never reads `registry.SITES`.**

§5.4's classes are enumerated from the source text:

| §5.4 class | enumerated as | required | named | unnamed |
|---|---|---|---|---|
| generator | every `fn` definition | 79 | 22 | **57** |
| score term | every `Candidate{` construction | 20 | 12 | 8 |
| filter | `.filter(` / `.retain(` / `continue` | 76 | 52 | 24 |
| early return | every `return` | 58 | 34 | 24 |
| arbitration | `.max_by` / `.min_by` / `.sort` | 16 | 12 | 4 |
| **total** | | **249** | **132 (53%)** | **117** |

## Independence is tested, not claimed

The property the review asked for is the one I could most easily fake, so it is a test:

- **enumeration is byte-identical with `registry.SITES` cut to three entries** — the derivation
  genuinely does not consult it;
- **coverage falls 132 → 13 when the registry shrinks** — so coverage moves with the thing it
  measures, rather than being a constant dressed as a measurement.

7 self-test cases, including a control proving the comment/string stripping is not vacuous: a
line containing only `// return continue Candidate{` mints no site, while a real `return 1;` does.

## Concrete omissions — offered as CANDIDATES, not as findings I certify

These are the mappings a curator should rule on. I derived them; I am not the person who should
bless them.

- **`endgame_candidates` (`:1233`) — absent from the registry entirely**, holding 15 unnamed
  sites including **3 score-term constructions**. `codex_1`'s D3 review placed C2's 10,000 CHOP
  overwrite and C3's 9,000/8,000 conversion planting *inside this function*. The registry omits
  the generator carrying the bot's largest score constants.
- **`idle_harvest_candidates` (`:1340`) — absent.** Increment 1 reported `IDLE_HARVEST` as one of
  five intents with **no source site bound**. Here is a function whose name matches it exactly.
  That is a candidate mapping and it wants a human ruling, not my say-so.
- **`endgame` (`:1371`), `focus_type` (`:341`), `carries_committed_fruit` (`:965`) — absent**, and
  plausibly relevant to the routing layer, `DENY_FOCUS_SPECIES` and `COMMIT_CURRENT_CHOP`
  respectively. Same caveat, more strongly: name similarity is not semantics.

## Limits, stated rather than discovered later

- **The class matchers are proxies.** A `continue` that skips a malformed row is not a semantic
  filter, and this code cannot tell the difference. The count 249 is therefore an upper bound on
  genuine §5.4 sites, not a target to hit.
- **Coverage measures NAMING, not correctness.** A site inside a registered span counts as
  covered even if its stage or intent is wrong. The semantic-mapping gap `codex_1` opened is
  **still open** and nothing here closes it.
- Status in the artifact is `PROPOSAL_FOR_INDEPENDENT_REVIEW`, carried inside the JSON.

## What I am asking for, and what I will not do

Per my commitment in the review ack and your disposition: **I will not curate what I derived.**
The inventory needs someone who did not write it to rule on which of the 249 are genuine §5.4
sites and which proxy hits are noise.

`codex_1` is the natural reviewer but is already carrying the spec v3 re-review. **Sequencing is
yours** — I am not blocked either way, because the next build step (packet/event schema) does not
depend on the curation landing first, only the *freeze* does.

## Next

P-1 increment 2b: the packet/event schema — the part of step 1 that `ENVELOPE_CONTRACT` explicitly
is not. Then registry completion against whatever survives curation.

## Boundaries

Subject byte-exact `98628e98…`; `rust/`, `cgauto/` and the frozen library untouched; registry
drift check still PASS and its 26-case suite still green. No Arena action.

**One transport note against myself:** I mangled a commit message with an unescaped backtick, then
amended a commit that was already pushed. The amend was rejected on push and I **reset to the
remote rather than force-pushing** — published history stays immutable. The tree is identical; only
one parenthetical word is missing from `e43d000b`'s message, and this message carries the full
statement.
