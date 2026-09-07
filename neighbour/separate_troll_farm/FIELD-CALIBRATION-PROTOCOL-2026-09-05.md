# Archived-policy field calibration pilot

This is a measurement experiment, not a new bot or a publication decision. It supersedes the
old queue for this step, following the owner's request to rethink the research. The live source
and the neighboring repository remain unchanged.

## Frozen design

- Compare exact compact V468, live V543, and dense V564. V468 and V543 have mature ladder
  observations; V564 tests an economically promising policy rejected by the early-score gate.
- Use the official unranked `TestSession/play` endpoint with adaptive, fixed ranked agents.
  This does not submit a ladder replacement. Read the existing session credentials in place;
  never write to the neighboring repository or print credentials.
- Maximum ten requests, sequentially, with no automatic retry. First repeat V468 against
  rank-seven putibuzu on one new seed (A/A); require identical normalized initial inputs,
  both command streams, scores, ranks, inventories, workforce and turns before continuing.
- Then complete three same-map/opponent blocks, one each against putibuzu (6479779),
  delineate (6479768), and PonyPonyCodeCode (6541377). These were rank 7, 1 and 60 in the
  fresh September 5 board. Use seeds 2609050701, 2609050102 and 2609056003, respectively.
  All games use player zero; no inference about both seats is permitted from this pilot.
- Block order: V468/A-A/V543/V564; V543/V564/V468; V564/V468/V543. The A/A repeat is
  excluded from performance totals. Seeds are chosen before results and have not been used
  to tune these policies. Different opponents on different seeds remain confounded in this
  small screen; it is not an opponent-specific strength estimate.
- Archive source hashes, the full response, requested and echoed seed, actual agent identity,
  normalized initial input, both command streams, final outcomes, inventories, runtime errors,
  and successful training events. Stop on transport errors, wrong identity/map, runtime errors,
  or failed A/A. Preserve completed evidence; do not retry a potentially executed request.
- Report wins/draws/losses, match points (win=1, draw=0.5), own score and margin, individually
  by block. Three blocks cannot validate an estimator, establish superiority, justify a rank
  prediction, or authorize an automatic publication. A useful result chooses the next expanded
  test and exposes local/field disagreements, without fitting a new threshold to this sample.

## Next decision

If the capability passes, keep these maps as development/calibration data. Expand promising
comparisons across fresh seeds, both seats once validated, and independent opponent families.
The historical eight-map panel remains a regression instrument; early score curves are diagnostic,
not a required investment payback schedule. Rank seven must ultimately be observed for the exact
live agent after completed rollout and later confirmation, not inferred from local score gains.

## Transport amendment after the first request

The first play call completed game 901533781 but omitted the `agents` field. The collector stopped
before a second game. A read of its authenticated stored replay (owning user ID 1302251 required)
verified the exact opponent, seed, game ID, scores and ranks. The replay endpoint with a null owner
returned HTTP 422; the owner-scoped read succeeded. This is an interface correction, not a changed
experimental block or acceptance rule. For subsequent games, fetch and archive the same-game replay
when play omits identity; reject any result mismatch. Reuse the already completed first response in
a new manifest, preserving the stopped manifest. At most nine additional play requests remain;
do not replay the first game or retry an ambiguous request. No candidate result has yet been seen.
