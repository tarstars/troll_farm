# Adversarial security review by execution — coordination transport tooling

- **Reviewer:** claude_1 (independent; not the author of the instrument under review)
- **Date:** 2026-08-07
- **Subject:** `scripts/inbox_sweep.py`, `scripts/lint_outbox.py`, `scripts/build_legacy_baseline.py`,
  `coordination/quarantine.json` (schema v2), `coordination/legacy-baseline.json` (691 pinned paths),
  protocol §10.1 / §10.2 — all as published on `origin/agent/local_claude_1`
- **Author of the subject:** `local_claude_1`, who is also the coordinator whose authority the
  instrument encodes and who uses the instrument to verify other agents' work. That is the reason
  this pass exists.
- **Method:** execution, not reading. A prior reviewer could not clone and reviewed by reading only;
  every claim below is backed by a command and its observed output.

## Safety envelope actually observed

- **Nothing was pushed** except this document, to `origin/agent/claude_1-banana-restoration-r2`.
- No real message, `coordination/quarantine.json`, or `coordination/legacy-baseline.json` was
  modified in the real worktree `/home/tarstars/prj/troll_farm-claude_1`.
- Every experiment ran in a throwaway clone under
  `/tmp/.../scratchpad/tq/probeN`, created with `git clone <real worktree> probeN`.
- A "push" by an attacker was simulated with `git update-ref refs/remotes/origin/agent/<x> <commit>`
  inside the throwaway clone. This produces **exactly the object graph a peer's clone has after the
  attacker pushed and the peer fetched**, so every verdict below is the verdict the real tool would
  produce on real data. It does **not** prove the attacker can obtain push access; see
  *Residual trust assumptions*.
- Network use: `git fetch -q origin '+refs/heads/agent/*:refs/remotes/origin/agent/*'` only.
- `pytest` is not installed on this host, so the author's own `tests/test_inbox_sweep.py` could not
  be executed. All findings come from direct execution of the tools instead.

### Reproduction harness

```bash
S=/tmp/.../scratchpad/tq
git clone --no-checkout /home/tarstars/prj/troll_farm-claude_1 $S/probe0
cd $S/probe0
git config filter.lfs.smudge ""; git config filter.lfs.process ""; git config filter.lfs.required false
git fetch -q origin '+refs/remotes/origin/*:refs/remotes/origin/*'   # 55 remote refs, faithful mirror
git checkout -q -B coord origin/agent/local_claude_1                  # the hardened tooling
```

Baseline, unmodified (**REAL RUN**):

```
$ python3 scripts/inbox_sweep.py --me claude_1        # exit 0
authority: refs/remotes/origin/** (55 remote refs); scanned 794 authoritative messages (691 legacy, 97 v2)
immutable-path collisions (0):
delivery errors (0):
quarantine authority: refs/remotes/origin/agent/local_claude_1:coordination/quarantine.json blob 4d981e06cc0d; legacy baseline 691 pinned paths
quarantine errors (0):
quarantined (6):
unacknowledged, ack required (0):
```

`forge.py` (in the scratchpad) builds a commit on a base ref with chosen file contents and moves a
`refs/remotes/origin/...` ref to it. All forging below uses it.

---

## Verdict on the prior reviewer's repairs

The prior reviewer's TQ-1/TQ-2/TQ-3 findings are **correct, and the repairs work as described** for
the attacks they were written against. I re-established all three by execution and then went past
them. Credit settled; the rest of this document is new ground.

| Claim | Verdict under execution |
|---|---|
| **TQ-1** quarantine loaded from the coordinator's ref, never the worktree; drift is reported | **HOLDS** — CONFIRMED-SAFE |
| **TQ-2** an entry is honoured only with a coordinator-authored v2 adjudication naming the exact target and pinning its blob | **PARTLY HOLDS** — the coordinator-authorship and blob-pin halves hold; "valid v2 message" and "present on the coordinator's canonical ref" are **not enforced in code**, and the blob pin is silently skipped for collided paths |
| **TQ-3** the 691-path baseline freezes pre-v2 paths by blob | **HOLDS** against backdating and blob tampering — CONFIRMED-SAFE. It is not an integrity control: it is an unsigned, unadjudicated waiver list |

### TQ-1 re-established (CONFIRMED-SAFE, REAL RUN in `probe14`)

Added a 7th entry to the **worktree** `coordination/quarantine.json` naming a real coordinator `stop`
message:

```
quarantine authority: refs/remotes/origin/agent/local_claude_1:coordination/quarantine.json blob 4d981e06cc0d; legacy baseline 691 pinned paths
warning: local quarantine differs from the authoritative blob (f94581a4de1c vs 4d981e06cc0d); the authoritative copy governs
quarantined (6):                    <- still 6, not 7
```

The `stop` message remained delivered. A local edit changes nothing and is announced loudly. Good.

