"""Static validation and linting of Fast Expression alphas.

An LLM writing Fast Expression makes the same handful of mistakes over and over:
hallucinated operators, wrong arity, a lookback window passed as an expression, a data
field that does not exist in the target region, or a raw signal with no cross-sectional
normalisation. Each one costs a simulation slot to discover remotely. This module finds
them locally in microseconds and, where the fix is unambiguous, applies it.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from brainiac.data.fields import FieldRegistry, default_registry
from brainiac.fastexpr import ast as fx
from brainiac.fastexpr.canonical import canonicalize
from brainiac.fastexpr.errors import FastExprError, LexError, ParseError
from brainiac.fastexpr.operators import Kind, OperatorSpec, canonical_name, get_operator
from brainiac.fastexpr.parser import parse
from brainiac.fastexpr.printer import unparse

__all__ = [
    "Diagnostic",
    "Severity",
    "ValidationReport",
    "ValidationSettings",
    "validate",
    "validate_source",
]

#: BRAIN rejects lookbacks longer than this, and very long windows rarely help anyway.
MAX_WINDOW = 512

#: Operators whose output is already scaled/neutralised across the cross section.
NORMALISING_OPERATORS = frozenset(
    {
        "rank",
        "rank_by_side",
        "generalized_rank",
        "zscore",
        "normalize",
        "scale",
        "scale_down",
        "quantile",
        "winsorize",
        "group_neutralize",
        "group_rank",
        "group_zscore",
        "group_scale",
        "group_normalize",
        "regression_neut",
        "vector_neut",
        "truncate",
        "one_side",
    }
)

#: Wrappers that pass the shape of their payload argument through unchanged.
_TRANSPARENT_WRAPPERS = {
    "trade_when": 1,
    "pasteurize": 0,
    "purify": 0,
    "hump": 0,
    "hump_decay": 0,
    "jump_decay": 0,
    "if_else": 1,
    "clamp": 0,
    "left_tail": 0,
    "right_tail": 0,
    "tail": 0,
    "nan_out": 0,
    "to_nan": 0,
}


class Severity(StrEnum):
    ERROR = "error"
    """The alpha cannot run; do not submit it."""
    WARNING = "warning"
    """The alpha will run but is likely to fail a BRAIN gate check or waste a slot."""
    INFO = "info"
    """Style and quality observations."""


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: Severity
    message: str
    suggestion: str | None = None
    location: str | None = None

    def __str__(self) -> str:
        where = f" [{self.location}]" if self.location else ""
        hint = f" Suggestion: {self.suggestion}" if self.suggestion else ""
        return f"{self.severity.value}: {self.code}{where}: {self.message}{hint}"


@dataclass(frozen=True)
class ValidationSettings:
    """Knobs that describe the simulation the alpha is destined for."""

    region: str = "USA"
    delay: int = 1
    max_nodes: int = 220
    max_depth: int = 24
    max_window: int = MAX_WINDOW
    require_normalisation: bool = True
    unknown_field_severity: Severity = Severity.ERROR


@dataclass
class ValidationReport:
    """Result of validating one alpha."""

    source: str
    diagnostics: list[Diagnostic] = field(default_factory=list)
    program: fx.Program | None = None
    repaired_source: str | None = None
    fields_used: frozenset[str] = frozenset()
    node_count: int = 0
    depth: int = 0

    @property
    def ok(self) -> bool:
        """True when nothing blocks submission."""
        return not self.errors

    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity is Severity.WARNING]

    @property
    def infos(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity is Severity.INFO]

    def codes(self) -> set[str]:
        return {d.code for d in self.diagnostics}

    def summary(self) -> str:
        if self.ok and not self.diagnostics:
            return "valid"
        counts = [
            f"{len(self.errors)} error(s)",
            f"{len(self.warnings)} warning(s)",
            f"{len(self.infos)} info",
        ]
        return ", ".join(counts)


def validate_source(
    source: str,
    settings: ValidationSettings | None = None,
    registry: FieldRegistry | None = None,
) -> ValidationReport:
    """Parse and validate raw Fast Expression source."""
    settings = settings or ValidationSettings()
    registry = registry or default_registry()
    report = ValidationReport(source=source)

    stripped = source.strip()
    if not stripped:
        report.diagnostics.append(
            Diagnostic("empty-alpha", Severity.ERROR, "The alpha source is empty.")
        )
        return report

    try:
        program = parse(source)
    except (ParseError, LexError) as exc:
        report.diagnostics.append(
            Diagnostic("syntax-error", Severity.ERROR, str(exc.message), location=str(exc.span))
        )
        return report
    except FastExprError as exc:  # pragma: no cover - defensive
        report.diagnostics.append(Diagnostic("syntax-error", Severity.ERROR, str(exc)))
        return report

    report.program = program
    return validate(program, settings=settings, registry=registry, report=report)


def validate(
    program: fx.Program,
    *,
    settings: ValidationSettings | None = None,
    registry: FieldRegistry | None = None,
    report: ValidationReport | None = None,
) -> ValidationReport:
    """Run every semantic check against an already-parsed program."""
    settings = settings or ValidationSettings()
    registry = registry or default_registry()
    report = report or ValidationReport(source=unparse(program), program=program)
    diagnostics = report.diagnostics

    report.node_count = fx.size(program)
    report.depth = fx.depth(program)

    locals_defined: set[str] = set()
    locals_used: set[str] = set()
    fields_used: set[str] = set()
    group_fields = registry.group_fields()

    def check_expression(node: fx.Expr, *, expected: Kind = Kind.VECTOR) -> None:
        match node:
            case fx.Identifier(name=name):
                _check_identifier(name, expected)
            case fx.Call(func=func, args=args, kwargs=kwargs):
                _check_call(func, args, kwargs, expected)
            case fx.UnaryOp(operand=operand):
                check_expression(operand)
            case fx.BinaryOp(op=op, left=left, right=right):
                check_expression(left)
                check_expression(right)
                if op == "/" and isinstance(right, fx.NumberLiteral) and right.value == 0:
                    diagnostics.append(
                        Diagnostic(
                            "division-by-zero",
                            Severity.ERROR,
                            "Division by the literal 0 always yields NaN.",
                            location=unparse(node),
                        )
                    )
            case fx.Ternary(condition=condition, if_true=if_true, if_false=if_false):
                check_expression(condition, expected=Kind.BOOL)
                check_expression(if_true)
                check_expression(if_false)
            case _:
                return

    def _check_identifier(name: str, expected: Kind) -> None:
        if name in locals_defined:
            locals_used.add(name)
            return
        fields_used.add(name)
        if name not in registry:
            similar = _closest_field(name, registry)
            diagnostics.append(
                Diagnostic(
                    "unknown-field",
                    settings.unknown_field_severity,
                    f"{name!r} is not a known data field or defined variable.",
                    suggestion=f"Did you mean {similar!r}?" if similar else None,
                    location=name,
                )
            )
            return
        if not registry.is_available(name, settings.region, settings.delay):
            available = [
                region
                for region in ("USA", "CHN")
                if registry.is_available(name, region, settings.delay)
            ]
            hint = f"Available in {', '.join(available)}." if available else None
            diagnostics.append(
                Diagnostic(
                    "field-unavailable",
                    Severity.ERROR,
                    f"{name!r} has no coverage in region {settings.region} at delay "
                    f"{settings.delay}.",
                    suggestion=hint,
                    location=name,
                )
            )
        if expected is Kind.GROUP and name not in group_fields:
            diagnostics.append(
                Diagnostic(
                    "not-a-group-field",
                    Severity.ERROR,
                    f"{name!r} is a data field, not a grouping field.",
                    suggestion=f"Use one of {', '.join(sorted(group_fields))}, "
                    f"or wrap it in bucket(...)/densify(...).",
                    location=name,
                )
            )
        spec = registry.get(name)
        if spec is not None and spec.is_vector:
            diagnostics.append(
                Diagnostic(
                    "vector-field-needs-aggregation",
                    Severity.WARNING,
                    f"{name!r} is a vector field and must be reduced before use.",
                    suggestion=f"Wrap it, e.g. vec_avg({name}).",
                    location=name,
                )
            )

    def _check_call(
        func: str,
        args: Sequence[fx.Expr],
        kwargs: Sequence[fx.Keyword],
        expected: Kind,
    ) -> None:
        spec = get_operator(func)
        if spec is None:
            similar = _closest_operator(func)
            diagnostics.append(
                Diagnostic(
                    "unknown-operator",
                    Severity.ERROR,
                    f"{func!r} is not a Fast Expression operator.",
                    suggestion=f"Did you mean {similar!r}?" if similar else None,
                    location=f"{func}(...)",
                )
            )
            for arg in args:
                check_expression(arg)
            for keyword in kwargs:
                check_expression(keyword.value)
            return

        if spec.alias_of:
            diagnostics.append(
                Diagnostic(
                    "legacy-operator",
                    Severity.WARNING,
                    f"{func!r} is a legacy spelling of {spec.alias_of!r}.",
                    suggestion=f"Rename to {spec.alias_of}.",
                    location=f"{func}(...)",
                )
            )
            spec = get_operator(spec.alias_of) or spec

        _check_arity(spec, func, args)
        _check_keywords(spec, func, kwargs)

        if expected is Kind.GROUP and spec.returns is not Kind.GROUP:
            diagnostics.append(
                Diagnostic(
                    "not-a-group-field",
                    Severity.ERROR,
                    f"{func}(...) returns a {spec.returns.value}, but a grouping field is "
                    "required here.",
                    suggestion="Use bucket(...), densify(...) or a group field such as sector.",
                    location=f"{func}(...)",
                )
            )

        for index, arg in enumerate(args):
            parameter = spec.parameter_at(index)
            kind = parameter.kind if parameter else Kind.VECTOR
            if kind is Kind.WINDOW:
                _check_window(func, parameter.name if parameter else f"arg{index}", arg)
                continue
            check_expression(arg, expected=kind)

        for keyword in kwargs:
            parameter = spec.kwargs.get(keyword.name)
            if parameter is not None and parameter.choices:
                _check_choice(func, parameter.name, parameter.choices, keyword.value)
            check_expression(keyword.value, expected=Kind.VECTOR)

    def _check_arity(spec: OperatorSpec, func: str, args: Sequence[fx.Expr]) -> None:
        maximum = spec.max_args
        if len(args) < spec.min_args:
            expected = f"at least {spec.min_args}" if maximum is None else f"{spec.min_args}"
            names = ", ".join(p.name for p in spec.params[: spec.min_args])
            diagnostics.append(
                Diagnostic(
                    "bad-arity",
                    Severity.ERROR,
                    f"{func}() takes {expected} argument(s) but got {len(args)}.",
                    suggestion=f"Signature: {func}({names})",
                    location=f"{func}(...)",
                )
            )
        elif maximum is not None and len(args) > maximum:
            diagnostics.append(
                Diagnostic(
                    "bad-arity",
                    Severity.ERROR,
                    f"{func}() takes at most {maximum} positional argument(s) but got {len(args)}.",
                    suggestion="Extra options must be passed as named arguments.",
                    location=f"{func}(...)",
                )
            )

    def _check_keywords(spec: OperatorSpec, func: str, kwargs: Sequence[fx.Keyword]) -> None:
        for keyword in kwargs:
            if keyword.name in spec.kwargs:
                continue
            positional = {p.name for p in spec.params}
            if keyword.name in positional:
                diagnostics.append(
                    Diagnostic(
                        "positional-as-keyword",
                        Severity.ERROR,
                        f"{keyword.name!r} is a positional parameter of {func}() and cannot "
                        "be passed by name.",
                        location=f"{func}(...)",
                    )
                )
                continue
            allowed = ", ".join(sorted(spec.kwargs)) or "none"
            diagnostics.append(
                Diagnostic(
                    "unknown-keyword",
                    Severity.ERROR,
                    f"{func}() has no named argument {keyword.name!r}.",
                    suggestion=f"Accepted named arguments: {allowed}.",
                    location=f"{func}(...)",
                )
            )

    def _check_window(func: str, parameter: str, arg: fx.Expr) -> None:
        if not isinstance(arg, fx.NumberLiteral):
            diagnostics.append(
                Diagnostic(
                    "non-literal-window",
                    Severity.ERROR,
                    f"{func}() expects {parameter} to be an integer constant, got "
                    f"{unparse(arg)!r}.",
                    suggestion="Lookback windows must be literals, e.g. ts_mean(close, 20).",
                    location=f"{func}(...)",
                )
            )
            check_expression(arg)
            return
        if not arg.is_integral or arg.value < 1:
            diagnostics.append(
                Diagnostic(
                    "invalid-window",
                    Severity.ERROR,
                    f"{func}() expects {parameter} to be a positive whole number of days, got "
                    f"{unparse(arg)}.",
                    location=f"{func}(...)",
                )
            )
        elif arg.value > settings.max_window:
            diagnostics.append(
                Diagnostic(
                    "window-too-long",
                    Severity.WARNING,
                    f"{func}() uses a {int(arg.value)}-day window, beyond the "
                    f"{settings.max_window}-day limit.",
                    location=f"{func}(...)",
                )
            )

    def _check_choice(func: str, parameter: str, choices: Sequence[str], value: fx.Expr) -> None:
        if isinstance(value, fx.StringLiteral) and value.value not in choices:
            diagnostics.append(
                Diagnostic(
                    "invalid-choice",
                    Severity.ERROR,
                    f"{func}({parameter}={value.value!r}) is not one of {', '.join(choices)}.",
                    location=f"{func}(...)",
                )
            )

    for statement in program.statements:
        if statement.target in locals_defined:
            diagnostics.append(
                Diagnostic(
                    "redefined-variable",
                    Severity.WARNING,
                    f"Variable {statement.target!r} is assigned more than once.",
                    location=statement.target,
                )
            )
        if get_operator(statement.target) is not None or statement.target in registry:
            diagnostics.append(
                Diagnostic(
                    "shadowed-name",
                    Severity.WARNING,
                    f"Variable {statement.target!r} shadows a data field or operator.",
                    location=statement.target,
                )
            )
        check_expression(statement.value)
        locals_defined.add(statement.target)

    check_expression(program.output)

    for name in sorted(locals_defined - locals_used):
        if isinstance(program.output, fx.Identifier) and program.output.name == name:
            continue
        diagnostics.append(
            Diagnostic(
                "unused-variable",
                Severity.INFO,
                f"Variable {name!r} is assigned but never used.",
                location=name,
            )
        )

    report.fields_used = frozenset(fields_used)

    if not fields_used:
        diagnostics.append(
            Diagnostic(
                "constant-alpha",
                Severity.ERROR,
                "The alpha references no data fields, so it produces a constant portfolio.",
            )
        )

    if report.node_count > settings.max_nodes:
        diagnostics.append(
            Diagnostic(
                "too-complex",
                Severity.WARNING,
                f"The alpha has {report.node_count} nodes (budget {settings.max_nodes}); "
                "large expressions overfit and are slow to simulate.",
            )
        )
    if report.depth > settings.max_depth:
        diagnostics.append(
            Diagnostic(
                "too-deep",
                Severity.WARNING,
                f"The alpha nests {report.depth} levels deep (budget {settings.max_depth}).",
            )
        )

    if settings.require_normalisation and not _is_normalised(program):
        diagnostics.append(
            Diagnostic(
                "no-normalisation",
                Severity.INFO,
                "The output is a raw signal with no cross-sectional normalisation, which "
                "usually concentrates weight in a few names.",
                suggestion="Wrap the output, e.g. rank(...) or group_neutralize(..., sector).",
            )
        )

    duplicates = _repeated_subexpressions(program)
    for text, count in duplicates:
        diagnostics.append(
            Diagnostic(
                "repeated-subexpression",
                Severity.INFO,
                f"{text!r} is computed {count} times.",
                suggestion="Assign it to a variable to keep the alpha readable and cheap.",
            )
        )

    # A repair is only meaningful for an alpha that already runs; the remaining errors
    # (hallucinated operators, missing fields, wrong arity) need a new expression, not a
    # rewrite of this one.
    if not report.errors:
        repaired_source = unparse(_repair(program, settings))
        if repaired_source != unparse(program):
            report.repaired_source = repaired_source

    return report


def _is_normalised(program: fx.Program) -> bool:
    """Whether the alpha's output passes through a cross-sectional normaliser."""
    bindings = {statement.target: statement.value for statement in program.statements}
    seen: set[str] = set()

    def check(node: fx.Expr) -> bool:
        match node:
            case fx.Identifier(name=name) if name in bindings and name not in seen:
                seen.add(name)
                return check(bindings[name])
            case fx.Call(func=func, args=args):
                if canonical_name(func) in NORMALISING_OPERATORS:
                    return True
                index = _TRANSPARENT_WRAPPERS.get(canonical_name(func))
                if index is not None and index < len(args):
                    return check(args[index])
                return False
            case fx.BinaryOp(op=op, left=left, right=right) if op in {"+", "-", "*", "/"}:
                return check(left) and check(right)
            case fx.UnaryOp(operand=operand):
                return check(operand)
            case fx.NumberLiteral():
                return True
            case _:
                return False

    return check(program.output)


