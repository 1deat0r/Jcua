"""Retrieve-or-create scoring. Formula ported from jeva (weights 0.6/0.3/0.1, threshold 0.46)."""
import re
WEIGHTS = (0.6, 0.3, 0.1)
CREATE_THRESHOLD = 0.46

def score(cosine, value_norm, tag_match, weights=WEIGHTS):
    wc, wv, wt = weights
    c = 0.5 if cosine is None else max(0.0, min(1.0, cosine))
    v = 0.5 if value_norm is None else max(0.0, min(1.0, value_norm))
    return round(wc * c + wv * v + wt * (1.0 if tag_match else 0.0), 4)

def should_create(top_score, failures=0, threshold=CREATE_THRESHOLD):
    if failures and failures >= 2:
        return True, "top artifact failed twice"
    if top_score is None or top_score < threshold:
        return True, f"score {top_score} < {threshold}"
    return False, "reuse"

def _tokens(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))

def cosine_fallback(a, b):
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.5
    inter = len(ta & tb)
    j = inter / max(1, len(ta | tb))
    cov = inter / max(1, len(ta))
    jm = 2 * j / (1 + j) if j else 0.0
    return round(0.4 * (0.2 + 0.8 * jm) + 0.6 * cov, 4)

def guess_cluster(goal):
    g = (goal or "").lower()
    if any(k in g for k in ["click", "window", "desktop", "gui", "app ", "browser"]):
        return "desktop"
    if any(k in g for k in ["android", "phone", "mobile", "adb"]):
        return "mobile"
    if any(k in g for k in ["code", "bug", "pytest", "refactor", "test"]):
        return "coding"
    return "general"

RETRIEVABLE = ("candidate", "default", "pinned", "quarantine")

def rank(goal, artifacts, top_k=3):
    cluster = guess_cluster(goal)
    vals = [a.get("value_score", 0.5) for a in artifacts]
    vmin, vmax = (min(vals), max(vals)) if vals else (None, None)
    scored = []
    for a in artifacts:
        if a.get("status", "candidate") not in RETRIEVABLE:
            continue
        cos = cosine_fallback(goal, a.get("text", ""))
        vn = 0.5 if vmax is None or vmax <= vmin else max(0.0, min(1.0, (a.get("value_score", 0.5) - vmin) / (vmax - vmin + 1e-9)))
        trg = [t for t in (a.get("triggers", []) or []) if t.lower() in (goal or "").lower()]
        s = score(cos, vn, bool(trg)) + min(0.15, 0.075 * len(trg))
        if a.get("cluster") == cluster:
            s = round(s + 0.05, 4)
        scored.append((round(s, 4), a))
    scored.sort(key=lambda x: -x[0])
    return [{"score": s, "artifact": a} for s, a in scored[:top_k]]