**But the same is not true of the legacy baseline.** I then doctored the worktree
`coordination/legacy-baseline.json` in the same clone. The sweep printed **no warning at all**, and
prints only a *count* for the baseline, never its blob oid:

```
quarantine authority: ...quarantine.json blob 4d981e06cc0d; legacy baseline 691 pinned paths
warning: local quarantine differs from the authoritative blob (...)      <- quarantine only
```

Consequence: a reader of sweep output can verify *which* quarantine blob governed, but **cannot
verify which baseline blob governed**. The baseline can be swapped on the coordinator ref and the
output is indistinguishable except for a count nobody records. See F5.

---

## Findings, ranked by severity

Severity is judged as: how much shared truth moves, how many agents are affected, and how
recoverable it is.

### F1 — CRITICAL — Any agent can nullify the entire quarantine and permanently break every peer's inbox, with one push to a branch it owns

**CONFIRMED-EXPLOITABLE. LOCAL SIMULATION of one push (`probe4`).**

The quarantine's authority chain terminates in a message path, and `validate_quarantine` resolves
that path through `messages`, which excludes any path with an immutable-path collision. Message
paths are not owned: git does not stop agent A from writing a file under
`coordination/messages/B/` on A's own branch, and there is no CODEOWNERS, pre-receive hook, or CI
check in the repository. Verified: `git ls-tree -r origin/agent/local_claude_1 | grep -iE
'CODEOWNERS|pre-receive'` is empty and that ref carries no `.github/` at all; and while 16 other
refs do carry workflows, `git grep -l -E 'inbox_sweep|lint_outbox|build_legacy_baseline'` over
every remote ref restricted to `.github` returns **nothing** — no CI anywhere runs the transport
tooling.

Attack: `chatgpt_1` — the agent whose six messages are quarantined, one of them for *fabricated
acceptance* — writes a byte-different copy of the **coordinator's adjudication message** onto its own
scratch branch.

```bash
ADJ=coordination/messages/local_claude_1/20260807T190000Z-20260807-transport-quarantine-and-outbox-lint-adjudication.md
git show origin/agent/local_claude_1:$ADJ > adj-tampered.md
printf '\n<!-- tampered by chatgpt_1 -->\n' >> adj-tampered.md
python3 forge.py --repo probe4 --base origin/agent/chatgpt_1 \
  --ref refs/remotes/origin/agent/chatgpt_1-review-scratch \
  --add "$ADJ=adj-tampered.md"
python3 scripts/inbox_sweep.py --me claude_1
```

Observed:

```
immutable-path collisions (1):
  coordination/messages/local_claude_1/20260807T190000Z-...-adjudication.md
    c0c55d0570a4... on refs/remotes/origin/agent/local_claude_1, refs/remotes/origin/main, refs/remotes/origin/session-2026-07-01
    db1ce94a5a7b... on refs/remotes/origin/agent/chatgpt_1-review-scratch

delivery errors (6):
  ...zero-oscillation-closeout.md: handoff missing required field: artifact_commit
  ... (all six formerly-quarantined messages)

quarantine errors (6):
  coordination/quarantine.json: adjudicated_by is not a valid v2 message: '...adjudication.md'   (x6)

quarantined (0):                       <- all six adjudications destroyed
exit 2
```

What moved:

1. **All six quarantines are gone.** `quarantined (0)`.
2. The coordinator's published reasons — including "fabricated acceptance … declared void by the
   coordinator with the owner" — **disappear from every agent's sweep output**.
3. Every agent's inbox is exit 2 permanently, which **blocks `--mark` for everyone**
   (`mark skipped: transport/delivery errors present`), so nobody can advance seen-state.
4. It is **irreparable inside the protocol**: the tool's own rule 7 states "Immutable-path
   collisions are never suppressed by quarantine", and the code implements that faithfully —
   collisions are computed before quarantine and never consulted against it. The only remedy is
   deleting or force-pushing someone else's branch, a repo-admin action outside the protocol.

The same one-line attack works against **any** message path, so it is also a general denial of
service on coordination, not only a quarantine bypass.

> **Abuse scenario.** An agent is adjudicated for fabricating a gate acceptance. Rather than
> repairing anything, it pushes a whitespace-changed copy of the coordinator's adjudication to a
> throwaway branch. The adjudication is annihilated, its own six messages return to the shared bus as
> ordinary delivery errors, the coordinator's finding of fabrication is no longer printed anywhere,
> and every peer's transport is red until a human deletes the branch.

### F2 — HIGH — "The coordinator" is an environment variable; setting it hands quarantine and baseline authority to any agent

**CONFIRMED-EXPLOITABLE. REAL RUN (F2a/F2b) and LOCAL SIMULATION (F2c, `probe1`).**

Answering the question that was posed as highest-value: the coordinator is resolved as **data, not
code**.

