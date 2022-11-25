from math import inf

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from gisp.gisp import Gisp, Pattern


class TestGisp:

    def test_transform(self) -> None:
        sequences = [
            [(0, ['a', ]), (86400, ['a', 'b', 'c', ]), (259200, ['a', 'c', ])],
            [(0, ['a', 'd', ]), (259200, ['c', ])],
            [(0, ['a', 'e', 'f', ]), (172800, ['a', 'b', ])],
        ]
        isdb = Gisp.transform(sequences)
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

    def test_mine_subpatterns(self) -> None:
        pdb = DataFrame(
            [
                (0, 0, 'a', 86400, 86400),
                (0, 0, 'b', 86400, 86400),
                (0, 0, 'c', 86400, 86400),
                (0, 0, 'a', 259200, 259200),
                (0, 0, 'c', 259200, 259200),
                (0, 1, 'b', 0, 0),
                (0, 1, 'c', 0, 0),
                (0, 1, 'a', 172800, 172800),
                (0, 1, 'c', 172800, 172800),
                (0, 2, 'c', 0, 0),
                (1, 3, 'd', 0, 0),
                (1, 3, 'c', 259200, 259200),
                (2, 4, 'e', 0, 0),
                (2, 4, 'f', 0, 0),
                (2, 4, 'a', 172800, 172800),
                (2, 4, 'b', 172800, 172800),
                (2, 5, 'b', 0, 0),
            ],
            columns=['sid', 'pid', 'item', 'interval', 'whole_interval'],
        )
        gisp = Gisp(
            itemize=lambda t: t//86400, min_support=2, min_interval=0,
            max_interval=172900, min_whole_interval=0, max_whole_interval=inf)
        patterns = gisp.mine_subpatterns(pdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'b')], 2),
            Pattern([(2, 'a')], 2),
        ])
