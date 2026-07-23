from cgauto.compact_rust_source import compact


def test_compactor_preserves_literals_lifetimes_and_required_boundaries() -> None:
    source = r'''
// removed
fn example<'a>(x: &'a str) -> &'a str {
    let raw = r#"// not a comment { }"#;
    let escaped = "/* literal */ \\";
    let byte = b'x';
    let slash = 4 / / 2;
    let range = 1 . . 3;
    /* outer /* nested */ comment */
    if x = = raw { escaped } else { x }
}
'''

    result = compact(source)

    assert "removed" not in result
    assert r'r#"// not a comment { }"#' in result
    assert r'"/* literal */ \\"' in result
    assert "example<'a>" in result
    assert "4/ /2" in result
    assert "1 . . 3" in result
    assert "x= =raw" in result


def test_compactor_does_not_merge_words_or_literal_prefixes() -> None:
    assert compact('let value = move item;') == 'let value=move item;'
    assert compact('let value = b "text";') == 'let value=b "text";'
    assert compact('let value = r # ident;') == 'let value=r #ident;'
