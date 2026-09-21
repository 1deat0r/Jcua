"""Single shared Jev transport + destructive-action guard. Decider only — never generation."""
import json, os, re, urllib.request

BASE = "https://api.typesafe.ai"
ENDPOINT = "/v1/systemone"
TIMEOUT_S = 30
QUESTION_TYPES = ("choice", "noul", "score")
CRITERIA = {
    "safe_to_proceed": "the action is harmless, read-only, or fully reversible",
    "needs_human_review": "the action is destructive, irreversible, or privilege-escalating",
}
VERDICT = {"safe_to_proceed": "APPROVE", "needs_human_review": "ESCALATE"}

def _model():
    return os.environ.get("TYPESAFE_MODEL", "jev-latest")

def _key():
    return os.environ.get("TYPESAFE_API_KEY", "")

DESTRUCTIVE = re.compile(r"(rm\s+-[rf]+|del\s+/[fs]|format[\s:]|mkfs|dd\s+[^ ]*if=|drop\s+(table|database)|delete\s+from|shutdown|reboot|:\(\)\s*\{[^}]*\}\s*;|push\b.*--force|\bpublish\b|grant\b.*admin|chmod\s+-R\s+777)", re.I)

def fallback_verdict(action):
    return "ESCALATE" if DESTRUCTIVE.search(action or "") else "APPROVE"

def decide(state, questions, transport=None):
    key = _key()
    if not key:
        return {"ok": False, "error": "missing TYPESAFE_API_KEY"}
    payload = {"state": state, "model": _model(), "questions": questions}
    try:
        if transport is None:
            def transport(url, payload, key, _t=TIMEOUT_S):
                req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=_t) as r:
                    return json.load(r)
        return {"ok": True, "raw": transport(BASE + ENDPOINT, payload, key)}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__ + ": " + str(e)[:160]}

def _walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)

def _extract_choice(raw):
    ids = set(CRITERIA)
    for node in _walk(raw):
        if not isinstance(node, dict):
            continue
        choice = node.get("choice", node.get("id", node.get("option")))
        probs = node.get("probabilities", node.get("probs"))
        if isinstance(choice, dict):
            choice = choice.get("id", choice.get("choice"))
        if choice in ids and isinstance(probs, dict) and ids <= set(probs):
            try:
                vals = [float(probs[i]) for i in ids]
            except (TypeError, ValueError):
                continue
            if abs(sum(vals) - 1.0) > 0.02:
                continue
            if max(ids, key=lambda i: probs[i]) != choice:
                continue
            return choice, {i: probs[i] for i in ids}
    return None, {}

def guard_action(action, enabled=False, floor=0.75, transport=None):
    if not enabled:
        return {"verdict": "APPROVE", "confidence": None, "mode": "disabled"}
    state = f"Should the agent execute this action? Action: {action}"
    questions = {"approval": {"type": "choice",
        "options": ["APPROVE", "DENY"], "criteria": dict(CRITERIA)}}
    res = decide(state, questions, transport=transport)
    if not res.get("ok"):
        return {"verdict": fallback_verdict(action), "confidence": None, "mode": "fallback", "error": res.get("error")}
    choice, probs = _extract_choice(res["raw"])
    if choice is None:
        return {"verdict": fallback_verdict(action), "confidence": None, "mode": "fallback", "error": "invalid answer"}
    conf = probs[choice]
    verdict = VERDICT[choice]
    if verdict == "ESCALATE" or conf < floor:
        return {"verdict": "ESCALATE", "confidence": conf, "mode": "live"}
    return {"verdict": "APPROVE", "confidence": conf, "mode": "live"}

def load_jev_config():
    try:
        import yaml
        cfg = yaml.safe_load(open("jcua.config.yaml")) or {}
    except Exception:
        cfg = {}
    j = cfg.get("jev", {}) if isinstance(cfg, dict) else {}
    return bool(j.get("enabled", False)), float(j.get("confidence_floor", 0.75))
