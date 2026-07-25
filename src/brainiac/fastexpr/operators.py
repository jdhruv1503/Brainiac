"""Registry of Fast Expression operators with machine-checkable signatures.

The registry is what lets Brainiac reject a broken alpha locally instead of spending a
simulation slot to discover the same thing minutes later. Every entry declares its
positional parameters, optional keyword parameters and return kind, so the validator can
check arity, literal-only parameters (lookback windows must be integer constants) and
grouping arguments without evaluating anything.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

__all__ = [
    "Category",
    "Kind",
    "OperatorSpec",
    "Parameter",
    "canonical_name",
    "get_operator",
    "iter_operators",
    "operator_names",
]


class Kind(Enum):
    """The value shape an argument accepts or an operator returns."""

    VECTOR = "vector"
    """Per-instrument, per-day numeric series."""
    BOOL = "bool"
    """Per-instrument, per-day boolean mask."""
    GROUP = "group"
    """Per-instrument grouping key (sector, industry, ...)."""
    NUMBER = "number"
    """Scalar numeric literal."""
    WINDOW = "window"
    """Positive integer lookback expressed in days; must be a literal."""
    STRING = "string"
    """String literal chosen from a fixed set."""
    ANY = "any"


class Category(Enum):
    ARITHMETIC = "arithmetic"
    LOGICAL = "logical"
    MATH = "math"
    TRANSFORMATIONAL = "transformational"
    CROSS_SECTIONAL = "cross_sectional"
    TIME_SERIES = "time_series"
    GROUP = "group"
    VECTOR = "vector"
    SPECIAL = "special"


@dataclass(frozen=True)
class Parameter:
    name: str
    kind: Kind
    default: object | None = None
    choices: tuple[str, ...] = ()

    @property
    def required(self) -> bool:
        return self.default is None and self.kind is not Kind.ANY


@dataclass(frozen=True)
class OperatorSpec:
    name: str
    category: Category
    params: tuple[Parameter, ...] = ()
    varargs: Parameter | None = None
    kwargs: Mapping[str, Parameter] = field(default_factory=dict)
    returns: Kind = Kind.VECTOR
    doc: str = ""
    alias_of: str | None = None
    """Set when this name is a legacy/incorrect spelling the canonicalizer rewrites."""

    @property
    def min_args(self) -> int:
        return sum(1 for p in self.params if p.required)

    @property
    def max_args(self) -> int | None:
        return None if self.varargs is not None else len(self.params)

    def parameter_at(self, index: int) -> Parameter | None:
        if index < len(self.params):
            return self.params[index]
        return self.varargs


def _parse_param(spec: str) -> Parameter:
    """Build a :class:`Parameter` from a compact ``name:kind[=default][|choices]`` string."""
    body, _, choice_text = spec.partition("|")
    name_kind, _, default_text = body.partition("=")
    name, _, kind_text = name_kind.partition(":")
    kind = Kind(kind_text or "vector")
    default: object | None = None
    if default_text:
        lowered = default_text.lower()
        if lowered in {"true", "false"}:
            default = lowered == "true"
        elif lowered == "none":
            default = "none"
        else:
            try:
                default = float(default_text) if "." in default_text else int(default_text)
            except ValueError:
                default = default_text
    choices = tuple(choice_text.split(",")) if choice_text else ()
    return Parameter(name=name, kind=kind, default=default, choices=choices)


def _op(
    name: str,
    category: Category,
    *params: str,
    varargs: str | None = None,
    kw: Iterable[str] = (),
    returns: Kind = Kind.VECTOR,
    doc: str = "",
    alias_of: str | None = None,
) -> OperatorSpec:
    keywords = {}
    for spec in kw:
        parameter = _parse_param(spec)
        keywords[parameter.name] = parameter
    return OperatorSpec(
        name=name,
        category=category,
        params=tuple(_parse_param(p) for p in params),
        varargs=_parse_param(varargs) if varargs else None,
        kwargs=keywords,
        returns=returns,
        doc=doc,
        alias_of=alias_of,
    )


_A = Category.ARITHMETIC
_L = Category.LOGICAL
_M = Category.MATH
_T = Category.TRANSFORMATIONAL
_X = Category.CROSS_SECTIONAL
_TS = Category.TIME_SERIES
_G = Category.GROUP
_V = Category.VECTOR
_S = Category.SPECIAL

_SPECS: Final[tuple[OperatorSpec, ...]] = (
    # ---- arithmetic -------------------------------------------------
    _op("add", _A, "x", "y", varargs="more", kw=["filter:bool=false"], doc="Sum of all inputs."),
    _op("subtract", _A, "x", "y", kw=["filter:bool=false"], doc="x - y."),
    _op("multiply", _A, "x", "y", varargs="more", kw=["filter:bool=false"], doc="Product."),
    _op("divide", _A, "x", "y", doc="x / y; NaN when y is 0."),
    _op("reverse", _A, "x", doc="-x."),
    _op("inverse", _A, "x", doc="1 / x."),
    _op("power", _A, "x", "y:number", kw=["precise:bool=false"], doc="x ** y."),
    _op("signed_power", _A, "x", "y", doc="sign(x) * abs(x) ** y."),
    _op("log", _M, "x", doc="Natural logarithm."),
    _op("log_diff", _A, "x", doc="log(x) - log(ts_delay(x, 1))."),
    _op("s_log_1p", _A, "x", doc="sign(x) * log(1 + abs(x))."),
    _op("exp", _M, "x", doc="e ** x."),
    _op("sqrt", _M, "x", doc="Square root."),
    _op("abs", _M, "x", doc="Absolute value."),
    _op("ceiling", _M, "x"),
    _op("floor", _M, "x"),
    _op("round", _M, "x", kw=["decimals:number=0"]),
    _op("round_down", _M, "x", "f:number=1"),
    _op("sign", _M, "x", doc="-1, 0 or 1."),
    _op("fraction", _A, "x", doc="Signed fractional part."),
    _op("nan_mask", _A, "x", "y", doc="NaN out x where y < 0."),
    _op("nan_out", _A, "x", "lower:number=0", "upper:number=0"),
    _op("purify", _A, "x", doc="Replace infinities with NaN."),
    _op("to_nan", _A, "x", "value:number=0", kw=["reverse:bool=false"]),
    _op("densify", _T, "x", returns=Kind.GROUP, doc="Compress a sparse grouping field."),
    _op("replace", _A, "x", kw=["target:string", "dest:string"]),
    _op("arc_cos", _M, "x"),
    _op("arc_sin", _M, "x"),
    _op("arc_tan", _M, "x"),
    _op("sigmoid", _M, "x"),
    _op("tanh", _M, "x"),
    # ---- logical ----------------------------------------------------
    _op("and", _L, "x:bool", "y:bool", returns=Kind.BOOL),
    _op("or", _L, "x:bool", "y:bool", returns=Kind.BOOL),
    _op("not", _L, "x:bool", returns=Kind.BOOL),
    _op("less", _L, "x", "y", returns=Kind.BOOL),
    _op("equal", _L, "x", "y", returns=Kind.BOOL),
    _op("greater", _L, "x", "y", returns=Kind.BOOL),
    _op("is_nan", _L, "x", returns=Kind.BOOL),
    _op("is_finite", _L, "x", returns=Kind.BOOL),
    _op("is_not_nan", _L, "x", returns=Kind.BOOL),
    _op("if_else", _L, "condition:bool", "if_true", "if_false", doc="Vectorised conditional."),
    # ---- statistical / cross sectional ------------------------------
    _op("max", _M, "x", "y", varargs="more", doc="Element-wise maximum of all inputs."),
    _op("min", _M, "x", "y", varargs="more", doc="Element-wise minimum of all inputs."),
    _op("zscore", _X, "x", doc="Cross-sectional z-score."),
    _op("winsorize", _X, "x", kw=["std:number=4"]),
    _op("normalize", _X, "x", kw=["useStd:bool=false", "limit:number=0.0"]),
    _op("one_side", _X, "x", kw=["side:string=long|long,short"]),
    _op(
        "quantile",
        _X,
        "x",
        kw=["driver:string=gaussian|gaussian,uniform,cauchy", "sigma:number=1.0"],
    ),
    _op("rank", _X, "x", kw=["rate:number=2"], doc="Cross-sectional rank scaled to [0, 1]."),
    _op("rank_by_side", _X, "x", kw=["rate:number=2", "scale:number=1"]),
    _op("generalized_rank", _X, "x", kw=["m:number=1"]),
    _op("regression_neut", _X, "y", "x", doc="Cross-sectional residual of y on x."),
    _op("regression_proj", _X, "y", "x"),
    _op("scale", _X, "x", kw=["scale:number=1", "longscale:number=1", "shortscale:number=1"]),
    _op("scale_down", _X, "x", kw=["constant:number=0"]),
    _op("truncate", _X, "x", kw=["maxPercent:number=0.01"]),
    _op("vector_neut", _X, "x", "y"),
    _op("vector_proj", _X, "x", "y"),
    _op("rank_gmean_amean_diff", _X, "x", "y", varargs="more"),
    # ---- time series ------------------------------------------------
    _op("ts_delay", _TS, "x", "d:window"),
    _op("ts_delta", _TS, "x", "d:window"),
    _op("ts_mean", _TS, "x", "d:window"),
    _op("ts_median", _TS, "x", "d:window"),
    _op("ts_sum", _TS, "x", "d:window"),
    _op("ts_product", _TS, "x", "d:window"),
    _op("ts_std_dev", _TS, "x", "d:window"),
    _op("ts_skewness", _TS, "x", "d:window"),
    _op("ts_kurtosis", _TS, "x", "d:window"),
    _op("ts_min", _TS, "x", "d:window"),
    _op("ts_max", _TS, "x", "d:window"),
    _op("ts_arg_min", _TS, "x", "d:window"),
    _op("ts_arg_max", _TS, "x", "d:window"),
    _op("ts_rank", _TS, "x", "d:window", kw=["constant:number=0"]),
    _op("ts_zscore", _TS, "x", "d:window"),
    _op("ts_scale", _TS, "x", "d:window", kw=["constant:number=0"]),
    _op("ts_corr", _TS, "x", "y", "d:window"),
    _op("ts_covariance", _TS, "x", "y", "d:window"),
    _op("ts_returns", _TS, "x", "d:window", kw=["mode:number=1"]),
    _op("ts_av_diff", _TS, "x", "d:window"),
    _op("ts_ir", _TS, "x", "d:window"),
    _op("ts_entropy", _TS, "x", "d:window", kw=["buckets:number=10"]),
    _op("ts_moment", _TS, "x", "d:window", "k:number"),
    _op("ts_decay_linear", _TS, "x", "d:window", kw=["dense:bool=false"]),
    _op("ts_decay_exp_window", _TS, "x", "d:window", kw=["factor:number=1.0", "nan:bool=true"]),
    _op("ts_backfill", _TS, "x", "d:window", kw=["k:number=1", "ignore:string=NAN"]),
    _op("ts_co_kurtosis", _TS, "y", "x", "d:window"),
    _op("ts_co_skewness", _TS, "y", "x", "d:window"),
    _op("ts_partial_corr", _TS, "x", "y", "z", "d:window"),
    _op("ts_percentage", _TS, "x", "d:window", kw=["percentage:number=0.5"]),
    _op("ts_poly_regression", _TS, "y", "x", "d:window", kw=["k:number=1"]),
    _op("ts_regression", _TS, "y", "x", "d:window", kw=["lag:number=0", "rettype:number=0"]),
    _op("ts_theilsen", _TS, "x", "y", "d:window"),
    _op("ts_triple_corr", _TS, "x", "y", "z", "d:window"),
    _op("ts_weighted_delay", _TS, "x", kw=["k:number=0.5"]),
    _op("ts_step", _TS, "d:window", doc="Linear ramp of length d, newest value first."),
    _op("ts_rank_gmean_amean_diff", _TS, "x", "y", "d:window"),
    _op("days_from_last_change", _TS, "x"),
    _op("hump", _TS, "x", kw=["hump:number=0.01"]),
    _op("hump_decay", _TS, "x", kw=["p:number=0.1", "relative:bool=false"]),
    _op(
        "jump_decay",
        _TS,
        "x",
        "d:window",
        kw=["stddev:bool=false", "sensitivity:number=1.0", "force:number=0.1"],
    ),
    _op("last_diff_value", _TS, "x", "d:window"),
    _op("kth_element", _TS, "x", "d:window", kw=["k:number=1", "ignore:string=NAN"]),
    # ---- group ------------------------------------------------------
    _op("group_backfill", _G, "x", "group:group", "d:window", kw=["std:number=4.0"]),
    _op("group_coalesce", _G, "group:group", varargs="more:group", returns=Kind.GROUP),
    _op("group_count", _G, "x", "group:group"),
    _op("group_extra", _G, "x", "weight", "group:group"),
    _op("group_max", _G, "x", "group:group"),
    _op("group_mean", _G, "x", "weight", "group:group"),
    _op("group_median", _G, "x", "group:group"),
    _op("group_min", _G, "x", "group:group"),
    _op("group_neutralize", _G, "x", "group:group"),
    _op(
        "group_normalize",
        _G,
        "x",
        "group:group",
        kw=["constantCheck:bool=false", "tolerance:number=0.01", "scale:number=1"],
    ),
    _op("group_percentage", _G, "x", "group:group", kw=["percentage:number=0.5"]),
    _op("group_rank", _G, "x", "group:group"),
    _op("group_scale", _G, "x", "group:group"),
    _op("group_std_dev", _G, "x", "group:group"),
    _op("group_sum", _G, "x", "group:group"),
    _op("group_zscore", _G, "x", "group:group"),
    _op("group_vector_neut", _G, "x", "y", "group:group"),
    _op("group_vector_proj", _G, "x", "y", "group:group"),
    _op(
        "bucket",
        _T,
        "x",
        kw=[
            "buckets:string",
            "range:string",
            "skipBegin:bool=false",
            "skipEnd:bool=false",
            "skipBoth:bool=false",
            "NANGroup:bool=false",
        ],
        returns=Kind.GROUP,
    ),
    # ---- vector (multi-value fields) --------------------------------
    _op("vec_avg", _V, "x"),
    _op("vec_sum", _V, "x"),
    _op("vec_count", _V, "x"),
    _op("vec_max", _V, "x"),
    _op("vec_min", _V, "x"),
    _op("vec_stddev", _V, "x"),
    _op("vec_skewness", _V, "x"),
    _op("vec_kurtosis", _V, "x"),
    _op("vec_ir", _V, "x"),
    _op("vec_norm", _V, "x"),
    _op("vec_powersum", _V, "x", kw=["constant:number=2"]),
    _op("vec_range", _V, "x"),
    _op("vec_choose", _V, "x", kw=["nth:number=0"]),
    # ---- special ----------------------------------------------------
    _op("trade_when", _S, "trigger:bool", "alpha", "exit:bool"),
    _op("pasteurize", _S, "x"),
    _op("convert", _S, "x", kw=["mode:string=dollar2share|dollar2share,share2dollar"]),
    _op("inst_pnl", _S, "x"),
    _op("left_tail", _S, "x", kw=["maximum:number=0"]),
    _op("right_tail", _S, "x", kw=["minimum:number=0"]),
    _op("tail", _S, "x", kw=["lower:number=0", "upper:number=0", "newval:number=0"]),
    _op("keep", _S, "x", "f", kw=["period:number=5"]),
    _op("filter", _S, "x", kw=["h:string", "t:string"]),
    _op(
        "clamp",
        _S,
        "x",
        kw=["lower:number=0", "upper:number=0", "inverse:bool=false", "mask:string=nearest_bound"],
    ),
    _op("__index__", _V, "x", "index:number", doc="Vector field subscript ``x[i]``."),
    # ---- aliases the canonicalizer rewrites -------------------------
    _op("mean", _TS, "x", "d:window", alias_of="ts_mean", doc="Legacy spelling of ts_mean."),
    _op("median", _TS, "x", "d:window", alias_of="ts_median"),
    _op("std_dev", _TS, "x", "d:window", alias_of="ts_std_dev"),
    _op("stddev", _TS, "x", "d:window", alias_of="ts_std_dev"),
    _op("skewness", _TS, "x", "d:window", alias_of="ts_skewness"),
    _op("kurtosis", _TS, "x", "d:window", alias_of="ts_kurtosis"),
    _op("corr", _TS, "x", "y", "d:window", alias_of="ts_corr"),
    _op("covariance", _TS, "x", "y", "d:window", alias_of="ts_covariance"),
    _op("delay", _TS, "x", "d:window", alias_of="ts_delay"),
    _op("delta", _TS, "x", "d:window", alias_of="ts_delta"),
    _op("sum", _TS, "x", "d:window", alias_of="ts_sum"),
    _op("product", _TS, "x", "d:window", alias_of="ts_product"),
    _op("decay_linear", _TS, "x", "d:window", kw=["dense:bool=false"], alias_of="ts_decay_linear"),
    _op("ts_stddev", _TS, "x", "d:window", alias_of="ts_std_dev"),
    _op("ts_count_nans", _TS, "x", "d:window"),
    _op("ts_quantile", _TS, "x", "d:window", kw=["driver:string=gaussian|gaussian,uniform,cauchy"]),
    _op("signed_log", _A, "x", alias_of="s_log_1p"),
    _op("ifelse", _L, "condition:bool", "if_true", "if_false", alias_of="if_else"),
)

_REGISTRY: Final[dict[str, OperatorSpec]] = {spec.name: spec for spec in _SPECS}


def get_operator(name: str) -> OperatorSpec | None:
    """Look up an operator by name, or ``None`` when it is unknown."""
    return _REGISTRY.get(name)


def canonical_name(name: str) -> str:
    """Resolve legacy operator spellings (``mean`` -> ``ts_mean``)."""
    spec = _REGISTRY.get(name)
    if spec is not None and spec.alias_of:
        return spec.alias_of
    return name


def operator_names() -> frozenset[str]:
    return frozenset(_REGISTRY)


def iter_operators() -> Iterable[OperatorSpec]:
    return _SPECS


def operators_by_category() -> dict[Category, list[OperatorSpec]]:
    grouped: dict[Category, list[OperatorSpec]] = {}
    for spec in _SPECS:
        if spec.alias_of:
            continue
        grouped.setdefault(spec.category, []).append(spec)
    return grouped
