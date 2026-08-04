"""Measure structured-span normalization at representative gradient sizes.

Run with ``uv run --locked python benchmarks/span_normalization.py`` after an
editable build.  The script records timings for comparison, but deliberately
does not enforce machine-dependent timing thresholds.
"""

from __future__ import annotations

from time import perf_counter

from manimpango import TextSpan
from manimpango._spans import normalize_spans


def main() -> None:
    for count in (500, 1_000, 2_000, 4_000):
        text = "x" * count
        spans = tuple(
            TextSpan(start=index, end=index + 1, weight=700) for index in range(count)
        )
        started = perf_counter()
        runs = normalize_spans(spans, text)
        elapsed = perf_counter() - started
        assert runs == ({"start": 0, "end": count, "weight": 700},)
        print(f"{count:5d} spans: {elapsed:.6f} s")


if __name__ == "__main__":
    main()
