from typing import Dict, Iterator, List, Tuple, Union
import collections
import itertools
import operator
import textwrap


class Keyboard(collections.UserDict):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._neighbors_cache = {}

    @property
    def n_rows(self):
        return int(max(pos.real for pos in self.values()) + 1)

    @property
    def n_columns(self):
        return int(max(pos.imag for pos in self.values()) + 1)

    @property
    def shape(self):
        return (self.n_rows, self.n_columns)

    def char_distance(self, c1: str, c2: str, metric='l2') -> float:
        """Measure the Euclidean distance between two characters."""
        if c1 == c2:
            return 0.0
        if metric == 'l2':
            return abs(self[c1] - self[c2])
        elif metric == 'l1':
            return abs(self[c1].real - self[c2].real) + abs(self[c1].imag - self[c2].imag)
        raise ValueError(f"Unknown metric: {metric}, must be 'l1' or 'l2'")

    def word_distance(
        self, w1: str, w2: str, deletion_cost=1, insertion_cost=1, metric='l2'
    ) -> float:
        """Levenshtein distance between two words.

        This is an implementation of the Wagner-Fisher algorithm for measuring the Levenshtein
        distance between two words. The substitution distance is the character distance given
        by the `char_distance` method. The deletion and insertion costs can be provided and both
        default to 1.

        """
        D = [[0 for _ in range(len(w1) + 1)] for _ in range(len(w2) + 1)]

        for i in range(1, len(w2) + 1):
            D[i][0] = i

        for j in range(1, len(w1) + 1):
            D[0][j] = j

        for j, c1 in enumerate(w1, start=1):
            for i, c2 in enumerate(w2, start=1):
                substitution_cost = self.char_distance(c1, c2, metric=metric)
                D[i][j] = min(
                    D[i - 1][j] + deletion_cost,
                    D[i][j - 1] + insertion_cost,
                    D[i - 1][j - 1] + substitution_cost,
                )

        return D[-1][-1]

    def typing_distance(self, word: str, metric='l2') -> float:
        """Measure the sum of distances between each pair of consecutive characters."""
        return sum(self.char_distance(c1, c2, metric=metric) for c1, c2 in zip(word, word[1:]))

    def nearest_neighbors(
        self, char: str, k=None, cache=False, metric='l2'
    ) -> Iterator[Tuple[str, float]]:
        """Iterate over the k closest neighbors to a char."""

        if cache and (neighbors := self._neighbors_cache):
            yield from neighbors
            return

        neighbors = sorted(
            (
                (neighbor, self.char_distance(char, neighbor, metric=metric))
                for neighbor in self
                if neighbor != char
            ),
            key=operator.itemgetter(1),
        )

        if k is not None:
            neighbors = neighbors[:k]

        if cache:
            self._neighbors_cache[char] = neighbors

        yield from neighbors

    @classmethod
    def from_coordinates(
        cls,
        coordinates: Dict[str, Tuple[int, int]],
        staggering: Union[float, List] = 0,
        horizontal_pitch=1,
        vertical_pitch=1,
    ):
        """

        Parameters
        ----------
        coordinates
            A dictionary specifying the (row, col) location of each character. The origin is
            assumed to be at the top-left corner.
        staggering
            Controls the amount of staggering between consecutive rows. The amount of staggering is
            the same between pair of consecutive rows if a single number is specified. Variable
            amounts of staggering can be specified by providing a list of length `n_rows - 1`,
            within which the ith element corresponds the staggering between rows `i` and `i + 1`.
        horizontal_pitch
            The horizontal distance between the center of two adjacent keys.
        vertical_pitch
            The vertical distance between the center of two adjacent keys.

        """
        if isinstance(staggering, list):
            staggering = list(itertools.accumulate(staggering, initial=0))

        return cls(
            {
                char.lower(): complex(
                    i * vertical_pitch,
                    j * horizontal_pitch
                    + (
                        staggering[i]
                        if isinstance(staggering, list)
                        else i * staggering
                    ),
                )
                for char, (i, j) in coordinates.items()
            }
        )

    @classmethod
    def from_grid(
        cls,
        grid: str,
        staggering: Union[float, List] = 0,
        horizontal_pitch=1,
        vertical_pitch=1,
    ):
        """

        Parameters
        ----------
        grid
            A keyboard layout specified as a grid separated by spaces. See the examples to
            understand the format.
        staggering
            Controls the amount of staggering between consecutive rows. The amount of staggering is
            the same between pair of consecutive rows if a single number is specified. Variable
            amounts of staggering can be specified by providing a list of length `n_rows - 1`,
            within which the ith element corresponds the staggering between rows `i` and `i + 1`.
        horizontal_pitch
            The horizontal distance between the center of two adjacent keys.
        vertical_pitch
            The vertical distance between the center of two adjacent keys.

        """
        return cls.from_coordinates(
            coordinates={
                char: (i, j)
                for i, row in enumerate(filter(len, textwrap.dedent(grid).splitlines()))
                for j, char in enumerate(row[::2])
                if char
            },
            staggering=staggering,
            horizontal_pitch=horizontal_pitch,
            vertical_pitch=vertical_pitch,
        )

    def __repr__(self):
        rows = [[] for _ in range(self.n_rows)]
        reverse_layout = {
            (int(pos.real), int(pos.imag)): char for char, pos in self.items()
        }
        for i, j in sorted(reverse_layout.keys()):
            rows[i].extend([" "] * (j - len(rows[i])))
            rows[i].append(reverse_layout[i, j])
        return "\n".join(" ".join(row) for row in rows)

    def draw(self, fontsize=150):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()

        for char, pos in self.items():
            ax.text(
                pos.imag,
                pos.real,
                char,
                fontsize=fontsize,
                horizontalalignment="center",
                verticalalignment="center",
            )

        ax.axis("off")
        ax.invert_yaxis()

        return ax
