import sys
sys.path.insert(0, "src")
from jcua.evolve import bump_version, tighten_preview, promotion_check

def test_bump_version():
    assert bump_version("0.1.0") == "0.1.1"
    assert bump_version("1.2.9") == "1.2.10"
    assert bump_version("nope") is None

def test_tighten_preview_dry_run():
    p = tighten_preview("hello-jcua/0.1.0")
    assert p["next"] == "0.1.1" and p["writes"] is False
    assert tighten_preview("missing/0.0.0")["error"] == "not found"

def test_promotion_gate_sides():
    stats = {"a/0.1.0": {"ref": "a/0.1.0", "uses": 5, "wins": 5, "value": 0.7, "status": "candidate"},
             "b/0.1.0": {"ref": "b/0.1.0", "uses": 5, "wins": 5, "value": 0.5, "status": "candidate"}}
    ok, _ = promotion_check("a/0.1.0", stats, golden_ok=True)
    assert ok is True
    ok, reason = promotion_check("a/0.1.0", stats, golden_ok=False)
    assert ok is False and "golden" in reason
    thin = {"a/0.1.0": {"ref": "a/0.1.0", "uses": 1, "wins": 1, "value": 0.9, "status": "candidate"}}
    ok, reason = promotion_check("a/0.1.0", thin, golden_ok=True)
    assert ok is False and "uses" in reason
    weak = {"a/0.1.0": {"ref": "a/0.1.0", "uses": 5, "wins": 2, "value": 0.9, "status": "candidate"}}
    ok, reason = promotion_check("a/0.1.0", weak, golden_ok=True)
    assert ok is False and "sr" in reason
