"""The in-memory panel the local evaluator runs against.

A :class:`Panel` is a ``(dates x instruments)`` cube of named fields, mirroring how BRAIN
presents data to Fast Expression: every field is a matrix aligned on the same date and
instrument axes, and grouping fields hold small integer codes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pandas as pd

__all__ = ["Panel", "PanelError"]


class PanelError(ValueError):
    """Raised when a panel is constructed with inconsistent inputs."""


@dataclass
class Panel:
    """Aligned market data for a universe of instruments over a date range.

    Attributes:
        dates: Sorted trading dates, one per row.
        instruments: Instrument identifiers, one per column.
        fields: Numeric matrices of shape ``(len(dates), len(instruments))``.
        groups: Integer grouping matrices (sector, industry, ...) of the same shape.
        tradable: Boolean mask of which instrument is in the universe on each date.
    """

    dates: np.ndarray
    instruments: tuple[str, ...]
    fields: dict[str, np.ndarray] = field(default_factory=dict)
    groups: dict[str, np.ndarray] = field(default_factory=dict)
    tradable: np.ndarray | None = None

    def __post_init__(self) -> None:
        self.dates = np.asarray(self.dates)
        expected = (len(self.dates), len(self.instruments))
        for name, matrix in {**self.fields, **self.groups}.items():
            if matrix.shape != expected:
                raise PanelError(f"Field {name!r} has shape {matrix.shape}, expected {expected}.")
        if self.tradable is None:
            self.tradable = np.ones(expected, dtype=bool)
        elif self.tradable.shape != expected:
            raise PanelError(f"tradable mask has shape {self.tradable.shape}, expected {expected}.")

    # -- shape ---------------------------------------------------------

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.dates), len(self.instruments)

    @property
    def n_dates(self) -> int:
        return len(self.dates)

    @property
    def n_instruments(self) -> int:
        return len(self.instruments)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and (name in self.fields or name in self.groups)

    def names(self) -> frozenset[str]:
        return frozenset(self.fields) | frozenset(self.groups)

    # -- access --------------------------------------------------------

    def get(self, name: str) -> np.ndarray:
        """Fetch a field or grouping matrix as float64, raising :class:`KeyError` if absent."""
        if name in self.fields:
            return self.fields[name]
        if name in self.groups:
            return self.groups[name].astype(np.float64)
        raise KeyError(name)

    def group_codes(self, name: str) -> np.ndarray:
        """Integer grouping codes for ``name``; a numeric field is bucketed by exact value."""
        if name in self.groups:
            return self.groups[name]
        if name in self.fields:
            return _to_codes(self.fields[name])
        raise KeyError(name)

    def with_fields(self, extra: Mapping[str, np.ndarray]) -> Panel:
        """A copy with additional fields; useful for injecting derived signals."""
        merged = dict(self.fields)
        merged.update(
            {name: np.asarray(matrix, dtype=np.float64) for name, matrix in extra.items()}
        )
        return Panel(
            dates=self.dates,
            instruments=self.instruments,
            fields=merged,
            groups=dict(self.groups),
            tradable=self.tradable,
        )

    def slice_dates(self, start: int | None = None, stop: int | None = None) -> Panel:
        """Restrict the panel to ``dates[start:stop]``."""
        window = slice(start, stop)
        assert self.tradable is not None
        return Panel(
            dates=self.dates[window],
            instruments=self.instruments,
            fields={name: matrix[window] for name, matrix in self.fields.items()},
            groups={name: matrix[window] for name, matrix in self.groups.items()},
            tradable=self.tradable[window],
        )

    def date_index(self, target: object) -> int:
        """Index of the first date greater than or equal to ``target``."""
        return int(np.searchsorted(self.dates, np.datetime64(str(target))))

    # -- construction --------------------------------------------------

    @classmethod
    def from_frames(
        cls,
        frames: Mapping[str, pd.DataFrame],
        *,
        group_names: Iterable[str] = (),
        tradable: pd.DataFrame | None = None,
    ) -> Panel:
        """Build a panel from ``{field: DataFrame(index=dates, columns=instruments)}``."""
        if not frames:
            raise PanelError("At least one field frame is required.")
        iterator = iter(frames.values())
        reference = next(iterator)
        dates = reference.index.to_numpy()
        instruments = tuple(str(column) for column in reference.columns)

        group_set = set(group_names)
        fields: dict[str, np.ndarray] = {}
        groups: dict[str, np.ndarray] = {}
        for name, frame in frames.items():
            aligned = frame.reindex(index=reference.index, columns=reference.columns)
            if name in group_set:
                groups[name] = _to_codes(aligned.to_numpy())
            else:
                fields[name] = aligned.to_numpy(dtype=np.float64)
        mask = (
            tradable.reindex(index=reference.index, columns=reference.columns).to_numpy(dtype=bool)
            if tradable is not None
            else None
        )
        return cls(
            dates=dates, instruments=instruments, fields=fields, groups=groups, tradable=mask
        )

    def to_frame(self, name: str) -> pd.DataFrame:
        """Return one field as a pandas DataFrame indexed by date."""
        import pandas as pd

        return pd.DataFrame(self.get(name), index=self.dates, columns=list(self.instruments))

    def describe(self) -> str:
        first = self.dates[0] if self.n_dates else "-"
        last = self.dates[-1] if self.n_dates else "-"
        return (
            f"Panel({self.n_dates} dates {first}..{last}, {self.n_instruments} instruments, "
            f"{len(self.fields)} fields, {len(self.groups)} groups)"
        )


def _to_codes(matrix: np.ndarray) -> np.ndarray:
    """Map arbitrary labels to dense integer codes, using ``-1`` for missing values."""
    flat = matrix.reshape(-1)
    if matrix.dtype.kind in {"i", "u"}:
        return matrix.astype(np.int64)
    if matrix.dtype.kind == "f":
        codes = np.where(np.isnan(flat), -1.0, flat)
        unique = np.unique(codes[codes >= 0])
        lookup = {value: index for index, value in enumerate(unique)}
        mapped = np.array([lookup.get(value, -1) for value in codes], dtype=np.int64)
        return mapped.reshape(matrix.shape)
    unique = {value: index for index, value in enumerate(sorted({str(v) for v in flat}))}
    mapped = np.array([unique[str(value)] for value in flat], dtype=np.int64)
    return mapped.reshape(matrix.shape)
