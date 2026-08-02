# D172a option corpus — selective Git LFS mirror

This directory mirrors four immutable D172a option-policy corpus shards from the
label-verified `medium_data` filesystem so repository-only agents can use the exact inputs.
The external copy beneath `artifacts/` remains authoritative; this mirror is distribution,
not backup or permission to remove the source.

The four TSV files are the only LFS-tracked paths in this directory. Metadata remains in
ordinary Git. Clone with automatic LFS smudge disabled, then download only this dataset:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone git@github.com:tarstars/troll_farm.git
git -C troll_farm lfs pull --include="data/shared-lfs/d172a-option-corpus/*.tsv"
(cd troll_farm/data/shared-lfs/d172a-option-corpus && sha256sum -c SHA256SUMS)
```

Acceptance is four regular TSV files, 82,824,259 apparent bytes, 79,997 data rows (80,001
physical lines including one header per shard), and every checksum in `SHA256SUMS` exact.
See `manifest.json` for provenance and per-file counts.
