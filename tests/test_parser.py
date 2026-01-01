from comptext_codex.parser import CompTextParser


def test_parse_single_command_without_options():
    parser = CompTextParser()
    parsed = parser.parse("@CODE_ANALYZE")
    assert parsed[0].name == "CODE_ANALYZE"
    assert parsed[0].options == {}


def test_parse_multiple_commands_with_options():
    parser = CompTextParser()
    parsed = parser.parse("@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]")
    assert len(parsed) == 2
    assert parsed[0].options == {"perf_bottleneck": True}
    assert parsed[1].options == {"explain": "detail", "bench": "compare"}


def test_execute_adds_summary_and_context():
    parser = CompTextParser()
    result = parser.execute("@DOC_SUMMARY[style=executive, length=short]", audience="cto")
    assert result["summary"] == "DOC_SUMMARY(style=executive, length=short)"
    assert result["context"] == {"audience": "cto"}


def test_invalid_command_raises_error():
    parser = CompTextParser()
    try:
        parser.parse("CODE_ANALYZE")
    except ValueError as exc:
        assert "Invalid command syntax" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_catalog_can_be_loaded():
    from comptext_codex.catalog import load_catalog

    catalog = load_catalog()
    assert isinstance(catalog, list)
    assert catalog, "Catalog should not be empty"
