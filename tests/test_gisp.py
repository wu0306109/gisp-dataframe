from math import inf, log2

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

        sequences = [
            [
                (0, ['a', ]),
                (2, ['a', 'c', ]),
                (7, ['a', 'b', ]),
                (20, ['c', 'f', ]),
            ],
            [
                (0, ['a', 'd', ]),
                (14, ['c', ]),
                (26, ['c', ]),
            ],
            [
                (0, ['a', 'e', 'f', ]),
                (6, ['a', 'b', 'd', ]),
                (19, ['b', 'c', ]),
            ],
        ]
        isdb = Gisp.transform(sequences)
        right = DataFrame(
            [
                (0, 'a', 0),
                (0, 'a', 2),
                (0, 'c', 2),
                (0, 'a', 7),
                (0, 'b', 7),
                (0, 'c', 20),
                (0, 'f', 20),
                (1, 'a', 0),
                (1, 'd', 0),
                (1, 'c', 14),
                (1, 'c', 26),
                (2, 'a', 0),
                (2, 'e', 0),
                (2, 'f', 0),
                (2, 'a', 6),
                (2, 'b', 6),
                (2, 'd', 6),
                (2, 'b', 19),
                (2, 'c', 19),
            ],
            columns=['sid', 'item', 'interval'],
        )
        assert_frame_equal(isdb, right, check_dtype=False)

    def test_mine(self) -> None:
        isdb = DataFrame(
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
        gisp = Gisp(
            itemize=lambda t: t//86400, min_support=2, min_interval=0,
            max_interval=172900, min_whole_interval=0, max_whole_interval=inf)
        patterns = gisp.mine(isdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'a')], 3),
            Pattern([(0, 'a'), (0, 'b')], 2),
            Pattern([(0, 'a'), (2, 'a')], 2),
            Pattern([(0, 'b')], 2),
            Pattern([(0, 'c')], 2),
        ])

        isdb = DataFrame(
            [
                (0, 'a', 0),
                (0, 'a', 2),
                (0, 'c', 2),
                (0, 'a', 7),
                (0, 'b', 7),
                (0, 'c', 20),
                (0, 'f', 20),
                (1, 'a', 0),
                (1, 'd', 0),
                (1, 'c', 14),
                (1, 'c', 26),
                (2, 'a', 0),
                (2, 'e', 0),
                (2, 'f', 0),
                (2, 'a', 6),
                (2, 'b', 6),
                (2, 'd', 6),
                (2, 'b', 19),
                (2, 'c', 19),
            ],
            columns=['sid', 'item', 'interval'],
        )
        gisp = Gisp(
            itemize=lambda t: int(log2(t+1)), min_support=2, min_interval=0,
            max_interval=inf, min_whole_interval=0, max_whole_interval=inf)
        patterns = gisp.mine(isdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'a')], 3),
            Pattern([(0, 'b')], 2),
            Pattern([(0, 'c')], 3),
            Pattern([(0, 'd')], 2),
            Pattern([(0, 'f')], 2),
            Pattern([(0, 'a'), (0, 'b')], 2),
            Pattern([(0, 'a'), (0, 'd')], 2),
            Pattern([(0, 'a'), (2, 'a')], 2),
            Pattern([(0, 'a'), (2, 'b')], 2),
            Pattern([(0, 'a'), (3, 'b')], 2),
            Pattern([(0, 'a'), (3, 'c')], 3),
            Pattern([(0, 'a'), (4, 'c')], 3),
            Pattern([(0, 'a'), (0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'a'), (0, 'b')], 2),
            Pattern([(0, 'a'), (2, 'a'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'a'), (0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (0, 'd'), (3, 'c')], 2),
            Pattern([(0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'd'), (3, 'c')], 2),
        ])

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

    def test_mine_subpatterns_with_multi_level(self) -> None:
        pdb = DataFrame(
            [
                (0, 1, 'b', 0, 0),
                (0, 1, 'c', 13, 0),
                (0, 1, 'f', 13, 0),
                (2, 4, 'b', 0, 0),
                (2, 4, 'c', 0, 0),
                (2, 4, 'b', 13, 0),
                (2, 4, 'c', 13, 0),
            ],
            columns=['sid', 'pid', 'item', 'interval', 'whole_interval'],
        )
        gisp = Gisp(
            itemize=lambda t: int(log2(t+1)), min_support=2, min_interval=0,
            max_interval=inf, min_whole_interval=0, max_whole_interval=inf)
        patterns = gisp.mine_subpatterns(pdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'b')], 2),
            Pattern([(3, 'c')], 2),
            Pattern([(0, 'b'), (3, 'c')], 2),
        ])

        pdb = DataFrame(
            [
                (0, 0, 'a', 2, 2),
                (0, 0, 'c', 2, 2),
                (0, 0, 'a', 7, 7),
                (0, 0, 'b', 7, 7),
                (0, 0, 'c', 20, 20),
                (0, 0, 'f', 20, 20),
                (0, 1, 'c', 0, 0),
                (0, 1, 'a', 5, 5),
                (0, 1, 'b', 5, 5),
                (0, 1, 'c', 18, 18),
                (0, 1, 'f', 18, 18),
                (0, 2, 'b', 0, 0),
                (0, 2, 'c', 13, 13),
                (0, 2, 'f', 13, 13),
                (1, 3, 'd', 0, 0),
                (1, 3, 'c', 14, 14),
                (1, 3, 'c', 26, 26),
                (2, 4, 'e', 0, 0),
                (2, 4, 'f', 0, 0),
                (2, 4, 'a', 6, 6),
                (2, 4, 'b', 6, 6),
                (2, 4, 'd', 6, 6),
                (2, 4, 'b', 19, 19),
                (2, 4, 'c', 19, 19),
                (2, 5, 'b', 0, 0),
                (2, 5, 'd', 0, 0),
                (2, 5, 'b', 13, 13),
                (2, 5, 'c', 13, 13),
            ],
            columns=['sid', 'pid', 'item', 'interval', 'whole_interval'],
        )
        patterns = gisp.mine_subpatterns(pdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'b')], 2),
            Pattern([(0, 'd')], 2),
            Pattern([(2, 'a')], 2),
            Pattern([(2, 'b')], 2),
            Pattern([(3, 'b')], 2),
            Pattern([(3, 'c')], 3),
            Pattern([(4, 'c')], 3),
            Pattern([(0, 'b'), (3, 'c')], 2),
            Pattern([(2, 'a'), (0, 'b')], 2),
            Pattern([(2, 'a'), (3, 'c')], 2),
            Pattern([(2, 'a'), (0, 'b'), (3, 'c')], 2),
            Pattern([(2, 'b'), (3, 'c')], 2),
            Pattern([(0, 'd'), (3, 'c')], 2),
        ])

    def test_mine_with_constrainsts(self) -> None:
        isdb = DataFrame(
            [
                (0, 'a', 0),
                (0, 'a', 2),
                (0, 'c', 2),
                (0, 'a', 7),
                (0, 'b', 7),
                (0, 'c', 20),
                (0, 'f', 20),
                (1, 'a', 0),
                (1, 'd', 0),
                (1, 'c', 14),
                (1, 'c', 26),
                (2, 'a', 0),
                (2, 'e', 0),
                (2, 'f', 0),
                (2, 'a', 6),
                (2, 'b', 6),
                (2, 'd', 6),
                (2, 'b', 19),
                (2, 'c', 19),
            ],
            columns=['sid', 'item', 'interval'],
        )
        gisp = Gisp(
            itemize=lambda t: int(log2(t+1)), min_support=2, min_interval=6,
            max_interval=inf, min_whole_interval=0, max_whole_interval=inf)
        patterns = gisp.mine(isdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'a')], 3),
            Pattern([(0, 'b')], 2),
            Pattern([(0, 'c')], 3),
            Pattern([(0, 'd')], 2),
            Pattern([(0, 'f')], 2),
            Pattern([(0, 'a'), (3, 'b')], 2),
            Pattern([(0, 'a'), (3, 'c')], 3),
            Pattern([(0, 'a'), (4, 'c')], 3),
            Pattern([(0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'd'), (3, 'c')], 2),
        ])

        gisp = Gisp(
            itemize=lambda t: int(log2(t+1)), min_support=2, min_interval=0,
            max_interval=13, min_whole_interval=0, max_whole_interval=inf)
        patterns = gisp.mine(isdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'a')], 3),
            Pattern([(0, 'b')], 2),
            Pattern([(0, 'c')], 3),
            Pattern([(0, 'd')], 2),
            Pattern([(0, 'f')], 2),
            Pattern([(0, 'a'), (0, 'b')], 2),
            Pattern([(0, 'a'), (0, 'd')], 2),
            Pattern([(0, 'a'), (2, 'a')], 2),
            Pattern([(0, 'a'), (2, 'b')], 2),
            Pattern([(0, 'a'), (3, 'b')], 2),
            Pattern([(0, 'a'), (3, 'c')], 2),
            Pattern([(0, 'a'), (0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'a'), (0, 'b')], 2),
            Pattern([(0, 'a'), (2, 'a'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'a'), (0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'b'), (3, 'c')], 2),
            Pattern([(0, 'b'), (3, 'c')], 2),
        ])

        gisp = Gisp(
            itemize=lambda t: int(log2(t+1)), min_support=2, min_interval=0,
            max_interval=inf, min_whole_interval=6, max_whole_interval=inf)
        patterns = gisp.mine(isdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'a'), (3, 'b')], 2),
            Pattern([(0, 'a'), (3, 'c')], 3),
            Pattern([(0, 'a'), (4, 'c')], 3),
            Pattern([(0, 'a'), (0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'a'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'a'), (0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (0, 'd'), (3, 'c')], 2),
            Pattern([(0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'd'), (3, 'c')], 2),
        ])

        gisp = Gisp(
            itemize=lambda t: int(log2(t+1)), min_support=2, min_interval=0,
            max_interval=inf, min_whole_interval=0, max_whole_interval=13)
        patterns = gisp.mine(isdb)
        assert sorted(patterns) == sorted([
            Pattern([(0, 'a')], 3),
            Pattern([(0, 'b')], 2),
            Pattern([(0, 'c')], 3),
            Pattern([(0, 'd')], 2),
            Pattern([(0, 'f')], 2),
            Pattern([(0, 'a'), (0, 'b')], 2),
            Pattern([(0, 'a'), (0, 'd')], 2),
            Pattern([(0, 'a'), (2, 'a')], 2),
            Pattern([(0, 'a'), (2, 'b')], 2),
            Pattern([(0, 'a'), (3, 'b')], 2),
            Pattern([(0, 'a'), (3, 'c')], 2),
            Pattern([(0, 'a'), (0, 'b'), (3, 'c')], 2),
            Pattern([(0, 'a'), (2, 'a'), (0, 'b')], 2),
            Pattern([(0, 'b'), (3, 'c')], 2),
        ])