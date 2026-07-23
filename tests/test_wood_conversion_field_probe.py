"""Pure tests for wood-conversion telemetry reconstruction."""

from cgauto.wood_conversion_field_probe import parse_events, telemetry_summary


def test_telemetry_reconstructs_partial_fell_from_next_state() -> None:
    result = {
        "frames": [
            {
                "stderr": (
                    "@WC_STATE t=1 u=0 x=2 y=2 cw=0 free=1 iw=0\n"
                    "@WC_SELECT t=1 u=0 op=CHOP kind=BANANA x=2 y=2 "
                    "size=2 health=1 fruits=0 chop=1 free=1\n"
                )
            },
            {"stderr": "@WC_STATE t=2 u=0 x=2 y=2 cw=1 free=0 iw=0\n"},
        ]
    }

    summary = telemetry_summary(result)

    assert summary["chops"]["chop_actions"] == 1
    assert summary["chops"]["fells"] == 1
    assert summary["chops"]["wood_gained"] == 1
    assert summary["chops"]["partial_fells"] == 1
    assert summary["chops"]["wood_lost_to_carry"] == 1
    assert summary["chops"]["wood_recoverable_by_banking"] == 0
    assert summary["chops"]["wood_unavoidable_at_capacity"] == 1
    assert summary["chops"]["other_uncollected_wood"] == 0


def test_outer_override_removes_inner_selection() -> None:
    raw = (
        "@WC_STATE t=9 u=0 x=1 y=1 cw=0 free=1 iw=0\n"
        "@WC_SELECT t=9 u=0 op=MOVE kind=APPLE x=4 y=4 size=4 health=20 "
        "fruits=1 chop=1 free=1\n"
        "@WC_OVERRIDE t=9 u=0 op=HARVEST\n"
    )

    summary = telemetry_summary({"frames": [{"stderr": raw}]})

    assert len(parse_events(raw)) == 3
    assert summary["overrides"] == 1
    assert summary["assignments"]["count"] == 0
