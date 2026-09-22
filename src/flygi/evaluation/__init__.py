"""Paired analysis and reporting for matched ARC result bundles."""

from .paired_analysis import (
    PairedAnalysisError,
    PairedResult,
    censored_summary,
    compare,
    extract_metric,
    match_rows,
)

__all__ = [
    "PairedAnalysisError",
    "PairedResult",
    "censored_summary",
    "compare",
    "extract_metric",
    "match_rows",
]
