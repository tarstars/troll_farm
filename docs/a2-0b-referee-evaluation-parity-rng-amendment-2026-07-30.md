# A2-0b amendment A1 — movement RNG advances on bound one

Status: **FROZEN before implementation and before any panel execution**  
Date: 2026-07-30  
Trigger: direct line-by-line check of `Board.getNextCell`

## Correction

The initial A2-0b protocol said a unique-best non-direct move consumes no RNG draw. That
is false. The referee constructs `closest` and unconditionally returns:

```java
return closest.get(random.nextInt(closest.size()));
```

Therefore:

- a target already reachable within movement speed returns before that line and consumes
  no movement RNG;
- every other path selection consumes exactly one bounded RNG draw;
- `nextInt(1)` still advances SUN SHA1PRNG state even though it can only return index 0;
- when `closest.size() > 1`, the same mandatory draw also chooses the destination.

This means exact RNG continuity must model all non-direct MOVE commands, not only visible
tie outcomes. Missing a bound-one draw can silently change a later tie.

## Frozen replacement gate

Replace "tie draws once; unique best draws zero" with:

1. direct reachable target → zero movement draws;
2. every non-direct path selection → exactly one `nextInt(closest_count)`;
3. candidates are ordered exactly as the Java loops order them: x ascending, then y
   ascending;
4. panel reports total non-direct draws and the subset with `closest_count > 1`.

No code or panel output existed when this correction was made. All other protocol
questions, task matrix, reproduction targets, gates, and prohibitions remain unchanged.