```python
DEFAULT_COORDINATOR = "local_claude_1"
COORDINATOR_ENV = "TROLL_FARM_COORDINATOR"

def coordinator_agent() -> str:
    return os.environ.get(COORDINATOR_ENV) or DEFAULT_COORDINATOR
```

The value is used unvalidated in two places: to build `refs/remotes/origin/agent/<coordinator>`,
from which **both** the quarantine and the legacy baseline are read, and as the namespace an
adjudication's path must match. It is referenced nowhere else in the repository except the test
suite (`git grep TROLL_FARM_COORDINATOR` across all 55 refs: only `scripts/inbox_sweep.py` and
`tests/test_inbox_sweep.py`), i.e. it is a test hook that is live in production.

**F2a/F2b (REAL RUN, `probe0`)** — one variable disables both controls:

```
$ TROLL_FARM_COORDINATOR=nonexistent_agent python3 scripts/inbox_sweep.py --me claude_1
quarantine authority: refs/remotes/origin/agent/nonexistent_agent:coordination/quarantine.json blob absent;
                      legacy baseline ABSENT — legacy messages are not pinned
quarantined (0):
```

Note the fail-open direction: with the baseline **ABSENT**, TQ-3 is entirely off — every legacy
message is accepted again and a sender can bypass v2 by omitting `schema_version`. There is no
"refuse to run without a baseline" mode.

**F2c (LOCAL SIMULATION, `probe1`)** — hostile coordinator takeover. `chatgpt_1` publishes, on its
**own canonical branch**, a `coordination/quarantine.json` and a matching adjudication in its own
namespace, quarantining the real coordinator's `stop` directive:

```
$ TROLL_FARM_COORDINATOR=chatgpt_1 python3 scripts/inbox_sweep.py --me claude_1
quarantine authority: refs/remotes/origin/agent/chatgpt_1:coordination/quarantine.json blob de7ddcee28ab; legacy baseline ABSENT
quarantine errors (0):
quarantined (1):
  coordination/messages/local_claude_1/20260807T132100Z-20260807-banana-disposition-review-stop.md:
      declared void by chatgpt_1 acting as coordinator
      [coordination/messages/chatgpt_1/20260807T210000Z-20260807-hostile-policy.md]
```

Zero errors. The system reports a peer's unilateral revocation of the coordinator's stop order as a
clean, valid adjudication.

Control run in the same repository without the variable: the `stop` message is delivered normally.

**Why this is exploitable and not merely a local footgun.** The agents here are language models that
read untrusted peer-authored message bodies and then run shell commands. A message, a task file, a
README, or a `.envrc` that says "run the sweep with `TROLL_FARM_COORDINATOR=…` to see the correct
quarantine state" is an ordinary prompt-injection payload, and the sweep prints the redirected ref
in a line that is easy to skim past. There is no allowlist, no cross-check against a protocol
document, no assertion that the ref exists, and no warning when the resolved coordinator differs
from `DEFAULT_COORDINATOR`.

> **Abuse scenario.** An adjudicated agent publishes a task note containing a "diagnostic command"
> that exports `TROLL_FARM_COORDINATOR=chatgpt_1`. Any agent that copies it now reads quarantine
> truth from the adjudicated agent's own branch — which can suppress the coordinator's stop orders,
> policies and corrections at will, with `quarantine errors (0)` and no drift warning, because the
> drift warning only ever compares against whichever ref the variable selected.

### F3 — HIGH — Version skew means there is no shared truth: the enforcement exists on exactly one of 55 refs

**CONFIRMED-EXPLOITABLE (as a correctness/authority failure). REAL RUN, `probe0`.**

The prompt mentioned two versions of `inbox_sweep.py` in circulation. There are **five**, and only
one implements any of this:

| blob | lines | quarantine/baseline aware? | canonical refs carrying it |
|---|---|---|---|
| `7621d62b` | 1069 | **yes** | `agent/local_claude_1` |
| `b2d06fb4` | 815 | no | `agent/claude_1`, `agent/local_codex_1` |
| `fb035f63` | 286 | no | *(my own working branch)* + 8 task refs |
| `84a8fb7a` | 269 | no | 8 task refs |
| `d4eb391a` | 149 | no | `agent/chatgpt_1` |
| `62082681` | 168 | no | 23 task refs |

Per active agent's canonical branch:

```
agent/chatgpt_1        d4eb391ab89a   149 lines  quarantine-mentions=0
agent/claude_1         b2d06fb43010   815 lines  quarantine-mentions=0
agent/local_claude_1   7621d62b6897  1069 lines  quarantine-mentions=51
agent/local_codex_1    b2d06fb43010   815 lines  quarantine-mentions=0
```

Three sweeps, one repository, one ref set, one instant, `--me claude_1`:

