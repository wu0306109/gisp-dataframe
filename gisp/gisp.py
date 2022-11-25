from typing import Callable, List, NamedTuple, Tuple

from pandas import DataFrame, concat


class Pattern(NamedTuple):

    # frequent interval-extended sequence,
    # which is a list of (itemized_interval, item)
    sequence: List[Tuple[int, str]]
    support: int  # number of the pattern occurrence


class Gisp:
    # A class maintaining settings for
    # Generalized Interval-extended Sequence Pattern mining
    #
    # There are two terms of database used in this class:
    # ISDB (interval-extended sequence database) and
    # PDB (Postfix database) which is an extention of ISDB.
    #
    # ISDB with columns 'sid': the ID of the sequence, 'item': the item itself,
    # and 'interval': the occurence of the item. ISDB should be sorted by
    # sid > interval > item ascendingly. A sequence for example
    # [(0, a), (86400m abc), (259200, ac)] would be represented as follow:
    #
    #   sid     item    interval
    #
    #   0       a       0
    #   0       a       86400
    #   0       b       86400
    #   0       c       86400
    #   0       a       259200
    #   0       c       259200
    #
    # PDB is an extention of ISDB with 2 mote columns 'pid' is the ID of the
    # postfix and 'whole_interval' is the interval from the head item. The a-
    # projected interval-extended sequence database represented in PDB is a the
    # collection of postfixes regard to a, where a is an interval-extended
    # sequence.

    def __init__(
            self, itemize: Callable[[int], int], min_support: int,
            min_interval: int, max_interval: int,
            min_whole_interval: int, max_whole_interval: int
    ) -> None:
        self._itemize = itemize
        self._min_support = min_support
        self._min_interval = min_interval
        self._max_interval = max_interval
        self._min_whole_interval = min_whole_interval
        self._max_whole_interval = max_whole_interval

    @staticmethod
    def transform(sequences: List[Tuple[int, List[str]]]) -> DataFrame:
        """Transform sequences into DataFrame (ISDB) for mining."""

        def yield_item_rows() -> Tuple[int, str, int]:
            for sid, sequence in enumerate(sequences):
                for interval, items in sequence:
                    for item in items:
                        yield sid, item, interval

        isdb = DataFrame(yield_item_rows(), columns=[
                         'sid', 'item', 'interval'])
        isdb.sort_values(by=['sid', 'interval', 'item'], inplace=True)
        return isdb

    def mine(self, isdb: DataFrame) -> List[Pattern]:
        """Driver function to run the algorithm on the given database."""
        pass

    def mine_subpatterns(self, pdb: DataFrame) -> List[Pattern]:
        """Perform level 2 or later projection to mine subpatterns recursively.

        Args:
            projected_db: The a- projected interval-extended sequence database 
                is a the collection of postfixes regard to a, where a be an 
                interval-extended sequence. Each item in the database is a list
                of postfixes for the original sequence.
        """

        def yield_sub_pdbs(itemized_interval: int, item: str) -> DataFrame:
            """Yield sub-PDBs of postfix projected by (itemized_interval, item).
            """
            matches = pdb[
                (pdb['item'] == item)
                & (pdb['itemized_interval'] == itemized_interval)]
            for i, (_, pid, _, interval, _, _) in matches.iterrows():
                sub_pdb = pdb[pdb['pid'] == pid].loc[i + 1:]
                sub_pdb['interval'] -= interval
                yield sub_pdb.drop(columns=['itemized_interval'])

        pdb['itemized_interval'] = pdb['interval'].apply(self._itemize)

        constraints = (
            (pdb['interval'] >= self._min_interval)
            & (pdb['interval'] <= self._max_interval)
            & (pdb['whole_interval'] >= self._min_whole_interval)
            & (pdb['whole_interval'] <= self._max_whole_interval))
        counts = pdb[constraints].drop_duplicates(
            subset=['sid', 'item', 'itemized_interval']).value_counts(
                subset=['item', 'itemized_interval'])
        counts = counts[counts >= self._min_support]

        patterns = []
        for (item, itemized_interval), count in counts.items():
            patterns.append(Pattern(
                sequence=[(itemized_interval, item)],
                support=count))

            child_pdb = concat(yield_sub_pdbs(itemized_interval, item))
            subpatterns = self.mine_subpatterns(child_pdb)

            for pattern in subpatterns:
                pattern.sequence.insert(0, (itemized_interval, item))
            patterns.extend(subpatterns)
        return patterns


def mine(
    sequences: List[Tuple[int, List[str]]], itemize: Callable[[int], int],
    min_support: int, min_interval: int = None, max_interval: int = None,
    min_whole_interval: int = None, max_whole_interval: int = None,
) -> List[Pattern]:
    """Mine frequent interval-extended sequences.

    Args:
        sequences: Interval-extended sequences, 
            where each sequence is a list of (interval, items).
        itemize: Converting function from interval to pseudo counts.
        min_support: Minimal number of occurrence for resulting patterns.
        min_interval: Minimum interval between any two adjacent items.
        max_interval: Maximum interval between any two adjacent items.
        min_whole_interval: Minimum interval between 
            the head and the tail of the sequence.
        max_whole_interval: Maximum interval between
            the head and the tail of the sequence.

    Returns:
        List of Pattern(sequence, support), 
        where sequence is a list of (itemized_interval, item),
        and support is the number of the pattern occurrence.
    """
    pass
