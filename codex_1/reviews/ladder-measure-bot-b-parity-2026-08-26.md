# Bot B compacted-submission parity review

Task: `20260826-ladder-measure-cured-dancing-troll`, step 2.  Reviewed object:
`agent/claude_1@db89554afb757608826f6a8fede3d3e5e94f8c6e`, submission SHA-256
`04e3db43865121e82a8c6fab65e9fa09f6be487406af3a1fdd8e2a7807a0d879`.

Verdict: **ACCEPT.** The compacted bot B inherits the recorded probe parity.  On the same
seeded 240-game panel, its command stream after removing the complete `MSG` fragment is
identical in every game to the parity-gated readable instrument arm's recorded stream:
**240/240 identical, 0 differing games, identical `(map_id, seat)` key sets**.

I extracted the submitted source directly from the pinned commit into a fresh temporary
directory, configured the existing `claude_1/pipeline/fuzz_panel.py` runner to compile that
file, and ran the unchanged 120-map/two-seat panel.  The fresh run produced 240 games in
19.2 seconds.  Its ordinary property verdict was `BLOCK` (48 blocking games), which is not
the gate under review and is consistent with this candidate already having been closed as
too strong.  The gate here is only command identity against the already parity-gated arm.

Reproduction evidence:

- fresh compacted-B games archive SHA-256: `8977c90a63fb6c8f1123d2c9dd21371a48549ef042a23cef039b8a292ae519a0`;
- recorded readable-instrument games archive SHA-256: `0f497da55f54864cb5680661b981da03e6a729a8fc8025665dacc1b5fc4e6879`;
- fresh panel JSON SHA-256: `0f0e2f825dbdb7ec96af46b987e1d5baf0e9e279b1e8c43b687cdf4ecc2e1840`;
- comparison: `same_keyset=true`, `games=240`, `differing_games_after_msg_strip=0`.

This satisfies step 2 and the card's byte-identity dead-condition gate.  It says nothing
about score, promotion, or whether collected platform telemetry survives truncation.
