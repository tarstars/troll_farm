# Banana-farm v8 watching-submission parity

Task: `20260826-banana-farm-candidate`. Reviewed object:
`agent/claude_1@56f4b673aac3c96340102f68f06ff4e9f2c0c3d2`, submission SHA-256
`443a196e51ca8a87066ef25ff88b81800601a6c901d3fe3e684effcad453a536`.

Verdict: **ACCEPT.** With each complete `MSG` fragment removed, the compacted farm submission's
command stream is identical to the panel-tested readable instrument arm on **240/240 games**:
same `(map_id, seat)` key set and **0 differing games**.

I extracted the pinned commit into a detached temporary worktree, changed only the panel config's
candidate source and declared SHA to the compacted submission, and ran the unchanged 120-map,
two-seat panel. The ordinary panel verdict was `BLOCK` (96 blocking games); that is expected and
does not revise the farm's standing validity failure. This review checks packaging parity only for
the owner's watching run.

Evidence:

- recorded readable-arm archive SHA-256:
  `fbc867f82f5cc5074253c9ed7981f4af7848f57609a3c2416c73fcc89fa289d4`;
- fresh compacted-submission archive SHA-256:
  `f333f841e094229e7e18a32013f1610570903bfe900a7a91f51574fb88f47174`;
- `same_keyset=true`, `games=240`, `differing_games_after_msg_strip=0`;
- fresh panel completed in 21.7 seconds, with zero gate-unready games.

This is not a qualification, promotion, or value verdict. The champion of record remains the
champion; the farm validity failure remains unchanged.
