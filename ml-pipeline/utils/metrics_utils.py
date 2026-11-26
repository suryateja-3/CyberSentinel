"""
utils/metrics_utils.py
======================
Shared reporting helpers: classification report, confusion matrix,
and plain-text report saving.

All functions print to stdout AND save to a text file in reports/.
"""

from __future__ import annotations

import datetime
import textwrap
from pathlib import Path
from typing import Any, List, Optional, Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from utils.data_utils import REPORTS_DIR


# ---------------------------------------------------------------------------
# Confusion matrix pretty-printer (no external plot library required)
# ---------------------------------------------------------------------------

def _fmt_confusion_matrix(
    cm: np.ndarray,
    class_names: Sequence[str],
) -> str:
    """Return a plain-text confusion matrix suitable for terminal / file."""
    n = len(class_names)
    max_name = max(len(c) for c in class_names)
    col_w = max(max_name, 8)

    # Header
    header_pad = " " * (max_name + 4)
    header = header_pad + "  PREDICTED\n"
    header += header_pad + "  " + "  ".join(f"{c:>{col_w}}" for c in class_names) + "\n"
    header += header_pad + "  " + "-" * (col_w * n + 2 * (n - 1)) + "\n"

    # Rows
    rows = ""
    for i, row_name in enumerate(class_names):
        prefix = f"  {row_name:>{max_name}} |  " if i == n // 2 else " " * (max_name + 4) + "|  "
        if i == 0:
            prefix = f"A {row_name:>{max_name}} |  "
        rows += prefix + "  ".join(f"{cm[i, j]:>{col_w}d}" for j in range(n)) + "\n"

    # Legend
    legend = (
        "\n  Rows = Actual class | Columns = Predicted class\n"
        "  TP/TN on diagonal, FP/FN off diagonal\n"
    )
    return header + rows + legend


# ---------------------------------------------------------------------------
# Main reporting function
# ---------------------------------------------------------------------------

def full_report(
    model_name: str,
    y_true: Any,
    y_pred: Any,
    class_names: List[str],
    extra_notes: str = "",
    seed: int = 42,
) -> str:
    """
    Compute and return a full text report including:
      - Overall accuracy
      - Precision / Recall / F1 per class (macro & weighted)
      - Confusion matrix

    Also saves the report to reports/<model_name>_metrics.txt.

    Parameters
    ----------
    model_name : str
        Short identifier used for the filename (e.g. 'fake_news').
    y_true : array-like
        Ground-truth labels (integers or strings matching class_names).
    y_pred : array-like
        Model predictions.
    class_names : list[str]
        Human-readable names for each class, in label order.
    extra_notes : str
        Any extra text to append at the bottom of the report.
    seed : int
        Random seed used — recorded for reproducibility.

    Returns
    -------
    str
        The full report text.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    acc = accuracy_score(y_true, y_pred)
    clf_report = classification_report(
        y_true, y_pred,
        target_names=class_names,
        digits=4,
        zero_division=0,
    )
    cm = confusion_matrix(y_true, y_pred)
    cm_text = _fmt_confusion_matrix(cm, class_names)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = textwrap.dedent(f"""
    {'='*70}
    MODEL: {model_name}
    Generated : {timestamp}
    Seed      : {seed}
    Test size : {len(y_true):,} samples
    {'='*70}

    OVERALL ACCURACY: {acc:.4f} ({acc*100:.2f}%)

    CLASSIFICATION REPORT
    ---------------------
    {clf_report}

    CONFUSION MATRIX
    ----------------
    {cm_text}
    """).strip()

    if extra_notes:
        report += f"\n\nNOTES\n-----\n{extra_notes}\n"

    report += "\n" + "=" * 70 + "\n"

    # Print to console
    print(report)

    # Save to file
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"{model_name}_metrics.txt"
    out_path.write_text(report, encoding="utf-8")
    print(f"  [saved] {out_path}")

    return report
