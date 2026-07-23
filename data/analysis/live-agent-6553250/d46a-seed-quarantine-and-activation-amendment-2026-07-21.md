# D46a seed quarantine and activation audit — frozen amendment (2026-07-21)

After the D46 protocol was frozen, the runner's focused mechanical tests instantiated seeds
9,778,000 and 9,778,001 while checking exact-prior and role-override invariants. The test did not
save or aggregate outcomes, but it traversed complete local games and reported that its selected
seed/opponent slice contained no override. That observation makes the original development block
ineligible for prospective value evidence.

Quarantine all original development seeds **9,778,000--9,778,031**. They may now be used once for
an activation/integrity audit only; their scores and margins must be ignored for policy selection.
Run the unchanged D46 candidate over all 512 tasks and require:

1. zero integrity failures and exact deterministic repeat;
2. at least 512 role-eligible decisions and 256 overrides; and
3. action-hash changes in at least 20% and at most 90% of tasks.

If any activation condition fails, close D46 without opening fresh value maps. Do not change the
designated-worker rule after seeing the audit.

If activation passes, replace prospective development with untouched seeds
**9,780,000--9,780,031** and confirmation with **9,781,000--9,781,031**. All original D46 value,
breadth, workforce, crop, tail, and confirmation gates remain unchanged. Original confirmation
seeds 9,779,000--9,779,031 remain sealed and unused.
