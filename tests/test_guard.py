import sys, os
sys.path.insert(0, "src")
import jcua.jev_gates as g

def _nonttransport(url, payload, key):
    raise AssertionError("network must not be touched")

def test_keyless_falls_back_without_network(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    v = g.guard_action("rm -rf /", enabled=True, transport=_nonttransport)
    assert v["verdict"] == "ESCALATE" and v["mode"] == "fallback"
    v = g.guard_action("list files in the current directory", enabled=True, transport=_nonttransport)
    assert v["verdict"] == "APPROVE" and v["mode"] == "fallback"

def test_transport_failure_falls_back(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
    def boom(url, payload, key):
        raise TimeoutError("down")
    v = g.guard_action("rm -rf /", enabled=True, transport=boom)
    assert v["verdict"] == "ESCALATE" and v["mode"] == "fallback"

def test_invalid_answer_falls_back(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
    bad = [
        {"choice": "MAYBE", "probabilities": {"safe_to_proceed": 0.5, "needs_human_review": 0.5}},
        {"choice": "safe_to_proceed", "probabilities": {"safe_to_proceed": 0.9, "needs_human_review": 0.9}},
        {"choice": "safety", "probabilities": {"safety": 1.0}},
        {"answer": "looks fine"},
    ]
    for raw in bad:
        v = g.guard_action("list files", enabled=True, transport=lambda u, p, k: raw)
        assert v["mode"] == "fallback", raw

def test_threshold_sides(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
    live = lambda c, p: (lambda u, pl, k: {"choice": c, "probabilities": {"safe_to_proceed": p if c == "safe_to_proceed" else 1 - p, "needs_human_review": p if c == "needs_human_review" else 1 - p}})
    v = g.guard_action("list files", enabled=True, floor=0.75, transport=live("safe_to_proceed", 0.9))
    assert v == {"verdict": "APPROVE", "confidence": 0.9, "mode": "live"}
    v = g.guard_action("list files", enabled=True, floor=0.75, transport=live("safe_to_proceed", 0.6))
    assert v["verdict"] == "ESCALATE" and v["mode"] == "live"
    v = g.guard_action("rm -rf /", enabled=True, floor=0.75, transport=live("needs_human_review", 0.99))
    assert v["verdict"] == "ESCALATE" and v["mode"] == "live"

def test_envelope_shape(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
    seen = {}
    def cap(url, payload, key):
        seen.update(payload)
        return {"choice": "safe_to_proceed", "probabilities": {"safe_to_proceed": 1.0, "needs_human_review": 0.0}}
    g.guard_action("list files", enabled=True, transport=cap)
    assert set(("state", "model", "questions")) <= set(seen)
    assert isinstance(seen["questions"], dict) and seen["questions"]
    for q in seen["questions"].values():
        assert q.get("type") in g.QUESTION_TYPES
        assert "criteria" not in q or isinstance(q["criteria"], dict)

def test_disabled_gate_approves_without_network(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    v = g.guard_action("rm -rf /", enabled=False, transport=_nonttransport)
    assert v["verdict"] == "APPROVE" and v["mode"] == "disabled"
