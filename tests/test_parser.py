def test_parser_mock():
    # Placeholder for parser test
    parsed = {"meals": [
        {"name": "meal1", "confidence_level": "high", "estimation_origin": "gpt"},
        {"name": "meal2", "confidence_level": "low", "estimation_origin": "manual"}
    ]}
    assert "meals" in parsed
    assert len(parsed["meals"]) == 2
    for meal in parsed["meals"]:
        assert meal["confidence_level"] in ["high", "medium", "low"]
        assert meal["estimation_origin"] in ["gpt", "rule", "manual"] 