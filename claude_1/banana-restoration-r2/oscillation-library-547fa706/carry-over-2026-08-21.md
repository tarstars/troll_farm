# Mechanism carry-over — the champion's exhibits vs the owner's rulings

Subject `547fa706cc1c`. Champion library `4d3b36558f31…` (21 cases); old subject library `1370384da9ca…` (34 cases).

**"No exhibit" is not "fixed".** A mechanism with no case here has NO EXHIBIT on the champion. It is NOT a claim that the champion has stopped doing it: the champion's floor is 240 games and a shape can be absent because it did not occur in those games. The owner's rulings on the old cases are rulings about MECHANISMS and stand unchanged.

## The ruled mechanisms

| mechanism | rule | old exhibits | champion exhibits | status |
|---|---|---|---|---|
| corridor pass -> swap | R-1 (owner-approved 2026-08-16) | OSC-001 | OSC-001, OSC-002, OSC-003, OSC-004, OSC-005, OSC-006, OSC-007, OSC-008 | exhibit present |
| open-map pass -> teammate-aware routing | cure beta, designed, not built | OSC-010 | OSC-001, OSC-002, OSC-003, OSC-004, OSC-005, OSC-006, OSC-007, OSC-008 | exhibit present |
| same tree wanted -> reservation | cure beta, designed, not built | OSC-030 | — | NO EXHIBIT -- not a claim that it is fixed |
| single-troll goal flip | cure gamma, designed, not built; OSC-026 stamp candidate at 4b | OSC-026 | OSC-018 | exhibit present |
| idle troll parked on a plant | cure alpha target shape (amended G-2, 20260821T105914Z) | OSC-012, OSC-013, OSC-017 | OSC-009, OSC-010, OSC-011, OSC-012, OSC-013, OSC-014, OSC-015, OSC-016, OSC-017 | exhibit present |
| benching: a troll with available work is not employed | R-2 (owner-approved 2026-08-20), class-wide | OSC-017, OSC-013, OSC-034, OSC-004 | OSC-001, OSC-002, OSC-005, OSC-006, OSC-007, OSC-008, OSC-010, OSC-011, OSC-012, OSC-013, OSC-014, OSC-015, OSC-016, OSC-017, OSC-021 | exhibit present |

**Two rows above share one label and therefore one case list.** `corridor pass -> swap` and `open-map pass -> teammate-aware routing` are both M1 in this vocabulary. The classifier records that a stationary peer held the route; it does not record whether the route was a dead-end corridor (where a swap is the only resolution) or open ground (where routing around exists). Splitting them needs the resolver's goal, which the library marks UNRESOLVED. The `free neighbours` column below is a declared geometric PROXY offered for sorting the viewer pages, and it rules nothing.

Join basis, per row: **corridor pass -> swap** — classifier label M1; **open-map pass -> teammate-aware routing** — classifier label M1; **same tree wanted -> reservation** — NOT SEPARABLE by this library's vocabulary: the discriminator is the resolver's goal, which every situation records as UNRESOLVED; **single-troll goal flip** — classifier label M3; **idle troll parked on a plant** — classifier label M2; **benching: a troll with available work is not employed** — cases with at least one benched unit-turn under the eligible-action oracle

## Every champion case

| case | label | blocker | kind | turns | unit | game | free neighbours (proxy) | benched unit-turns | old case on the same game |
|---|---|---|---|---|---|---|---:|---:|---|
| OSC-001 | M1 | IDLE | D1_EPISODE | 6–200 | 0 | m110 s1 | 2.0 | 39 | OSC-001 (M1, same window) |
| OSC-002 | M1 | IDLE | D1_EPISODE | 12–200 | 2 | m059 s1 | 2.5 | 189 | OSC-002 (M1, same window) |
| OSC-003 | M1 | IDLE | D1_EPISODE | 17–200 | 2 | m082 s1 | 3.5 | 0 | — (new game) |
| OSC-004 | M1 | IDLE | D1_EPISODE | 50–200 | 2 | m063 s1 | 2.5 | 0 | — (new game) |
| OSC-005 | M1 | IDLE | D1_EPISODE | 176–200 | 0 | m040 s0 | 3.0 | 25 | — (new game) |
| OSC-006 | M1 | WORKING | D1_EPISODE | 29–42 | 0 | m058 s1 | 3.0 | 14 | OSC-029 (UNCLASSIFIED) |
| OSC-007 | M1 | WORKING | D1_EPISODE | 7–18 | 2 | m070 s1 | 2.0 | 1 | OSC-005 (M1, same window) |
| OSC-008 | M1 | WORKING | D1_EPISODE | 26–32 | 0 | m028 s1 | 3.0 | 7 | OSC-011 (M1, same window) |
| OSC-009 | M2 | IDLE | D1_EPISODE | 8–200 | 0 | m099 s1 | 2.0 | 0 | OSC-012 (M2, same window) |
| OSC-010 | M2 | IDLE | D1_EPISODE | 7–200 | 2 | m014 s1 | 3.5 | 194 | OSC-017 (M2, same window) |
| OSC-011 | M2 | IDLE | D1_EPISODE | 14–200 | 2 | m046 s0 | 2.0 | 187 | OSC-013 (M2, same window) |
| OSC-012 | M2 | IDLE | D1_EPISODE | 32–200 | 0 | m084 s1 | 3.5 | 169 | OSC-021 (M2, same window) |
| OSC-013 | M2 | IDLE | D1_EPISODE | 38–200 | 2 | m079 s0 | 4.0 | 163 | — (new game) |
| OSC-014 | M2 | IDLE | D1_EPISODE | 52–200 | 0 | m070 s1 | 2.5 | 149 | OSC-005 (M1) |
| OSC-015 | M2 | IDLE | D1_EPISODE | 52–200 | 0 | m004 s0 | 4.0 | 149 | OSC-030 (UNCLASSIFIED) |
| OSC-016 | M2 | IDLE | D1_EPISODE | 5–69 | 0 | m073 s0 | 2.5 | 64 | OSC-024 (M2, same window) |
| OSC-017 | M2 | IDLE | D1_EPISODE | 12–32 | 0 | m012 s1 | 3.5 | 21 | OSC-025 (M2, same window) |
| OSC-018 | M3 | NONE | D1_EPISODE | 17–25 | 0 | m085 s0 | 3.5 | 0 | OSC-026 (M3, same window) |
| OSC-019 | UNCLASSIFIED | NONE | D1_EPISODE | 3–24 | 2 | m066 s0 | 2.0 | 0 | OSC-027 (UNCLASSIFIED, same window) |
| OSC-020 | UNCLASSIFIED | NONE | D1_EPISODE | 24–31 | 2 | m004 s0 | 3.5 | 0 | OSC-030 (UNCLASSIFIED, same window) |
| OSC-021 | UNCLASSIFIED | NONE | P4_STALL | 11–200 | 0 | m059 s0 | 2.5 | 380 | OSC-031 (UNCLASSIFIED, same window) |

## Old cases whose GAME has no champion case (17)

OSC-003, OSC-004, OSC-006, OSC-007, OSC-008, OSC-010, OSC-014, OSC-015, OSC-016, OSC-018, OSC-019, OSC-020, OSC-023, OSC-028, OSC-032, OSC-033, OSC-034

A game is matched on `(map_id, seat)`, which is the same panel skeleton in both libraries. An old case with no champion case on its game means the champion's own floor recorded no oscillation or stall episode there — again, a statement about what was recorded, not a verdict about the bot.