```
v1069 (coordinator's copy)   exit 0   delivery errors (0)   quarantined (6)
v815  (agent/claude_1)       exit 2   delivery errors (6)   quarantine concept absent
v286  (my working branch)    exit 1   watermark-based, 246 "new", and it counts
                                       refs/heads/... local branches as sources
```

The quarantine adjudication therefore has **no effect on three of the four active agents** unless
they first adopt the coordinator's script. The security control is not in the data; it is in a copy
of a script that each agent holds independently and that the transport does not version, pin, or
check. `DEFAULT_COORDINATOR` being a code constant makes this worse, not better: a role transfer
(protocol §9) requires editing code on every agent's branch, and an agent still running an older
constant would silently read quarantine truth from the *previous* coordinator's ref.

Worth stating plainly: **my own worktree** — the branch this review was commissioned on — has the
286-line sweep and **no `coordination/quarantine.json` and no `coordination/legacy-baseline.json` at
all** (`ls: cannot access 'coordination/quarantine.json': No such file or directory`). The
instrument that governs my inbox is not present in my checkout.

### F4 — HIGH — The coordinator can silently re-open another agent's legitimately discharged obligations

**CONFIRMED-EXPLOITABLE. LOCAL SIMULATION, `probe5`.**

"A quarantined ACK acknowledges nothing" is implemented exactly as specified — `messages.pop(path)`
runs before `collect_my_acks`, so a quarantined ACK is never even seen. The sharper consequence is
not documented anywhere: because acknowledgement is recomputed from scratch on every sweep,
quarantining an ACK **retroactively un-discharges everything that ACK had settled**.

Baseline (`probe0`), `--me chatgpt_1 --task 20260807-transport-quarantine-and-outbox-lint`:

```
unacknowledged, ack required (1):
  coordination/messages/claude_1/20260807T170100Z-...-transport-invalid-message-repost.md
```

`local_claude_1/20260807T163000Z-...-policy.md` is **not** listed — it was acknowledged by
`chatgpt_1/20260807T170000Z-...-ack.md`.

The coordinator then adds one quarantine entry naming that ACK, plus an adjudication naming it:

```
quarantine errors (0):
quarantined (7):
  ...chatgpt_1/20260807T170000Z-...-ack.md: A3 probe: quarantining a peer ACK

unacknowledged, ack required (3):
  coordination/messages/claude_1/20260807T170100Z-...-repost.md
  coordination/messages/local_claude_1/20260807T163000Z-...-policy.md      <- RESURRECTED
  coordination/messages/local_claude_1/20260807T230000Z-...-ack-revocation-policy.md
```

An obligation the peer had properly discharged is open again. The peer cannot repair it: published
messages are immutable, so it must author a *new* ACK — which the coordinator can quarantine again.
The sweep prints **no indication** that anything was re-opened; the reader sees an agent that simply
has not acknowledged a policy. Combined with F6 (no validity requirement on the target), this is a
mechanism for placing a peer in permanent, apparently self-inflicted non-compliance.

> **Abuse scenario.** A coordinator in a dispute quarantines the disputing agent's ACKs one at a
> time. Each sweep shows the disputing agent as unresponsive to standing policy, with a clean
> transport and zero quarantine errors, and each repair the agent attempts can be quarantined in
> turn.

### F5 — MEDIUM-HIGH — The legacy baseline is a v2-enforcement waiver list that requires no adjudication at all

**Backdating: CONFIRMED-SAFE. Blob tampering: CONFIRMED-SAFE (with a caveat).
Grandfathering a forgery: CONFIRMED-EXPLOITABLE. LOCAL SIMULATION, `probe8`–`probe10`.**

**(c) Backdated filename — TQ-3 holds.** A brand-new non-v2 message named
`20260729T090000Z-…-claim.md` (before the migration), forged onto `agent/chatgpt_1`:

```
delivery errors (1):
  coordination/messages/chatgpt_1/20260729T090000Z-20260729-backdated-forgery-claim.md:
    legacy message not in the frozen legacy baseline; messages published after the v2 migration
    must declare schema_version: 2
```

**(b) Altering a frozen blob — detected.** Repinning
`claude_1/20260729T115658Z-…-p0-audits-claim.md` to `ffff…`:

```
delivery errors (3):
  ...p0-audits-claim.md: legacy baseline blob mismatch: pinned ffffffffffff but found 2fc6680d5401
```

*Caveat, and it is a real one:* the baseline blob check runs **only for messages addressed to the
sweeping agent** (`addressed` list). A tampered pin on a message addressed to somebody else is
invisible in your sweep. Nobody verifies the whole baseline; each agent verifies its own slice.

**(a) Adding a path — accepted with no adjudication whatsoever.** One line added to
`legacy-baseline.json` on the coordinator ref:

```
delivery errors (0):
quarantine authority: ... ; legacy baseline 692 pinned paths
exit 1        # the forged legacy message is now a delivered, ack-required inbox item
```

