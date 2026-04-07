def make_decision(anomaly_score: float, threshold: float) -> str:
    if anomaly_score >= threshold:
        return "Suspicious"
    return "Legitimate"
