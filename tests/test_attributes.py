from manimpango.attributes import *
import pytest


@pytest.mark.parametrize("values", [(1.0, 2), (1, 2.0), (1.0, 2.0)])
def test_attributes_accepts_only_int(values):
    with pytest.raises(ValueError):
        TextAttribute(*values)
