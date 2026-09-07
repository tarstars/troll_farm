# Frozen chopup diagnostic — park

Both planned unranked games completed once, without deployment failures.
Primary verified raw/replay hashes, fixed opponent agent6505289, physical seat1,
seed260906110801, identical initial input, and official ranks.

| Policy | Game | W/D/L | Points | Own/opponent score | Margin | Wood |
|---|---|---|---|---|---|---|
| policy-flat | 901727948 | 0/0/1 | 0 | 241/262 | -21 | 60/63 |
| chopup | 901727987 | 0/0/1 | 0 | 204/242 | -38 | 51/58 |

Both have empty diagnostics and two workers per side. Candidate first hire moves
from turn8 to18. Candidate fruit1->0 and wood60->51. The frozen rule required a
clean strictly better paired outcome before proposing fresh evaluation; it failed.
Park this implementation. No repeat, confirmation sample, or ranked publication.
This is one previously inspected map, not independent strength validation.

Exact-source certification was completed before either request. Primary compile
evidence: primary-cert-h_ltq_o4/certification.json, actual Rust1.90.0, three matched
pairs, median6.736s vs V4396.382s (ratio1.0555 <=1.10), zero candidate diagnostics.
The earlier Claude Rust1.97 timings are not accepted. Primary's first timing
invocation stopped because a dotted source filename needed --crate-name; preserved
under primary-cert-wahju2ed/. The invocation fix did not change bot source.
Focused oracle checks passed independently (changed reference accepted, differing
compact and legacy default rejected); startup320 passed with max1.570ms. Existing
exact160-stream/43263-turn certification was verified, not repeated.

Production bot.rs/submission.rs and submission41245746/agent6704418 were unchanged.
