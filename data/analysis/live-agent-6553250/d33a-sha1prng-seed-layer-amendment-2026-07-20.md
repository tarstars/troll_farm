# D33a authoritative SHA1PRNG seed-layer amendment (2026-07-20)

## Trigger

The first Rust port used `java.util.Random(seed)` exactly as the board's declared field type
suggested.  It passed compilation and structural invariants but matched none of the three permitted
development witnesses.  Dimensions already differed in two cases, before any held-out confirmation
text was opened.

Inspection of the released primary dependency resolves the discrepancy.  Troll Farm pins
`com.codingame.gameengine:core:4.7.8`; that artifact's `MultiplayerGameManager` creates
`SecureRandom.getInstance("SHA1PRNG")`, calls `setSeed(long)`, and returns it through a method typed
as `Random`.  The board therefore consumes SUN SHA1PRNG output, not the 48-bit `java.util.Random`
linear congruential stream.

Primary sources frozen for this amendment:

- Maven Central `core-4.7.8-sources.jar`, SHA-256
  `bf9e8b8a253626f5fa307bdedb5c732e96251a7aa8ec554416debfa27d63e7ab`;
- OpenJDK 17 `java.security.SecureRandom`: signed-long seed bytes are least-significant byte first,
  and inherited `Random` methods obtain bits through `next(int)`;
- OpenJDK 17 `sun.security.provider.SecureRandom`: SHA-1 state initialization, 20-byte remainder
  consumption, and the provider's signed-byte state update.

## Frozen correction

Replace only the D33 RNG layer with a behavioral SUN SHA1PRNG port:

1. encode each nonzero signed seed as eight little-endian two's-complement bytes;
2. initialize the 20-byte state with SHA-1 of those bytes;
3. reproduce `engineNextBytes`, including remainder zeroing and signed-byte `updateState` carry;
4. reproduce `SecureRandom.next(31)` and inherited bounded `nextInt` rejection semantics; and
5. leave board call order, terrain/tree rules, manifest, development witnesses, and every frozen
   parity gate unchanged.

Seed zero is outside the deterministic contract because OpenJDK intentionally ignores
`setSeed(0)` and self-seeds on first use.  The frozen manifest must contain no zero seed.

No confirmation turn-one text has been read or compared.  The implementation hash remains
unfrozen, so this is a development-layer correction, not a confirmation retry.  If the corrected
port fails any development witness, D33 stops before confirmation and uses recorded-map fixtures.

