from __future__ import annotations

import numpy as np
from sklearn.metrics import confusion_matrix, roc_auc_score


def compute_far_frr_auc(y_true: list[int], y_pred: list[int], y_scores: list[float]) -> dict[str, float | None]:
    if len(y_true) == 0:
        return {"far": None, "frr": None, "auc": None}

    labels = [0, 1]
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=labels).ravel()

    far = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    frr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    auc = None
    unique_labels = np.unique(np.array(y_true))
    if len(unique_labels) > 1:
        auc = float(roc_auc_score(y_true, y_scores))

    return {"far": far, "frr": frr, "auc": auc}
