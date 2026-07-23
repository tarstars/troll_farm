from __future__ import annotations

from cgauto.agent_trajectory_command_audit import command_signature


def test_command_signature_removes_unit_identity_but_keeps_payload() -> None:
    assert command_signature("MOVE 7 3 4") == ("MOVE", "3", "4")
    assert command_signature("MOVE 9 3 4") == command_signature("MOVE 7 3 4")
    assert command_signature("PICK 7 banana") == ("PICK", "BANANA")
    assert command_signature("CHOP 7") == ("CHOP",)
    assert command_signature("WAIT") == ("WAIT",)
