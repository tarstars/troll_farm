# How complex is this bot, and how high does it stand?

Prepared 2026-08-04 for the owner's question. Everything here is from measurements already
in the repository; the pending round-36 submission adds one confirming point.

## Complexity

| Measure | Value |
|---|---:|
| Submitted source (exact E7a, live) | 62,820 bytes |
| Simplified equivalent (round 36, behaviour-identical) | **55,799 bytes** |
| Platform allowance | 100,000 characters |
| Fraction of allowance used | **55.8 %** |
| Readable form | 2,552 lines of Rust |
| Functions | ~180 |
| Modules | 5 (`types`, `rules`, `nav`, `protocol`, `moisan`) |

Of the 55,799 bytes, two features are measured individually:

| Feature | Bytes | Share | What it buys |
|---|---:|---:|---|
| Secure apple orchard | 15,013 | 23.9 % | **+2.03 rating** (measured by live ablation) |
| Door unblocking | 5,991 | 9.5 % | no measurable effect yet — changed 0 of 7,234 commands |

So roughly a quarter of the program earns two rating points, and roughly a tenth has never
been observed changing a decision.

## Standing

| Agent / source | Score | Rank |
|---|---:|---|
| delineate (ladder leader) | 31.02 | 1 |
| norxondor_gorgonax | 29.67 | 2 |
| MSz | 28.26 | 3 |
| Escdemon (top-10 boundary, our target) | 25.37 | ~10 |
| **Exact E7a, first mature cycle** | **25.30** | **12 / 131** |
| **Exact E7a, restore cycle (same source!)** | **23.56** | **32 / 137** |
| No-orchard ablation | 23.27 | 34 / 137 |

## The finding that most affects your question

**The identical source scored 25.30 at rank 12 and later 23.56 at rank 32.** Same bytes, same
SHA, two maturity cycles. That is a swing of 1.74 points and 20 ranks from ladder variance and
pool composition alone — larger than the entire measured value of the orchard.

Two consequences worth holding onto:

1. "How high is it" is only meaningful as a distribution, not a number. On current evidence
   this design lives somewhere around **rank 12–34 of ~135**, i.e. comfortably in the upper
   quartile of Legend but well outside the top ten.
2. Any single submission — including the round-36 one — is one draw from that distribution.
   It answers "does the simplified source behave like the original" cleanly, but it cannot by
   itself pin the design's true standing. The project's completion rule already encodes this:
   a mature read **plus a later confirmation**, never a single spike.

## What the round-36 submission adds

- A third data point for the same behaviour at 6,479 fewer bytes.
- A falsification test: if it matures materially away from the exact E7a band, the
  behaviour-exactness claim — currently supported by 516 paired development tasks and 7,234
  live command lines — is wrong and we would want to know.
- 10.4 % of the submission allowance freed as headroom.

## Context for "is 55.8 % of the allowance a lot?"

The ledger records that **25 Legend agents reach ranks 7–54 using our exact two-worker
roster**, so the architecture is demonstrably capable of better standing than we hold. The
2026-07-29 synthesis closed eight tested improvement routes for this architecture; the
measured gap is scale-asymmetry survival in long games, not code volume. Complexity is not
the binding constraint — this bot is not losing because it is too small.
