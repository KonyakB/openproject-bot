from app.openproject.mapper import match_value


def test_match_value_case_insensitive() -> None:
    matched, fuzzy = match_value("Space1", ["space1", "space2"])
    assert matched == "space1"
    assert fuzzy is False


def test_match_value_slug_match() -> None:
    matched, fuzzy = match_value("space-1", ["space 1", "space2"])
    assert matched == "space 1"
    assert fuzzy is False


def test_match_value_ambiguous_fuzzy() -> None:
    matched, fuzzy = match_value("elec", ["electronics", "electrical"])
    assert matched is None
    assert fuzzy is True
