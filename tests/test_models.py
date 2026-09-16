import pytest
from pydantic import ValidationError

from src.models import SearchResult


def test_search_result_accepts_valid_confidence():
    result = SearchResult(answer="a", sections=["x"], sources=["doc"], confidence=0.75)
    assert result.confidence == 0.75


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_search_result_rejects_out_of_range_confidence(confidence):
    with pytest.raises(ValidationError):
        SearchResult(answer="a", sections=[], sources=[], confidence=confidence)
