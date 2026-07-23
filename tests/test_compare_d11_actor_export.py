from pathlib import Path

import numpy as np
import torch

from cgauto.compare_d11_actor_export import compare_trace, decode_corpus, encode_corpus
from cgauto.train_level1_ppo import SpatialActorCritic


def test_corpus_codec_is_deterministic_and_lossless() -> None:
    rng = np.random.default_rng(31)
    observations = rng.integers(0, 256, (3, 104, 11, 22), dtype=np.uint8)
    masks = rng.integers(0, 2, (3, 13, 11, 22), dtype=np.uint8)
    encoded_a, raw_sha_a = encode_corpus(observations, masks)
    encoded_b, raw_sha_b = encode_corpus(observations.copy(), masks.copy())
    decoded_observations, decoded_masks, decoded_sha = decode_corpus(encoded_a)

    assert encoded_a == encoded_b
    assert raw_sha_a == raw_sha_b == decoded_sha
    assert np.array_equal(decoded_observations, observations)
    assert np.array_equal(decoded_masks, masks)


def test_identical_models_have_exact_trace_agreement(tmp_path: Path) -> None:
    torch.manual_seed(37)
    checkpoint = tmp_path / "model.pt"
    torch.save({"model": SpatialActorCritic().state_dict()}, checkpoint)
    corpus = tmp_path / "corpus.zlib"
    output = tmp_path / "result.json"

    result = compare_trace(
        checkpoint,
        checkpoint,
        seed_base=9_100_000,
        decisions=8,
        num_envs=4,
        corpus_samples=5,
        threads=2,
        corpus_path=corpus,
        output_path=output,
    )

    assert result["trace_gate_passed"] is True
    assert result["masked_argmax_agreement_rate"] == 1.0
    assert result["maximum_absolute_logit_difference"] == 0.0
    assert result["source_illegal_actions"] == 0
    assert result["converted_illegal_actions"] == 0
    observations, masks, raw_sha = decode_corpus(corpus.read_bytes())
    assert observations.shape == (5, 104, 11, 22)
    assert masks.shape == (5, 13, 11, 22)
    assert raw_sha == result["corpus_raw_sha256"]
