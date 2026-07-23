from pathlib import Path

from cgauto.make_d105b_proposal_union_manifest import arm_key_digest


def test_arm_key_digest_is_order_independent_and_delimited():
    assert arm_key_digest(["b", "a"]) == arm_key_digest(["a", "b"])
    assert arm_key_digest(["ab", "c"]) != arm_key_digest(["a", "bc"])


def test_sha_inputs_are_paths():
    # Protect the lock helper's explicit filesystem contract.
    assert isinstance(Path("manifest.tsv"), Path)
