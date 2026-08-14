---
schema_version: 2
type: handoff
task_id: 20260814-iteration-3-work-plan
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260814T162849Z-20260814-iteration-3-work-plan-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: f0f9d74c8eb8beefbe782109a949b93caa004585
artifact_paths: ["claude_1/h3a-a5-trigger-preflight-2026-08-14.md", "claude_1/h3a-preflight-integrity-gate.py", "claude_1/h3a-preflight-integrity-gate-result.json"]
created_utc: 2026-08-14T16:28:49Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260814-iteration-3-work-plan
- Requires acknowledgement: yes

# A-5 delivered: trigger preflight **PASS** on all five gates — and the fifth gate did not exist

## For the owner, in plain terms

The H3a idea is *"when the bot is short-handed, play differently."* Before building anything to
test whether that helps, we check the cheap thing: **does the short-handed condition actually
happen in the archived games where the idea would need it?** A condition that never occurs cannot
be worth acting on, and finding that out takes hours instead of days.

**It happens.** In **9 of 10** disaster games the condition turns true by turn 150. In **10 of 10**
it turns true *before* the collapse started — early enough to act on, not just a symptom of the
wreckage. In the **7 comparison games the bot won** it fired **0 times** by turn 150, so it is not
simply always-on. And in **9 of 10** disasters there was a real move afterwards that the idea would
have handled differently.

**One thing had to be fixed before I could report any of that.** The check that confirms the input
data is what it claims to be was described in the analyzer's own documentation and **had never been
written**. I wrote it, and — before trusting it — deliberately corrupted each of its seven parts in
turn to confirm it rejects them.

**PASS here does not mean the idea works.** It means the expensive comparison is now worth
building. That comparison is the next item and it is not started.

## Result

Artifact `f0f9d74c`; report at `claude_1/h3a-a5-trigger-preflight-2026-08-14.md`.

| gate | requirement | result | |
|---|---|---|---|
| 1 | true by turn 150 in ≥8/10 catastrophes | **9 / 10** | PASS |
| 2 | first true turn precedes the collapse in ≥8/10 | **10 / 10** | PASS |
| 3 | false positive by turn 150 in ≤20% of 7 matched wins | **0 / 7** | PASS |
| 4 | ≥1 ETA-6-eligible scoring decision after activation, ≥6/10 | **9 / 10** | PASS |
| 5 | identities, turns, provenance, ETA semantics, counts consistent | **7 / 7 checks** | PASS |

**Input reachability, checked first as you instructed:** A-5 is **not** storage-blocked. All six
inputs are committed in-repo and each hash-matches the task record's frozen value — the two package
gzips, both manifests, and the membership CSV. Nothing sat behind the unmounted volume.

**Gates 1–4 were re-run, not cited.** A result JSON existed from 2026-08-10; a committed number is
not evidence that it still reproduces. The re-run is **byte-identical** to it.

## Gate 5 was named in the code and never executed

`h3a-conditioned-value-unblock-preflight.py` states in its docstring that it evaluates *"the four
pinned Phase-A2 gates **plus the integrity gate**."* It assigns `gate1`…`gate4` and computes no
fifth. **A gate that is documented, absent, and therefore incapable of failing** — the exact shape
G6 spent a week removing from the detector audit, found here in the analyzer for the
highest-priority route.

Implemented at `claude_1/h3a-preflight-integrity-gate.py`: hashes of all six inputs against the
task record, exact cohort identities, three independent count sources agreeing on 5,100 rows,
per-game row counts, ETA semantics against the frozen reconstruction record, the package's own
exact-IDs/no-sealed-data assertions, and that the locked resident is the sacred `fff6669b…`.

**Every check observed failing first.** `--self-test` sabotages each of the seven in turn and
requires the gate to fail; all seven do. One design point worth carrying: the check compares
on-disk bytes to **the task record's** frozen hashes, not to the manifest's own — a manifest can
be perfectly self-consistent while describing different data, and only an external anchor catches
substitution.

## Two boundary facts I am not smoothing over

Both are places where a looser reading would have improved my result:

- The gate-1 miss is game `897782213`, activating at turn **169** — after the line. It still
  counts for gate 2 (169 precedes its collapse at 200), which is why gate 2 reads 10/10 while
  gate 1 reads 9/10. Different gates, different questions, not merged.
- Matched win `897781674` activates at **169**. Gate 3 is scoped *by turn 150*, so it is not a
  false positive as written. Unscoped it would be 1 of 7 — still inside the 20% allowance, so the
  verdict does not turn on it, but the headline number does, and 0/7 should not travel without
  that sentence.

## What A-6 inherits, unchanged

PASS licenses building the comparison; it does not suggest the conditioning has value. Carried
forward: the state package is a **reconstruction, not a continued-RNG replay** — admissible for
this retrospective audit, **forbidden for the Phase-C value panel**; the substrate blockers (213
numeric alias crashes, RNG divergence, empty `MSG ;`) are A-6's first scope; 232
WAIT-canonicalized no-landing moves and referee-derived tree dynamics remain disclosed residual
risks; any value claim needs **5 runs per arm at σ = 1.501**.

**A-6 is not started and I will not start it until this is accepted.** I authored A-5 and review
none of it. Read-only throughout: no analyzer, data, candidate, corpus or Arena state changed.
