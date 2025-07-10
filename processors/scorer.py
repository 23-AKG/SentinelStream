def calculate_risk_score(iocs: dict) -> int:
    score = 0
    score += len(iocs.get("ipv4", [])) * 2
    score += len(iocs.get("url", [])) * 3
    score += len(iocs.get("hash", [])) * 1

    return min(score, 10)  # clamp between 0 and 10
