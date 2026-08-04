"""Structured-text span declarations and safe Python-side validation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Mapping, Sequence

from .enums import Style, Weight


@dataclass(frozen=True, slots=True)
class TextSpan:
    """Attributes applied to the half-open code-point range ``[start, end)``."""

    start: int
    end: int
    font: str | None = None
    size: float | None = None
    weight: Weight | int | None = None
    style: Style | None = None
    foreground: str | None = None
    features: Mapping[str, int | bool] | None = None
    variations: Mapping[str, float] | None = None


def _require_finite_number(value: object, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    converted = float(value)
    if positive and converted <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return converted


def _validate_tag(tag: object, name: str) -> str:
    if not isinstance(tag, str) or len(tag) != 4 or not tag.isascii():
        raise ValueError(f"{name} keys must be four-character ASCII OpenType tags")
    return tag


def _validate_weight(weight: object, name: str) -> None:
    if isinstance(weight, bool) or not isinstance(weight, int) or not 1 <= weight <= 1000:
        raise ValueError(f"{name} must be an integer between 1 and 1000")


def validate_variations(variations: Mapping[str, float] | None, name: str = "variations") -> None:
    if variations is None:
        return
    if not isinstance(variations, Mapping):
        raise TypeError(f"{name} must be a mapping or None")
    for tag, value in variations.items():
        _validate_tag(tag, name)
        _require_finite_number(value, f"{name}[{tag!r}]")


def validate_spans(spans: Sequence[TextSpan], text: str) -> tuple[TextSpan, ...]:
    """Validate span-local values and bounds without invoking native code.

    Attribute overlap normalization deliberately stays out of this initial
    bridge: the native renderer does not yet accept attributes.
    """
    if isinstance(spans, (str, bytes)) or not isinstance(spans, Sequence):
        raise TypeError("spans must be a sequence of TextSpan instances")
    validated = tuple(spans)
    for span in validated:
        if not isinstance(span, TextSpan):
            raise TypeError("spans must contain only TextSpan instances")
        if isinstance(span.start, bool) or not isinstance(span.start, int):
            raise TypeError("TextSpan.start must be an integer")
        if isinstance(span.end, bool) or not isinstance(span.end, int):
            raise TypeError("TextSpan.end must be an integer")
        if not 0 <= span.start <= span.end <= len(text):
            raise ValueError("TextSpan bounds must satisfy 0 <= start <= end <= len(text)")
        if span.font is not None and not isinstance(span.font, str):
            raise TypeError("TextSpan.font must be a string or None")
        if span.size is not None:
            _require_finite_number(span.size, "TextSpan.size", positive=True)
        if span.weight is not None:
            _validate_weight(span.weight, "TextSpan.weight")
        if span.style is not None and not isinstance(span.style, Style):
            raise TypeError("TextSpan.style must be a Style or None")
        if span.foreground is not None and not isinstance(span.foreground, str):
            raise TypeError("TextSpan.foreground must be a string or None")
        if span.features is not None:
            if not isinstance(span.features, Mapping):
                raise TypeError("TextSpan.features must be a mapping or None")
            for tag, value in span.features.items():
                _validate_tag(tag, "TextSpan.features")
                if not isinstance(value, (int, bool)):
                    raise TypeError("TextSpan feature values must be integers or bools")
        validate_variations(span.variations, "TextSpan.variations")
    _validate_overlap_conflicts(validated)
    return validated


def normalize_spans(spans: Sequence[TextSpan], text: str) -> tuple[dict[str, object], ...]:
    """Return compact, native-ready effective runs for ``spans``.

    Each result dictionary has byte-based ``start`` and ``end`` keys plus only
    the attributes active in that half-open range.  Runs are sorted,
    non-overlapping, and adjacent equivalent runs are combined.  Callers pass
    this representation directly to the Cython rendering boundary.
    """
    validated = validate_spans(spans, text)
    if not validated:
        return ()

    byte_offsets = _utf8_byte_offsets(text)
    boundaries = sorted({boundary for span in validated for boundary in (span.start, span.end)})
    normalized: list[dict[str, object]] = []
    for start, end in zip(boundaries, boundaries[1:]):
        attributes = _effective_attributes(validated, start, end)
        if not attributes:
            continue
        run = {"start": byte_offsets[start], "end": byte_offsets[end], **attributes}
        if (
            normalized
            and normalized[-1]["end"] == run["start"]
            and _run_attributes(normalized[-1]) == attributes
        ):
            normalized[-1]["end"] = run["end"]
        else:
            normalized.append(run)
    return tuple(normalized)


def _utf8_byte_offsets(text: str) -> tuple[int, ...]:
    """Map each Python code-point boundary in ``text`` to a UTF-8 byte index."""
    offsets = [0]
    total = 0
    for character in text:
        total += len(character.encode("utf-8"))
        offsets.append(total)
    return tuple(offsets)


def _effective_attributes(
    spans: tuple[TextSpan, ...], start: int, end: int
) -> dict[str, object]:
    active = [span for span in spans if span.start <= start and span.end >= end]
    attributes: dict[str, object] = {}
    for name in ("font", "size", "weight", "style", "foreground"):
        values = [getattr(span, name) for span in active if getattr(span, name) is not None]
        if values:
            attributes[name] = values[0]
    for name in ("features", "variations"):
        values: dict[str, object] = {}
        for span in active:
            mapping = getattr(span, name)
            if mapping:
                values.update(mapping)
        if values:
            attributes[name] = dict(sorted(values.items()))
    return attributes


def _run_attributes(run: Mapping[str, object]) -> dict[str, object]:
    return {key: value for key, value in run.items() if key not in {"start", "end"}}


def _validate_overlap_conflicts(spans: tuple[TextSpan, ...]) -> None:
    """Reject ambiguous overlapping values without imposing span order."""
    scalar_attributes = ("font", "size", "weight", "style", "foreground")
    for index, left in enumerate(spans):
        for right in spans[index + 1 :]:
            if max(left.start, right.start) >= min(left.end, right.end):
                continue
            for attribute in scalar_attributes:
                left_value = getattr(left, attribute)
                right_value = getattr(right, attribute)
                if (
                    left_value is not None
                    and right_value is not None
                    and left_value != right_value
                ):
                    raise ValueError(
                        f"conflicting overlapping TextSpan {attribute} values"
                    )
            for attribute in ("features", "variations"):
                left_values = getattr(left, attribute) or {}
                right_values = getattr(right, attribute) or {}
                for tag in left_values.keys() & right_values.keys():
                    if left_values[tag] != right_values[tag]:
                        raise ValueError(
                            f"conflicting overlapping TextSpan {attribute} value for {tag!r}"
                        )
