import pytest

from rent.rent_comparator import RentComparator


def test_rent_comparison_is_deferred():
    with pytest.raises(NotImplementedError):
        RentComparator().compare(700, "Cork")