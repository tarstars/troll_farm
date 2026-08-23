# Unified review — Phase 3b anti-benching G-d/G-e

- Task: `20260820-pair-selector-anti-benching`
- Builder handoff: `agent/codex_1@f167c8e660b9cda642eba3701cde102e9f8712cb`
- Builder artifacts: `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196`
- Fresh-eyes review: `agent/chatgpt_1@c67244197bec5ff59a3b5e59f10430c0197af639`
- Executable reproducer and unified-verdict reviewer: `local_codex_1`
- Verdict: **`PACKAGE_REPRODUCED; BLOCKED_FIRST_FALSIFIER`**

## Decision

The exact r2 candidate is stopped at the named-cost panel gate (G-d). It fails three independent
hard R-3 requirements on the locked 240-game population:

| hard measurement | exact P1+P2 base | r2 candidate | verdict |
|---|---:|---:|---|
| blocking games | 35 | 115 | **FAIL: +80** |
| de-novo blocking games | — | 80 | **FAIL** |
| healed blocking games | — | 0 | no offset |
| games with a new P3 orchard-inertness failure | — | 5 | **FAIL** |
| games with a new P4 liveness failure | — | 73 | **FAIL** |
| games with a new `r5-horizon` flag | — | 0 | clean on this clause only |

The candidate therefore cannot qualify. The frozen design names any new or worse P3, P4, or
`r5-horizon` event as a downstream-commitment falsifier and says G-d/G-e stop on it; aggregate
improvement cannot waive it. Here blocking also worsens by 80 games and there is no healing.
Stopping before the real-progress gate (G-e) was correct. Running G-e could not rescue r2 and would
violate the first-falsifier rule.

## Independent executable reproduction

### Identities and transport

- The handoff is valid on the sender's canonical ref; its full artifact commit is reachable and all
  six declared paths exist there.
- At both the panel checkout `e6cb7523d87d4da02e6f81406d572e3e83e4cf10` and accepted build
  `09ed550f91936818425ad2611c1b875531f32a35`, the candidate hashes to
  `457360589a65cb2662950761deba817852ea9eb0d2c53b05a3e6fd2ab9dfda8a` and the exact base hashes to
  `5e1f4df406480f678ff03677cdda0f69d510c5c94efe90d4f0a8231b70c3339e`.
- The committed base-panel JSON is byte-identical to
  `claude_1/picker2/panel-door1-cand.json` at the panel checkout (Git blob
  `c3e9e49d311400261d26b068c62a31a4c0fcf5ee`, SHA-256
  `41e3be878b590998e69b9d690559daa87db0ed959b11ec142879c9af75b27a5b`).
- The panel and engine hashes reproduce as `d8900abf…` and `7c240abf…`; the sacred resident remains
  byte-exact at SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

### Full 240-game rerun

The builder did not commit the package-local runner named in its claim, so I supplied a
path-independent review runner that reconstructs the config from the accepted locked config,
verifies the exact checkout and four input hashes, reruns the real panel, and compares the complete
game rows with the submitted packet:

```text
git worktree add --detach /tmp/gdge-claude e6cb7523d87d4da02e6f81406d572e3e83e4cf10
git worktree add --detach /tmp/gdge-codex 35d569f2b78c90dd7c15b46183376cc95efa7196
python3 local_codex_1/reviews/run_gd_blocker_full_reproduction.py \
  --claude-checkout /tmp/gdge-claude \
  --codex-artifact-checkout /tmp/gdge-codex \
  --output-dir /tmp/gdge-local-review
```

The panel returned its expected scientific exit 1 (`BLOCK`): 240 games, 115 blocking, two flagged,
zero gate-unready. Every one of the 240 rerun game rows equals the submitted game row. The complete
JSON packets are equal after removing only measured wall time (11.4 seconds locally versus 17.6 in
the submitted run).

### Independent keyed audit

`local_codex_1/reviews/reproduce_gd_blocker.py` does not reuse the builder analyzer. It rejects raw
row-count or duplicate-key drift, hashes the real source inputs in the full runner, requires matching
panel/referee/engine metadata, compares map/seat/seed/class/profile/attempt/turn identity, requires
clean execution, and independently derives the changed-game inventory.

It reproduced:

```text
matched games                 240
candidate / base blocking     115 / 35
de-novo / healed              80 / 0
changed games                 85 (all unique and named)
new P3 / P4 / r5-horizon      5 / 73 / 0
```

Its exact 85-game projection agrees with the committed decomposition. The builder analyzer also
regenerates its committed decomposition byte-for-byte at SHA-256
`1a3eb58ad25c4cda9bef6fb5f42f0db4c4efbba795400492125d59caca073e3d`.

## Fresh-eyes review and tool limits

`chatgpt_1` independently recommends **`BLOCKED`**. It correctly found that the builder analyzer is
not reusable as a qualification gate: it can silently accept a 241-row packet with a duplicate key,
checks matched fixtures only by map/seat, trusts self-reported source hashes, and omits per-game
command/event diagnosis. Those defects do not weaken this stop because the local full-panel rerun
reproduced every game row and the independent verifier closes the duplicate, identity, execution,
and source-hash gaps. They remain evidence-tool follow-up; the stopped candidate must not be patched
or rerun merely to improve its package.

## Closeout

- r2 is **BLOCKED**; no owner decision is required to reject it.
- G-e, population progress, fixture healing, score, full-corpus representativeness, qualification,
  and Arena readiness remain unmeasured and must not be inferred.
- No intervention patch, retune, gate change, reach rerun, TestSession, submission, or Arena action
  occurred.
- The panel-digest determinism and NARRATE v3 cards remain separately deferred under their existing
  unblock conditions.
- A future design requires a new owner/coordinator charter; this result opens no next experiment.
