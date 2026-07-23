from cgauto.make_d29b_submission import assemble, compact_renamed


def test_compact_renamed_changes_only_identifier_tokens():
    source = 'fn long_name(){let long_name=1;println!("long_name {}",long_name);}'
    assert compact_renamed(source, {"long_name": "x"}) == (
        'fn x(){let x=1;println!("long_name {}",x);}'
    )


def test_d29b_submission_assembles_below_limit():
    source, sizes = assemble()
    assert len(source.encode()) == sizes["total"]
    assert sizes["total"] < 100_000
    assert "let mut bot=D::n();" in source
    assert "let mut bot=SecureOrchardBot::new();" not in source
    assert "mod d29f{" in source
    assert "mod d29k{" in source
    assert "mod d29o{" in source
