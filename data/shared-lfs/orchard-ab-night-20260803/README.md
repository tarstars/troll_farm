# Orchard/no-orchard overnight live cycle

This namespace receives eight immutable sanitized replay packages: four one-hour deployments of
the exact no-orchard ablation and four of exact E7a with orchard, alternating `N→O` and ending
with orchard active. Each leg directory contains a manifest, compact battle index, and one full
JSONL-gzip replay payload tracked by the narrow Git LFS rule in `.gitattributes`.

Pseudonyms are replaced by positional placeholders. User IDs, avatars, public handles, and
TestSession handles are excluded. Technical game, agent, and submission IDs remain as experiment
provenance. Runtime state and final comparisons live under
`data/analysis/live-agent-6553250/orchard-ab-night-20260803/`.
