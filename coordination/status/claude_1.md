# claude_1 Status

- Updated UTC: 2026-08-08T22:00:00Z
- State: Phase 1 measurement repair; three items delivered, three queued
- Role: contributor; **execution reviewer** on every artifact (coordinator = `local_claude_1`; `chatgpt_1` = adversarial/committed-blob reviewer)
- Branch: agent/claude_1-banana-restoration-r2; canonical agent/claude_1; worktree /home/tarstars/prj/troll_farm-claude_1
- Write set: claude_1/**, my message namespace, this status file. NOT trace_detectors.py (detector semantics = local_claude_1 since 2026-08-08)

## Where the programme actually stands

- **The gate blocks its own reference: 118/240.** Perfect raw D-1/D-4 compliance moves it only to **106** (12 of 118 games block solely on D-1/D-4). Measurement repair precedes bot repair — the owner-adopted ordering, driven by my feasibility scoping.
- **Strict rule STANDS** (owner, reaffirmed 08-07): raw `D-1 == 0`, `D-4 == 0`, no exemption. Consequence accepted: the parent lineage must be repaired.
- **D-9 is `INAPPLICABLE`** — not unproven. The panel is *built* so the parent can never TRAIN: second worker injected at bias 0.5 → `can_train` false at `yamo_orchard_live.rs:836` (`n >= 2 || TOTAL_TURNS - turn <= 20`); otherwise PLUM granted at 1 vs cost 2. Do not build a fixture for its paired clauses.
- **D-6 enforces a retired predicate.** `founding_safety_oracle` (design F4 replacement) is called by **zero detectors**; `detect_d6` still uses arrival-order. Any verdict citing D-6 is unsound; its 9 floor games must not be quoted.
- **Bite-test suite pins ~a third of its behaviour.** Mutation sweep: 64 mutants, 20 caught / 44 survived. 0 of 9 pairs establish truth validity; exactly one independent truth label exists (`founding_safety_oracle`, unused).
- **D89a** (banana seed factory, +79.44 margin, CI [+40.99,+117.89]) is real and was never Arena-tested. My `NOT_REPAIRABLE` was **withdrawn** → `UNRESOLVED, leaning NOT_REPAIRABLE` after chatgpt_1 showed D92's 898 selections were nominal, not landed. Next step is U4, read-only, map-held-out.
- Lineage preservation: the D89a/ring work exists **only on `origin/agent/local_codex_1`** (author inactive). Mirroring requested.

## My Phase 1 items

- DELIVERED: item 4 detector bite-test audit (`f9b102c1`); item 6 I-30 + revision 2 (`258818cb`, schema v2, 48/48, aggregate `GATE_UNREADY`, zero PASS); D-9 calibration execution review; gate architecture revision-2 execution review (**`PARTIAL` — design commitments cannot be execution-reviewed until code lands**).
- QUEUED: **item 3** P4 liveness post-`C_T` referee-state rule (32 games); **item 8** D-4 repair (single-door bank serialisation, 6/6 on 1-door maps, 0/210 elsewhere); **item 7** exit floor self-test on two machines (with `local_claude_1`); completion of the item-5 execution review once implemented.
- I-30 open: never run against a real recorded pair, so the `unknown`/`GATE_UNREADY` firing rate is unknown — if high, the instrument is safe but unusable and the referee-side ledger returns. Identifiability rule sufficient for 3 enumerated ambiguity classes, **not proven complete**. D2–D4 deviations open, unrelied-upon.

## Standing lessons that keep recurring

- **A mechanism that cannot fail is not a check.** D-9 (clause never runs), D-6 (retired predicate), my own I-30 tie-break (reproducible, not identifiable) — three instances, one day.
- Bite-tests measure detector-vs-spec; the floor measures detector-vs-parent; **neither measures detector-vs-truth**. Independent oracles are a third requirement.
- **Re-derive, never repeat**, any figure crossing a document boundary — my `+12.453/+76.508` over-claim propagated into the CBF spec and BACKLOG before being caught.
- Read a prose figure to the end of its paragraph before citing it (the D92 "898 selections" qualification sat 9 lines below).
- State the unit: games vs episodes (74/196, 32/35, 63/68) produced three "contradictions" that were all the same measurement.

## Transport

- **`ack_for` is INERT unless `type: ack`.** I broke this three times in two days (in a `handoff`, and twice in a `correction`); proposed a lint rule to error on it. Always publish a separate `type: ack`.
- Run `python3 scripts/lint_outbox.py --me claude_1 --fetch` before every publish. `pytest` is NOT installed — use `python3 -m unittest`.
- Quarantine enforcement exists on **1 of 55 refs**; my canonical branch carries neither `quarantine.json` nor `legacy-baseline.json`, so my sweep ignores quarantine. Five sweep versions live — verify which you are running.
- Arena controller: NO. Sacred: `rust/src/bin/yamo_orchard_live.rs` (fff6669b). No CI anywhere.
