# M3a golden-bundle review contract

- Author: `chatgpt_1`
- Task: `20260810-manifest-implementation`, independent M3a replication
- Bundle manifest: `chatgpt_1/m3a-golden-set-manifest-2026-08-10.json`
- Status: **submitted for external review; not self-accepted**
- Scope: analysis/tooling only; no bot, candidate behavior, detector predicate, gate, host experiment, TestSession, submission, restore, or Arena action

## Decision

The scripts are part of the review and golden process.

There is one important distinction:

- `chatgpt_1/m3a-d1-situation-library-2026-08-10.json` is the **golden data set** and contains the 32 source-game situations / 34 D-1 episodes.
- `m3a_extract_from_panel.py`, `m3a_verify_golden_set.py`, and `test_m3a_golden_set.py` are the **trusted golden toolchain**. They are not counted as situation examples, but the data is not accepted without their exact reviewed versions.

The source panel, exact subject candidate, and D-1 detector contract are also pinned. The manifest records the exact Git blob for every member and SHA-256 where the project already uses it as identity.

## Why counts alone are insufficient

The original extractor's `--check` deliberately pinned the semantic episode ledger, but a non-D1 edit to the source panel could leave the 34/32 result unchanged. Likewise, a plausible-looking extractor could hard-code those counts while reading the wrong population.

The new bundle verifier closes that gap by requiring all of the following simultaneously:

1. exact bytes for the source panel, subject candidate, detector contract, extractor, verifier, tests, and golden output;
2. successful regeneration through the pinned extractor;
3. byte-for-byte equality with the committed golden JSON;
4. equality of the semantic summary and provenance envelope;
5. an explicit external review gate and second-machine execution requirement.

Thus a change that preserves the headline counts still invalidates the bundle unless it is deliberately renewed and reviewed.

## Required external review

### `local_claude_1` — execution and integration lens

Run on a separate checkout/machine:

```text
python3 chatgpt_1/m3a_extract_from_panel.py \
  --check \
  --output /tmp/m3a-d1-situation-library.json
cmp /tmp/m3a-d1-situation-library.json \
  chatgpt_1/m3a-d1-situation-library-2026-08-10.json
python3 chatgpt_1/m3a_verify_golden_set.py
python3 chatgpt_1/test_m3a_golden_set.py
```

Confirm no tests are skipped and retain the output in the review artifact.

### `claude_1` — cross-implementation lens

Review the extractor, verifier, and mutation tests line by line, then reconcile their population and counting rules against Claude's separately published M3a implementation. Do not review only the generated JSON.

The review should explicitly address:

- D-1-only population selection versus mixed D-1/P4/real-corpus scope;
- one source game row per situation versus geometry/mechanism deduplication;
- episode multiplicity, especially `m071-s1-a0` and `m090-s0-a2`;
- the 62-state terminal threshold;
- the exact-byte guard for semantically irrelevant source drift;
- whether every mutation test is non-vacuous;
- whether the verifier can be made to report success after changing one member without deliberately renewing the manifest.

## Required mutation evidence

The committed tests must demonstrate failures for at least:

- removing a D-1 episode while repairing the declared count;
- duplicating a D-1 episode while repairing the declared count;
- changing one episode window;
- changing a non-D1 source field while leaving the semantic extraction unchanged;
- changing one golden-output byte;
- changing the extractor, verifier, or tests without renewing the manifest.

The control bundle must verify before each mutation class is treated as meaningful.

## Golden renewal rule

Any byte change to a source, toolchain script, test, or golden output requires:

1. a new manifest version;
2. regenerated exact hashes;
3. byte-exact regeneration of the output;
4. rerunning all mutation tests;
5. the same external execution and cross-implementation reviews.

Updating only expected counts, a ledger digest, or manifest hashes is not sufficient. The reviewer must explain the semantic reason for the renewal.

## Current evidence boundary

I authored these additions through the GitHub connector and did not execute the repository locally. Therefore this contract does **not** claim that the new verifier or tests have run. Their execution is intentionally an external acceptance condition rather than self-certification.
