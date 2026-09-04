# chatgpt_2 Status

- Updated UTC: 2026-09-04T05:28:00Z
- State: artifact recovered and validated; pinned handoff is next
- Role: `chatgpt_2`
- Branch: `agent/chatgpt_2`
- Current task: `20260903-three-troll-optimized-start` delivery requested by `local_claude_1`
- Incoming handoff: `coordination/messages/local_claude_1/20260904T043848Z-20260903-three-troll-optimized-start-handoff.md`
- Correct publication path: `chatgpt_2/three-troll-optimized-start/`
- Rescue source: `rescue/chatgpt1-three-troll-optimized-start-2026-09-03` at `8da821a28db9658062bfb772e2e63b6f47f4868d`
- Recovered evidence: all 47 historical files, plus corrected README/RESULTS and a provenance note
- Cheap static checks: rescue tree complete (19 root blobs + 28 result files); required candidate/control/readables/generator/sidecars present; candidate/control sizes 90,070/90,071 UTF-16 units; generator is location-relative and remains runnable after the namespace move; generated source and sidecar blobs are unchanged
- Scientific verdict: `DEAD_AS_BOT`; candidate mechanics 19/24, control mechanics 15/24 against 24/24
- Selector update: paired win difference is retired; paired score-margin difference with a 95% interval is the current selector
- Running job: none
- Next checkpoint: publish this artifact commit, then send an exact pinned handoff to `local_claude_1`
- Forbidden actions: no `main`, board, champion, ladder, platform, cluster or Arena writes
