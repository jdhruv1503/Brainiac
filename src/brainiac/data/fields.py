"""Catalogue of BRAIN data fields, loaded from the bundled dataset exports.

The original project shipped a hand-maintained ``datasets_chn.md`` prompt table and
referenced a ``datasets_usa.md`` that never existed, so any USA alpha crashed on a missing
file. Here the catalogue is derived from the CSV exports instead, and the prompt tables are
generated on demand for whichever region and delay we are actually targeting.
"""

from __future__ import annotations

import functools
import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from brainiac.knowledge import knowledge_path

__all__ = ["FieldRegistry", "FieldSpec", "FieldType", "default_registry"]

_COVERAGE_RE: Final = re.compile(r"(\d+(?:\.\d+)?)\s*%")
# The exports use em/en dashes to mean "no coverage in this region".
_MISSING: Final = frozenset({"", "-", "\u2014", "\u2013", "n/a", "na", "none"})

#: Fields every region exposes as grouping keys.
GROUP_FIELDS: Final[frozenset[str]] = frozenset(
    {"market", "sector", "industry", "subindustry", "country", "exchange"}
)

#: Price/volume fields that are always present; used as the local engine's base panel.
CORE_FIELDS: Final[tuple[str, ...]] = (
    "open",
    "high",
    "low",
    "close",
    "vwap",
    "volume",
    "returns",
    "adv20",
    "cap",
    "sharesout",
    "dividend",
    "split",
)


class FieldType(str):
    MATRIX = "matrix"
    VECTOR = "vector"
    GROUP = "group"


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """One BRAIN data field, at one delay setting."""

    id: str
    description: str
    delay: int
    type: str
    dataset: str
    coverage: dict[str, float | None]

    def available_in(self, region: str) -> bool:
        return self.coverage.get(region.upper()) is not None

    def coverage_in(self, region: str) -> float | None:
        return self.coverage.get(region.upper())

    @property
    def is_group(self) -> bool:
        return self.type == FieldType.GROUP or self.id in GROUP_FIELDS

    @property
    def is_vector(self) -> bool:
        return self.type == FieldType.VECTOR


def _parse_coverage(text: str) -> float | None:
    cleaned = text.strip()
    if cleaned.lower() in _MISSING:
        return None
    match = _COVERAGE_RE.search(cleaned)
    if match:
        return float(match.group(1)) / 100.0
    if cleaned in {"✔", "yes", "Y"}:
        return 1.0
    return None


def _dataset_name_from_filename(path: Path) -> str:
    """``CompanyFundamentalDataForEquity.csv`` -> ``Company Fundamental Data For Equity``."""
    stem = path.stem
    return re.sub(r"(?<!^)(?=[A-Z])", " ", stem).replace("  ", " ").strip()


def _split_row(line: str, tail_columns: int) -> tuple[str, str, list[str]] | None:
    """Split a header-less row into ``(field, description, tail)``.

    The exports are not quoted and several descriptions contain commas, so the row is
    anchored on the first column and the known number of trailing columns.
    """
    parts = line.rstrip("\n").split(",")
    if len(parts) < tail_columns + 2:
        return None
    field = parts[0].strip()
    tail = [part.strip() for part in parts[-tail_columns:]]
    description = ",".join(parts[1:-tail_columns]).strip()
    if not field:
        return None
    return field, description, tail


@dataclass(frozen=True)
class _Layout:
    """Where delay/type/coverage live inside a file's trailing columns."""

    tail_columns: int
    delay_index: int
    type_index: int
    region_indexes: dict[str, int]


def _detect_layout(header: str) -> _Layout:
    columns = [column.strip() for column in header.rstrip("\n").split(",")]
    tail_columns = len(columns) - 2
    tail = columns[-tail_columns:]
    lowered = [column.lower() for column in tail]

    delay_index = lowered.index("delay") if "delay" in lowered else 0
    type_index = lowered.index("type") if "type" in lowered else 1

    regions: dict[str, int] = {}
    for region in ("USA", "CHN"):
        if region.lower() in lowered:
            regions[region] = lowered.index(region.lower())
    if not regions:
        # ``Covg, Thm, Covg, Thm`` style header: first coverage is USA, second is CHN.
        coverage_indexes = [i for i, name in enumerate(lowered) if name.startswith("cov")]
        for region, index in zip(("USA", "CHN"), coverage_indexes, strict=False):
            regions[region] = index
    return _Layout(tail_columns, delay_index, type_index, regions)


