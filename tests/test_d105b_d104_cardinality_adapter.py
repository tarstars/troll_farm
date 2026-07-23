import csv

from cgauto.d105b_d104_cardinality_adapter import (
    pad_manifest,
    strip_proposals,
)


def write_table(path, fields, rows):
    with path.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_pad_and_strip_are_behavior_neutral_for_source_roots(tmp_path):
    fields = ["root_id", "arm_id", "value"]
    manifest = tmp_path / "manifest.tsv"
    rows = [
        {"root_id": str(root), "arm_id": f"r{root:04}__control", "value": str(root)}
        for root in range(233)
    ]
    write_table(manifest, fields, rows)
    padded = tmp_path / "padded.tsv"
    metadata = tmp_path / "metadata.json"
    report = pad_manifest(manifest, padded, metadata)
    assert report["source_roots"] == 233
    assert report["target_roots"] == 240
    assert len(report["clone_mapping"]) == 7

    proposal_fields = ["root_id", "expert_index", "arm_id"]
    raw = tmp_path / "raw.tsv"
    proposal_rows = [
        {
            "root_id": str(root),
            "expert_index": str(expert),
            "arm_id": f"r{root:04}__e{expert:02}",
        }
        for root in range(240)
        for expert in range(64)
    ]
    write_table(raw, proposal_fields, proposal_rows)
    stripped = tmp_path / "stripped.tsv"
    strip_report = strip_proposals(manifest, raw, stripped)
    assert strip_report["retained_rows"] == 233 * 64
    with stripped.open(newline="") as source:
        retained = list(csv.DictReader(source, delimiter="\t"))
    assert {int(row["root_id"]) for row in retained} == set(range(233))
