import pytest

import clavier


@pytest.mark.parametrize(
    "w1,w2,expected", [("kitten", "sitting", 3), ("saturday", "sunday", 3)]
)
def test_levenshtein(w1, w2, expected):
    """Tests word distance by assuming the distance between characters is always 1."""
    keyboard = clavier.load_qwerty()

    def mock_distance(c1, c2, metric):
        return 1 if c1 != c2 else 0

    keyboard.char_distance = mock_distance
    assert keyboard.word_distance(w1, w2) == expected


def test_phone_number_distance() -> None:
    dialpad = clavier.load_dialpad()
    assert dialpad.word_distance("123", "423") == 1.0
    assert dialpad.word_distance("123", "523") == pytest.approx(1.414, 0.001)
    assert dialpad.word_distance("123", "183") == 2.0
    assert dialpad.word_distance("1234", "123") == 1.0