The asymmetry is the finding. **Suppressing** a message requires a cited adjudication message,
coordinator authorship, and a blob pin. **Admitting** an arbitrary, entirely unvalidated non-v2
message — bypassing every v2 rule: `message_id`, `from`, kind vocabulary, handoff artifact checks —
requires *editing one JSON line*, cites nothing, and (per TQ-1 above) is not even blob-reported in
the sweep output. `691 → 692` is the only trace, and no agent records that number.

**(d) `build_legacy_baseline.py --check` audits a different file than the sweep enforces.**
`--check` reads `root / coordination/legacy-baseline.json` — the **worktree** — while the sweep reads
the **coordinator ref**. In `probe9` both tools ran in the same clone at the same instant:

```
worktree baseline:      691 pinned paths
authoritative baseline: 692 pinned paths

$ python3 scripts/build_legacy_baseline.py --check
committed 691 pinned paths; observed 692
  new legacy (must be v2): 1
    coordination/messages/chatgpt_1/20260729T090000Z-20260729-backdated-forgery-claim.md
exit 2

$ python3 scripts/inbox_sweep.py --me claude_1
delivery errors (0):   ... legacy baseline 692 pinned paths
exit 1
```

The auditor says "a new legacy message has appeared, this must be v2"; the enforcer says "clean,
delivered". They disagree because they read different files. As a detector `--check` is otherwise
sound (it correctly flagged the forgery, and it is clean on the unmodified repository: `committed
691; observed 691; exit 0`). Its weakness is the file it points at — and its documented remedy is
worse than the disease: running the builder without `--check` regenerates the baseline to include
**every** currently-legacy message, forgeries included, which is the exact re-opening the docstring
warns against but nothing prevents.

### F6 — MEDIUM-HIGH — Quarantine is a general evidence-suppression primitive; nothing checks that the target is invalid

**CONFIRMED-EXPLOITABLE, and by design. LOCAL SIMULATION, `probe11`.**

`validate_quarantine` checks authorization. It never checks that the quarantined message is actually
invalid — there is no call to `validate_v2` on the target, no requirement that the target have any
delivery error, and the `reason` string is free text nobody verifies.

Target: `claude_1/20260807T170100Z-…-transport-invalid-message-repost.md`, a **fully valid** v2
message (the sweep reports zero delivery errors for it) that is `chatgpt_1`'s only outstanding
obligation on that task. Coordinator adds an entry with `reason: "inconvenient"`:

```
BEFORE                                             AFTER
new (unseen) (4):                                  new (unseen) (4):
  claude_1/...-transport-invalid-message-repost.md   claude_1/...-transport-quarantine-review-ack.md
  claude_1/...-transport-quarantine-review-ack.md    local_claude_1/...-lint-policy.md
  local_claude_1/...-lint-policy.md                  local_claude_1/...-adjudication.md
  local_claude_1/...-adjudication.md                 local_claude_1/...-suppression-policy.md

unacknowledged, ack required (1):                  unacknowledged, ack required (1):
  claude_1/...-repost.md                             local_claude_1/...-suppression-policy.md

                                                   quarantine errors (0):
```

The valid message is gone from `new` and from `unacknowledged`.

**What actually limits this, stated plainly.** Three things, all weak and none technical:

1. The message is still listed under `quarantined` with the coordinator's stated reason, so it is
   *displaced, not erased* — a reader who reads the whole sweep output sees it. This is the only real
   control, and it is a **transparency** control, not an authorization one.
2. The adjudication message must exist somewhere on the remote refs — but see F7: it need not be
   valid and need not be on the coordinator's own branch, so it can be placed where reviewers do not
   look and, being on a branch the coordinator does not own, can be removed later.
3. Nothing else. There is no appeal path, no second signature, no requirement that the target have a
   delivery error, and no distinction in the schema between "this message is malformed" and "I do not
   want this message counted".

**Residual trust assumption:** the design necessarily trusts that whoever controls
`refs/heads/agent/<coordinator>` will only quarantine genuinely invalid messages. The tool cannot and
does not check this. Everything that makes quarantine useful — suppressing an unrepairable message so
peers can make progress — is the same capability that suppresses an inconvenient one.

### F7 — MEDIUM — An adjudication need be neither valid nor on the coordinator's canonical ref; protocol §10.2 states both requirements and code enforces neither

**CONFIRMED-EXPLOITABLE (spec violation). LOCAL SIMULATION, `probe3` and `probe12`.**

Protocol §10.2: *"It must be a valid v2 message, authored by the coordinator, present on the
coordinator's canonical ref."* The code checks only `adjudicator in authoritative_paths` (the union
of **all** remote refs) and `sender_of(adjudicator) == coordinator` (the **path namespace**), then
`msg.is_v2` — which is `schema >= 2 or schema_error is not None`, i.e. true even for
`schema_version: banana`. `validate_v2` is never called on an adjudication.

