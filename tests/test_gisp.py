from pandas import DataFrame
from pandas.testing import assert_frame_equal

from gisp.gisp import Gisp


class TestGisp:

    def test_transform(self):
        sequences = [
            [(0, ['a', ]), (86400, ['a', 'b', 'c', ]), (259200, ['a', 'c', ])],
            [(0, ['a', 'd', ]), (259200, ['c', ])],
            [(0, ['a', 'e', 'f', ]), (172800, ['a', 'b', ])],
        ]
        gisp = Gisp(itemize=None, min_support=None)
        isdb = gisp.transform(sequences)
        right = DataFrame(
            [
                (0, 'a', 0),
                (0, 'a', 86400),
                (0, 'b', 86400),
                (0, 'c', 86400),
                (0, 'a', 259200),
                (0, 'c', 259200),
                (1, 'a', 0),
                (1, 'd', 0),
                (1, 'c', 259200),
                (2, 'a', 0),
                (2, 'e', 0),
                (2, 'f', 0),
                (2, 'a', 172800),
                (2, 'b', 172800),
            ],
            columns=['sid', 'item', 'interval'],
        )
        assert_frame_equal(isdb, right, check_dtype=False)