def _repeated_subexpressions(
    program: fx.Program, *, min_size: int = 5, min_count: int = 3, limit: int = 3
) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for node in fx.walk(program):
        if isinstance(node, fx.Call | fx.BinaryOp) and fx.size(node) >= min_size:
            counts[unparse(node)] = counts.get(unparse(node), 0) + 1
    repeated = [(text, count) for text, count in counts.items() if count >= min_count]
    repeated.sort(key=lambda item: (-item[1], -len(item[0])))
    return repeated[:limit]


def _repair(program: fx.Program, settings: ValidationSettings) -> fx.Program:
    """Apply the unambiguous fixes: legacy operator names and missing normalisation."""
    canonical = canonicalize(program)
    output = canonical.output
    if settings.require_normalisation and not _is_normalised(canonical):
        output = fx.Call(func="rank", args=(output,))
    return fx.Program(output=output)


def _closest_operator(name: str) -> str | None:
    from brainiac.fastexpr.operators import operator_names

    return _closest(name, operator_names())


def _closest_field(name: str, registry: FieldRegistry) -> str | None:
    return _closest(name, registry.known_ids())


def _closest(name: str, candidates: Iterable[str]) -> str | None:
    import difflib

    matches = difflib.get_close_matches(name, list(candidates), n=1, cutoff=0.78)
    return matches[0] if matches else None
