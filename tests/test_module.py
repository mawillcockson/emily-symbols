"""
ensures properties of the module stay consistent
"""
import emily_symbols


def test_uniqueStarters_unique() -> None:
    "are the unique starters unique?"
    # set() discards duplicate elements
    uniqueStarters = set(emily_symbols.uniqueStarters)

    # if any elements were discarded the set will contain fewer elements than
    # the original list
    assert len(uniqueStarters) == len(emily_symbols.uniqueStarters)


def test_uniqueStarters_match_symbols() -> None:
    "are the starters in uniqueStarters exactly the ones used in symbols?"
    assert emily_symbols.uniqueStarters == list(emily_symbols.symbols.keys()), (
        "uniqueStarters does not exactly match "
        "the starters used in the symbols dictionary"
    )