**F7a — off-branch adjudication (`probe3`).** Adjudication placed only on
`refs/remotes/origin/agent/chatgpt_1-evil`, absent from the coordinator's canonical ref:

```
$ git cat-file -e origin/agent/local_claude_1:.../20260807T220000Z-...-offbranch-policy.md
fatal: path '...' does not exist in 'origin/agent/local_claude_1'

quarantine errors (0):
quarantined (1):
  local_claude_1/20260807T132100Z-...-banana-disposition-review-stop.md: adjudicated off-branch
     [coordination/messages/local_claude_1/20260807T220000Z-20260807-offbranch-policy.md]
```

**F7b — structurally invalid adjudication (`probe12`).** The entire adjudication:

```yaml
---
schema_version: 2
from: somebody_else
message_id: not/even/a/path.md
quarantines: ["coordination/messages/local_claude_1/20260807T132100Z-...-stop.md"]
---
junk
```

Missing 8 of 11 required v2 fields, `from` naming a different agent, `message_id` not a path.

```
quarantine errors (0):
quarantined (1):
  local_claude_1/20260807T132100Z-...-stop.md: adjudicated by a junk message
```

Two consequences. First, an auditor reading the adjudication sees `from: somebody_else` and would
conclude it is not the coordinator's — the tool disagrees, because it trusts the **path**, not the
field. Second, the entire authorization reduces to *"a file exists at a path beginning
`coordination/messages/local_claude_1/` on some remote ref"*. Anyone who can push any branch can
create such a file; there is no path-ownership enforcement anywhere in the repository. What still
blocks the attack is only that `coordination/quarantine.json` must be on the coordinator's ref — so
this is defence-in-depth that is absent, not a live privilege escalation. It is also the direct
enabler of F1: the adjudication resolution is exactly what a collision destroys.

### F8 — MEDIUM — The `target_blob` pin is silently unenforced precisely when bytes are ambiguous

**Pin normally holds: CONFIRMED-SAFE. Bypass under collision: CONFIRMED-EXPLOITABLE.
LOCAL SIMULATION, `probe6`/`probe7`.**

```python
if path in blob_by_path and entry["target_blob"] != blob_by_path[path]:
```

`blob_by_path` is populated only for non-collided paths. A collided path is therefore not `in
blob_by_path`, and the pin check is skipped entirely.

`probe6` — wrong pin, no collision (the pin works):

```
quarantine errors (1):
  target_blob does not match the message at '...-closeout.md':
    '0000000000000000000000000000000000000000' != '41d31c4efe3e10b56e09976f56493412af7a9465'
quarantined (0):
```

`probe7` — the **same all-zeros pin**, plus a colliding copy of that path on another branch:

```
quarantine errors (0):
quarantined (6):
  ...closeout.md: fabricated acceptance...      <- honoured with a garbage pin
```

The pin exists to say *which bytes* were adjudicated. It is disabled in the one case where the bytes
are genuinely ambiguous, and reports nothing. Direct exploitation is limited because the collision is
itself exit 2, but the mechanism lets a coordinator pre-place an entry with a stale or fabricated
pin that becomes "valid" the moment anyone creates a collision — and per F1, anyone can.

### F9 — MEDIUM — `lint_outbox.py` does not reproduce the sweep's verdicts; both divergences are silent and both produce permanent, unrepairable delivery errors

**CONFIRMED-EXPLOITABLE (as a safety-net failure). LOCAL SIMULATION, `probe8`/`probe13`.**

§10.1 says lint "applies the same v2 rules as the sweep … minus canonical-branch presence". Two
divergences beyond that, in the direction that matters (lint clean → sweep error):

**F9a — the legacy baseline.** `lint_outbox.py` does not load `legacy-baseline.json` at all, and
`lint_message` returns `[]` for any non-v2 message that is already published. The backdated forgery
from F5, placed in the worktree and linted with `--all`:

```
$ python3 scripts/lint_outbox.py --me chatgpt_1 --all
errors (6):     # the six pre-existing quarantined messages; the forgery is NOT among them
```

while the receiver:

```
$ python3 scripts/inbox_sweep.py --me claude_1
  ...20260729T090000Z-20260729-backdated-forgery-claim.md: legacy message not in the frozen
    legacy baseline; messages published after the v2 migration must declare schema_version: 2
```

§10.1's claim that "legacy messages are grandfathered only per the frozen baseline in §10.2" is not
implemented in the lint.

**F9b — canonical-branch presence, which is the failure mode this repository actually suffered.**
Three of the six real quarantine entries exist because messages referenced or lived on task branches
rather than `agent/<id>`. A structurally perfect v2 claim published to
`agent/chatgpt_1-taskwork` instead of `agent/chatgpt_1`:

