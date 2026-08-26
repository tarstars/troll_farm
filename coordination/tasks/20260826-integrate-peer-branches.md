# 20260826-integrate-peer-branches: Track 0-2 — bring the peer branches onto `main`, once, deliberately

- Status: **OPEN — CHARTERED 2026-08-26T13:40Z by owner ruling ("do it")**, board row 0-2.
- Record owner and work owner: **local_claude_1** (the integrator). Reviewer: codex_1 (one
  round: quarantine and shared files verified by execution). Arena: nothing.
- **Done means:** `agent/claude_1` and `agent/codex_1` (and `agent/chatgpt_1`) are merged into
  `main` with **`main` winning on every shared file** (`coordination/multi-agent-protocol.md`,
  `roster.json`, `quarantine.json`, `readable/*`, `scripts/*`, `tests/*`, `docs/*`); the peers'
  own directories (`claude_1/`, `codex_1/`, `chatgpt_1/`) and message trees come in verbatim;
  the quarantine re-verified by hand afterwards (`inbox_sweep` shows 0 quarantine errors, the
  12 entries still adjudicated by an authorised id); the champion readable still 2,210 lines,
  sha `ad1ae4ef…`; every peer told (ack-required) to rebase onto the result; ahead-of-`main`
  counts for all three branches = 0 at the moment of the merge.
- **Dead means:** never — but if the merge cannot be made to pass the checks above in one
  session it is aborted (`git merge --abort`), nothing is pushed, and the obstacle is written up.
- **Budget:** one session, one review round, 0 ladder. Sequenced **after Candidate 3's build
  lands** (D-1 at Panel), so no merge happens under a moving build.
- Created UTC: 2026-08-26T13:40:00Z · Last updated UTC: 2026-08-26T13:40:00Z

## Why (plain words)

`claude_1` is 287 commits ahead of `main`, `codex_1` 262 (2026-08-26 13:20Z). The transport
reads their messages straight from their branches, so nothing *breaks* — which is why nobody
noticed that the peers' whole artifact trees are not on the integrated branch. Rules §7
("everything lands on `main` at every gate") stops it growing back; this task clears the
backlog. A blind merge is not acceptable: the quarantine has silently broken on every merge so
far, and a peer's stale copy of `readable/door1-champion.rs` (2,206 lines) would overwrite the
corrected one.

## Method

1. Fresh branch from `main`; `git merge --no-ff --no-commit origin/agent/<peer>`; for every
   conflicted or shared file, `git checkout --ours`; verify the list of paths taken from the
   peer is a subset of `<peer>/`, `coordination/messages/<peer>/`, `coordination/status/<peer>.md`.
2. Run `python3 scripts/inbox_sweep.py --me local_claude_1` and the test suite; check the
   champion readable hash; check `quarantine.json` unchanged from `main`.
3. Commit, push to `agent/local_claude_1`, fast-forward `main`; ack-required notice to the
   peers: rebase onto `main`, do not merge.

## Done on 2026-08-26 as the first step (owner "do it")

Branch hygiene: `agent/chatgpt_2` (0 ahead) and `session-2026-07-01` (0 ahead) deleted;
`archive/local_codex_1-stranded-20260810` converted to the tag of the same name (commit
`2bfc462a` preserved) and the branch deleted; the stale worktree `/tmp/troll_farm-local_codex_1`
removed; `agent/local_codex_1`'s one unmerged commit (the 08-24 role-transfer handoff and
policy, two immutable messages) cherry-picked onto `main` with `main` winning on the task card,
then the branch deleted.
