import sys, pathlib
sys.path.insert(0, "src")
from jcua.retriever import score, should_create, cosine_fallback, rank

def test_score_weights():
    assert score(1.0, 1.0, True) == round(0.6 + 0.3 + 0.1, 4)
    assert score(None, None, False) == round(0.6 * 0.5 + 0.3 * 0.5, 4)

def test_should_create_threshold():
    c, _ = should_create(0.9)
    assert c is False
    c, _ = should_create(0.1)
    assert c is True
    c, _ = should_create(None)
    assert c is True

def test_rank_prefers_trigger_match():
    arts = [
        {"ref": "a/0.1.0", "text": "unrelated weather", "status": "candidate", "cluster": "general", "value_score": 0.5, "triggers": []},
        {"ref": "b/0.1.0", "text": "capture desktop click element", "status": "candidate", "cluster": "desktop", "value_score": 0.5, "triggers": ["capture"]},
    ]
    top = rank("capture the desktop", arts, top_k=2)
    assert top[0]["artifact"]["ref"] == "b/0.1.0"

def test_registry_loads_seed():
    from jcua.registry import load_skills, validate_skill
    skills = load_skills()
    assert any(s["ref"] == "hello-jcua/0.1.0" for s in skills)
    assert all(validate_skill(s) == [] for s in skills)

def test_golden_gate():
    from jcua.golden import run_all, golden_gate
    results = run_all()
    assert len(results) == 3
    assert golden_gate(results) is True
