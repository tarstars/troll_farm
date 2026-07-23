import numpy as np

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d149a_joint_two_stage_policy as d149a
from cgauto import train_d149b_state_conditioned_joint_policy as d149b


def test_state_conditioned_shapes_and_parameter_budget():
    data = __import__(
        "tests.test_train_d149a_joint_two_stage_policy",
        fromlist=["tiny_dataset"],
    ).tiny_dataset()
    tensors = d149a.tensors(data)
    inputs = d149b.proposal_inputs(tensors["actions"], tensors["states"])
    assert inputs.shape == (4, 2, 443)
    model, summary = d149b.train_model(
        data, 14901, 14951, rank_epochs=2, gate_epochs=2, threads=1
    )
    assert d115.parameter_count(model) == 7810
    context, selected, logits = d149b.winner_context(model.ranker, data)
    assert context.shape == (4, 84)
    assert selected.shape == (4,)
    assert logits.shape == (4, 2)
    assert np.isfinite(context.detach().numpy()).all()
    assert summary["ranker"]["groups"] == 2
