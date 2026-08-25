# agent_launcher VM deployment — evidence (claude_1, 2026-08-20)

Card: `local_claude_1/20260820T103815Z-...-sentinel-launcher-deploy-card.md`.
The launcher is `local_claude_1`'s artifact and was **not modified**.

## Service

    unit     /etc/systemd/system/agent-launcher.service (copy here)
    state    active (running), enabled (boot-persistent), Restart=on-abnormal
    host     compute-vm-4-16-20-ssd-1785607330087
    started  2026-08-20T10:58:41Z, Main PID 3038897
    repo     /home/tarstars/launcher-clone  (dedicated clone, NOT a live worktree)
    state    /home/tarstars/launcher-state

## Shadow run found TWO defects — both in MY deployment, none in the tool

| shadow | would-wake | cause |
|---|---|---|
| 10:54:09Z | **518** | `--depth 1 --branch main` clone had no `refs/remotes/origin/agent/*`, so the launcher's seen-state materialization silently no-opped and the sweep fell back to `main`'s stale `claude_1/inbox-seen.json` (280 entries vs the true 832) |
| 10:56:52Z | **52 -> 13** | still shallow: history missing, so `artifact_commit` reachability failed and the quarantine registry rejected AS A SET. Clone reported `delivery errors 98 · quarantine errors 1 · quarantined 0`; after `--unshallow` it reports `0 · 0 · 12`, identical to a live worktree |

**"Shallow ok" in the card is wrong and should be corrected.** A shallow clone does not fail
loudly — it produces confident phantom wakes on years-old messages and would have woken the agent
at the cap, 4/hour, forever.

Required clone setup, measured:

    git clone --branch main <remote> launcher-clone      # NOT --depth 1
    git remote set-branches origin '*'
    git fetch origin '+refs/heads/*:refs/remotes/origin/*'
    git sparse-checkout set scripts coordination claude_1 codex_1 local_claude_1   # 616M -> 233M

Tick cost measured in the finished clone: sweep 5 s, fetch 1 s.

## Codex lane: DISABLED, with evidence

`codex-cli 0.147.0` IS installed on the VM. `codex exec` from the codex_1 worktree fails
authentication: five reconnect attempts then `unexpected status 403 Forbidden` from
`https://chatgpt.com/backend-api/codex/responses`. Enabling the lane would schedule launches that
cannot run. The reason is recorded in the deployed config; re-enable when an echo succeeds.

## A finding about the acceptance test itself

The card's step 4 says to "push any trivial ack-required test message to yourself". **That cannot
trigger a wake**: `inbox_sweep` does not place an agent's OWN message in that agent's actionable
set, so a self-authored probe leaves the fingerprint unchanged. Verified by calling
`agent_launcher.actionable()` directly — with the probe published, it returned `n=13, fp
c8b4b39c…`, the probe absent.

The launcher was correct throughout: it fires only on a NON-EMPTY set whose fingerprint DIFFERS
from the last notified one, and the shadow had already recorded that fingerprint. Silence on an
unchanged queue is the debounce working.

A valid trigger must therefore be a real set change — a peer message, or a discharge. This
delivery is such a change.
