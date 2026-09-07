# V545 first-output hardening result

## Design

V545 isolated the repaired R1FA economy used by V543 and removed the complete V468 controller,
adaptive latch, and stall-rescue shadow controller. It retained V543's constant-time own-half
predicate and behavior-neutral dead-state removal. This directly tested whether reducing source and
executable size enough to remove the dual-controller surface was worth V543's known compatibility
benefit.

## Packaging and timing

Both readable and compact programs compiled with Rust 2021 optimization and accepted the sample
protocol input. The compact source was 70,981 bytes / UTF-16 units, SHA-256
`42f3774d0239202deb65c499f663c39c510bd5cf7cd2e4f9a0f8e123ddb8eb1f` (28,844 units smaller than
V543). The optimized executable's text/data footprint fell from 796,669 to 546,805 bytes, 31.4%.
On the 192-game panel, candidate planning latency was 0.94 ms at p95 and 2.00 ms maximum.

## Development gate

The standard eight-map, both-seat, 12-family panel used seeds 9,941,000 through 9,941,007:

| turn | V468 own | V545 own | delta |
|---|---:|---:|---:|
| 100 | 93.0 | 16.0 | -77.0 |
| 200 | 176.2 | 141.1 | -35.1 |
| 300 | 247.2 | 363.5 | +116.3 |

V545 raised final mean margin by 59.94 and wood from 45.0 to 78.6, but W/T/L worsened from
177/3/12 to 165/0/27. Its mean resident-family margin fell by 49.4. Critical and unclassified
command issues remained zero. The source reduction therefore removes precisely the opening and
opponent-compatibility behavior needed for match wins; the candidate fails the checkpoint gate.

The panel SHA-256 is `86046e3515169e3253518debe2602f48711f8827e455d15bbd9058ab77aeda53`.
The gate-report SHA-256 is `dbd92dab42cafaa20a15fce98af7db41dc83a0829d0172c82e925ba153d8512f`.
V545 was not published and V543 remains canonical.