class FieldRegistry:
    """Queryable collection of :class:`FieldSpec` entries."""

    def __init__(self, specs: Iterable[FieldSpec]) -> None:
        self._specs = tuple(specs)
        self._by_id: dict[str, list[FieldSpec]] = {}
        for spec in self._specs:
            self._by_id.setdefault(spec.id, []).append(spec)

    def __len__(self) -> int:
        return len(self._specs)

    def __iter__(self) -> Iterator[FieldSpec]:
        return iter(self._specs)

    def __contains__(self, field_id: object) -> bool:
        return isinstance(field_id, str) and field_id in self._by_id

    @classmethod
    def from_directory(cls, directory: Path | None = None) -> FieldRegistry:
        """Load every ``*.csv`` export in ``directory`` (defaults to the bundled catalogue)."""
        root = directory or knowledge_path("datasets")
        specs: list[FieldSpec] = []
        for path in sorted(root.glob("*.csv")):
            specs.extend(cls._load_file(path))
        return cls(specs)

    @staticmethod
    def _load_file(path: Path) -> list[FieldSpec]:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if not lines:
            return []
        layout = _detect_layout(lines[0])
        dataset = _dataset_name_from_filename(path)
        specs: list[FieldSpec] = []
        seen: set[tuple[str, int]] = set()
        for line in lines[1:]:
            if not line.strip():
                continue
            row = _split_row(line, layout.tail_columns)
            if row is None:
                continue
            field, description, tail = row
            try:
                delay = int(tail[layout.delay_index])
            except (ValueError, IndexError):
                continue
            key = (field, delay)
            if key in seen:
                continue
            seen.add(key)
            field_type = tail[layout.type_index].lower() if layout.type_index < len(tail) else ""
            coverage = {
                region: _parse_coverage(tail[index]) if index < len(tail) else None
                for region, index in layout.region_indexes.items()
            }
            specs.append(
                FieldSpec(
                    id=field,
                    description=description,
                    delay=delay,
                    type=field_type or FieldType.MATRIX,
                    dataset=dataset,
                    coverage=coverage,
                )
            )
        return specs

    # -- queries -------------------------------------------------------

    def get(self, field_id: str, delay: int | None = None) -> FieldSpec | None:
        candidates = self._by_id.get(field_id)
        if not candidates:
            return None
        if delay is None:
            return candidates[0]
        for spec in candidates:
            if spec.delay == delay:
                return spec
        return None

    def variants(self, field_id: str) -> tuple[FieldSpec, ...]:
        return tuple(self._by_id.get(field_id, ()))

    def known_ids(self) -> frozenset[str]:
        return frozenset(self._by_id)

    def group_fields(self) -> frozenset[str]:
        found = {spec.id for spec in self._specs if spec.is_group}
        return frozenset(found | GROUP_FIELDS)

    def vector_fields(self) -> frozenset[str]:
        return frozenset(spec.id for spec in self._specs if spec.is_vector)

    def datasets(self) -> tuple[str, ...]:
        return tuple(sorted({spec.dataset for spec in self._specs}))

    def available(
        self,
        region: str,
        delay: int | None = None,
        *,
        min_coverage: float = 0.0,
        datasets: Sequence[str] | None = None,
        types: Sequence[str] | None = None,
    ) -> tuple[FieldSpec, ...]:
        """Fields usable for a given region/delay, optionally filtered by coverage."""
        wanted_datasets = {name.lower() for name in datasets} if datasets else None
        wanted_types = {name.lower() for name in types} if types else None
        results = []
        for spec in self._specs:
            if delay is not None and spec.delay != delay:
                continue
            coverage = spec.coverage_in(region)
            if coverage is None or coverage < min_coverage:
                continue
            if wanted_datasets is not None and spec.dataset.lower() not in wanted_datasets:
                continue
            if wanted_types is not None and spec.type.lower() not in wanted_types:
                continue
            results.append(spec)
        return tuple(sorted(results, key=lambda s: (-(s.coverage_in(region) or 0.0), s.id)))

    def is_available(self, field_id: str, region: str, delay: int | None = None) -> bool:
        if field_id in GROUP_FIELDS:
            return True
        specs = self.variants(field_id)
        if not specs:
            return False
        if delay is None:
            return any(spec.available_in(region) for spec in specs)
        matching = [spec for spec in specs if spec.delay == delay]
        if not matching:
            # BRAIN exposes delay-1 data to delay-0 alphas but never the other way round.
            matching = [spec for spec in specs if spec.delay < delay]
        return any(spec.available_in(region) for spec in matching)

    def markdown_table(
        self,
        region: str,
        delay: int | None = 1,
        *,
        limit: int | None = 150,
        min_coverage: float = 0.0,
        datasets: Sequence[str] | None = None,
    ) -> str:
        """Render a prompt-ready table of the highest-coverage fields for a region."""
        specs = self.available(
            region, delay, min_coverage=min_coverage, datasets=datasets, types=["matrix", "group"]
        )
        if limit is not None:
            specs = specs[:limit]
        rows = ["| Field | Description | Type | Coverage | Dataset |", "|---|---|---|---|---|"]
        for spec in specs:
            coverage = spec.coverage_in(region)
            coverage_text = f"{coverage:.0%}" if coverage is not None else "-"
            description = spec.description.replace("|", "/")[:120]
            rows.append(
                f"| {spec.id} | {description} | {spec.type} | {coverage_text} | {spec.dataset} |"
            )
        return "\n".join(rows)

    def search(self, query: str, *, limit: int = 25) -> tuple[FieldSpec, ...]:
        """Cheap keyword search over field ids and descriptions."""
        terms = [term for term in re.split(r"\W+", query.lower()) if len(term) > 2]
        if not terms:
            return ()
        scored: list[tuple[int, FieldSpec]] = []
        for spec in self._specs:
            haystack = f"{spec.id} {spec.description}".lower()
            score = sum(3 if term in spec.id.lower() else haystack.count(term) for term in terms)
            if score:
                scored.append((score, spec))
        scored.sort(key=lambda item: (-item[0], item[1].id))
        return tuple(spec for _, spec in scored[:limit])


@functools.lru_cache(maxsize=1)
def default_registry() -> FieldRegistry:
    """The bundled field catalogue, loaded once per process."""
    return FieldRegistry.from_directory()
