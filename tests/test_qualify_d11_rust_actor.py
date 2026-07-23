import struct

import numpy as np
import pytest

from cgauto.qualify_d11_rust_actor import (
    ACTION_COUNT,
    HEADER,
    OBSERVATION_BYTES,
    OUTPUT_MAGIC,
    decode_runner_output,
    encode_runner_input,
)


def test_runner_input_is_exact_and_deterministic() -> None:
    observations = np.arange(2 * OBSERVATION_BYTES, dtype=np.uint8).reshape(2, 104, 11, 22)
    masks = np.zeros((2, 13, 11, 22), dtype=np.uint8)
    masks[:, 0, 0, 0] = 1
    encoded = encode_runner_input(observations, masks)

    assert encoded[:8] == b"TFD11IN1"
    assert struct.unpack_from("<I", encoded, 8)[0] == 2
    assert encoded == encode_runner_input(observations.copy(), masks.copy())
    assert len(encoded) == HEADER.size + observations.size + masks.size


def test_runner_output_decoder_handles_interleaved_records() -> None:
    first = np.arange(ACTION_COUNT, dtype="<f4")
    second = -first
    encoded = bytearray(HEADER.pack(OUTPUT_MAGIC, 2))
    encoded.extend(first.tobytes())
    encoded.extend(struct.pack("<I", 17))
    encoded.extend(second.tobytes())
    encoded.extend(struct.pack("<I", 29))

    logits, actions = decode_runner_output(bytes(encoded), 2)
    assert np.array_equal(logits[0], first)
    assert np.array_equal(logits[1], second)
    assert actions.tolist() == [17, 29]


def test_runner_codecs_reject_wrong_shapes_and_headers() -> None:
    with pytest.raises(ValueError, match="observation shape"):
        encode_runner_input(np.zeros((1, 2), dtype=np.uint8), np.zeros((1, 13, 11, 22), dtype=np.uint8))
    with pytest.raises(ValueError, match="runner output header"):
        decode_runner_output(HEADER.pack(b"WRONGMAG", 0), 0)