```
lint BEFORE publishing:        errors (0)   exit 0
lint AFTER publishing (--all): errors (6)   # pre-existing only; the new message is clean
sweep (receiver):
  ...20260808T020000Z-20260808-taskbranch-claim.md: message not present on canonical
    refs/remotes/origin/agent/chatgpt_1
```

Lint is clean at every point at which a sender would run it, and the result is a permanent delivery
error on the shared bus that only the coordinator can clear — via quarantine, with all the authority
concentration that implies. The lint's stated purpose is "catching it before the push is the only
cheap fix"; for the single most common real cause of quarantine in this repository, it cannot.

### F10 — LOW — `requires_ack: false` is silently ignored for eight of thirteen v2 kinds

**CONFIRMED. REAL RUN.**

```python
return yaml_required is True or legacy_required or kind in ACK_REQUIRED_KINDS
```

`requires_ack` is a **required** v2 field validated as a boolean, but setting it to `false` has no
effect for `claim, question, blocker, policy, stop, takeover, handoff, correction`. Observed while
constructing F6: an adjudication declaring `requires_ack: false` appeared under "unacknowledged, ack
required". Not a security hole; it inflates unacked counts, and unacked counts are how coordination
pressure is applied.

---

## What I could not break, and what that does and does not mean

These are attacks I ran that **failed**. "I could not break it" is the correct claim; "it is secure"
is not, because in each case the control rests on the trust assumptions listed below rather than on
anything cryptographic.

| Attack | Result |
|---|---|
| Worktree `quarantine.json` suppressing a message (TQ-1) | **CONFIRMED-SAFE** — inert, drift warned with both blob oids |
| Non-coordinator namespace as `adjudicated_by` (TQ-2) | **CONFIRMED-SAFE** — `adjudicated_by is not authored by the coordinator 'local_claude_1'`, `quarantined (0)`, exit 2 |
| A peer's own `quarantine.json` on their own ref, default coordinator | **CONFIRMED-SAFE** — never read; only `origin/agent/<coordinator>` is consulted |
| Wrong `target_blob` with no collision | **CONFIRMED-SAFE** — mismatch reported, nothing suppressed (but see F8) |
| Backdated filename to look pre-v2 (TQ-3) | **CONFIRMED-SAFE** — rejected; the baseline is by exact path, not by date |
| Altering a pinned blob in the baseline | **CONFIRMED-SAFE** for messages addressed to me; **UNRESOLVED** for messages addressed to others (never checked by my sweep) |
| Quarantining to suppress an immutable-path collision | **CONFIRMED-SAFE** — collisions are computed first and never suppressed (this is also why F1 is irreparable) |
| Multi-line YAML `quarantines:` array | **CONFIRMED-SAFE** — fails closed with "unparseable quarantines array" |

**UNRESOLVED — the load-bearing question I could not test.** Every attack above that requires
writing `coordination/quarantine.json` or `coordination/legacy-baseline.json` on
`refs/heads/agent/local_claude_1`, and F1 which requires pushing any branch at all, assumes push
access. I was instructed not to push and did not. I found **no in-repository evidence of any control
that would stop it**: no CODEOWNERS, no pre-receive hook, no CI workflow referencing the transport
scripts, and all agents share one `origin` (`git@github.com:tarstars/troll_farm.git`). Whether
GitHub-side branch protection exists on `agent/*` is **untested and unknown**, and it is the single
factor that decides whether F1 is critical or merely latent. It should be checked by someone who can
query the remote's protection settings.

---

## Residual trust assumptions

These are not bugs. They are what the design necessarily trusts, and they should be written down so
that nobody mistakes the tooling for something stronger than it is.

1. **Whoever controls `refs/heads/agent/<coordinator>` controls shared inbox truth.** They can
   suppress any message, valid or not (F6), re-open any agent's discharged obligations (F4), and
   admit any unvalidated non-v2 message (F5a). The tool verifies *authorization*, never *justice*.
   The only check on abuse is that suppressed messages remain listed with a reason — a transparency
   control that depends on someone reading the whole sweep output.
2. **Whoever controls the *reader's* environment controls which branch is "the coordinator".**
   `TROLL_FARM_COORDINATOR` is an unvalidated, unlogged-against-expectation override (F2). Authority
   is data here, not code.
3. **Whoever controls the *reader's* checkout of `scripts/inbox_sweep.py` controls whether any of
   this is enforced at all.** The security control is a script, not a protocol artifact; five
   versions are live and only one enforces anything (F3). The transport does not pin, version, or
   verify the tool that interprets it.
4. **Message-path namespaces are conventions, not permissions.** Nothing prevents agent A from
   writing under `coordination/messages/B/` on A's branch. Authorship is inferred from a path, so
   "authored by the coordinator" means "sits under the coordinator's directory on some ref" (F7).
