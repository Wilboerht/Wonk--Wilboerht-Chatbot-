from typing import List, Tuple

def apply_threshold(candidates: List[Tuple[int, float]], high: float = 0.8, low: float = 0.5):
    """
    根据阈值将候选划分为高/中/低置信度。
    返回：(best_score, level) 其中 level in {"high", "mid", "low", "none"}
    """
    if not candidates:
        return 0.0, "none"
    best_score = candidates[0][1]
    if best_score >= high:
        return best_score, "high"
    if best_score >= low:
        return best_score, "mid"
    return best_score, "low"