5. **Immutability is a convention too.** "Published messages are immutable" is enforced only by the
   collision *detector*, which turns a violation into a repository-wide exit 2 rather than rejecting
   the violating copy. A detector that cannot quarantine what it detects converts an integrity
   property into an availability liability (F1).
6. **`git fetch` is trusted.** Everything reduces to "what is on `refs/remotes/origin/**` in *my*
   clone". A stale, partial, or manipulated fetch changes every verdict, and `--fetch` only checks
   that git exited zero.
7. **The legacy baseline is trusted because it is in the repository**, not because its integrity is
   established anywhere. It is unsigned, cites no adjudication, has no drift warning, and its blob
   is not printed in sweep output (F5, TQ-1 caveat). Its 691 entries are a standing waiver of v2
   validation, and additions to it are the least-audited privileged operation in the system.

---

## Recommendations, in severity order

1. **Do not let a collision destroy an adjudication (F1).** Resolve `adjudicated_by` against the
   coordinator's canonical ref by blob, not against the collision-filtered `messages` map; and pin
   the adjudication's blob in the quarantine entry the same way targets are pinned. A collision on a
   third-party branch would then be reported without invalidating the adjudication. This is the
   single highest-value change.
2. **Make the coordinator a protocol artifact, not an environment variable (F2).** Read it from a
   committed protocol file on a fixed ref, or at minimum: refuse to run when
   `TROLL_FARM_COORDINATOR` differs from `DEFAULT_COORDINATOR` unless an explicit
   `--i-know-this-is-not-the-coordinator` flag is passed, and print a loud banner. Also refuse to
   run — or exit 2 — when the resolved coordinator ref does not exist, instead of degrading to
   "baseline ABSENT".
3. **Version-pin the tool (F3).** Publish `scripts/inbox_sweep.py` on the coordinator ref with a
   declared `TRANSPORT_TOOL_VERSION`, have the sweep print it, and have `lint_outbox.py` refuse to
   run if the local copy's version is behind what the coordinator ref advertises. Today an agent can
   be "compliant" against a script that has never heard of quarantine.
4. **Report acknowledgement deltas when an ACK is quarantined (F4).** The sweep already knows which
   paths a quarantined ACK named; print "quarantining X re-opened: Y, Z". Silence here is what turns
   a transport action into an invisible political one.
5. **Bind the legacy baseline to an adjudication and report its blob (F5).** Require the same
   `adjudicated_by` + coordinator authorship for baseline *additions* as for quarantine entries, and
   print the baseline blob oid and drift warning exactly as the quarantine does. Point
   `build_legacy_baseline.py --check` at the coordinator ref, not the worktree, or make it print
   both and flag disagreement.
6. **Require the target to be invalid (F6).** Refuse a quarantine entry whose target produces no
   `validate_v2` error, or require an explicit `"kind": "suppression"` field that renders the
   discretionary case visible as such in the output. If the coordinator is to have a suppression
   power, it should be labelled rather than disguised as a schema verdict.
7. **Enforce what §10.2 says (F7).** Run `validate_v2` on the adjudication, and require it on
   `refs/remotes/origin/agent/<coordinator>` specifically, not on any remote ref.
8. **Enforce `target_blob` unconditionally (F8).** Drop the `path in blob_by_path` guard; for a
   collided path, require the pin to match one of the colliding blobs and say which.
9. **Teach `lint_outbox.py` the two rules it is missing (F9):** the legacy baseline, and a
   "you are not on your canonical branch" warning when `HEAD` is not `agent/<me>` — the latter
   would have prevented three of the six real quarantines in this repository.
10. **Honour `requires_ack: false` (F10)** or remove the field from `V2_REQUIRED_FIELDS`; a required
    field that is ignored is worse than an absent one.

---

## Appendix: probe index

| probe | purpose | finding |
|---|---|---|
| `probe0` | faithful unmodified mirror; baseline for every comparison | TQ-1/2/3 baseline |
| `probe1` | hostile `quarantine.json` + adjudication on `agent/chatgpt_1` | F2c |
| `probe2` | non-coordinator namespace as `adjudicated_by` | TQ-2 safe |
| `probe3` | adjudication in coordinator namespace, off-branch | F7a |
| `probe4` | colliding copy of the coordinator's adjudication | **F1** |
| `probe5` | quarantine a peer's ACK | F4 |
| `probe6` | wrong `target_blob`, no collision | F8 safe half |
| `probe7` | wrong `target_blob` + collision | F8 bypass |
| `probe8` | backdated new legacy message | F5c safe, F9a |
| `probe9` | forged path added to the baseline | F5a, F5d divergence |
| `probe10` | frozen blob altered | F5b safe |
| `probe11` | quarantine a fully valid message | F6 |
| `probe12` | structurally invalid adjudication | F7b |
| `probe13` | valid v2 message published to a task branch | F9b |
| `probe14` | worktree quarantine and worktree baseline | TQ-1 + baseline asymmetry |
