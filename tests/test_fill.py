import json, sys
sys.path.insert(0, "src")
from jcua.fill import build_examples, decide, heuristic_pick, order_actions

def _fixture():
    return json.load(open("evals/s1-forms/fixture-northwind.json"))

def test_build_examples_shape():
    fx = _fixture()
    exs = build_examples(fx["task"], fx["form"], fx["elements"], fx["entities"])
    assert len(exs) == 3
    assert exs[0]["options"][-3:] == ["check", "click", "skip"]
    assert exs[0]["context"].startswith("TASK ")

def test_heuristic_picks_right_entities():
    fx = _fixture()
    exs = build_examples(fx["task"], fx["form"], fx["elements"], fx["entities"])
    picks = [heuristic_pick(e) for e in exs]
    assert picks[0] == "fill First name: Amara"
    assert picks[1] == "fill Phone number: (503) 555-0142"
    assert picks[2] == "fill City: Portland"

def test_order_fills_then_check_then_one_click():
    plan = order_actions([
        {"element": "a", "action": "click", "confidence": 1.0, "mode": "t"},
        {"element": "b", "action": "fill X: 1", "confidence": 1.0, "mode": "t"},
        {"element": "c", "action": "skip", "confidence": 1.0, "mode": "t"},
        {"element": "d", "action": "check", "confidence": 1.0, "mode": "t"},
    ])
    assert [p["action"] for p in plan] == ["fill X: 1", "check", "click"]

def test_decide_end_to_end_heuristic():
    fx = _fixture()
    exs = build_examples(fx["task"], fx["form"], fx["elements"], fx["entities"])
    plan = decide(exs)
    assert len(plan) == 3 and all(p["mode"] == "heuristic" for p in plan)

def test_s1_scorer_skips_without_torch():
    import sys
    saved = sys.modules.pop("torch", None)
    sys.modules["torch"] = None
    try:
        from jcua.fill import s1_scorer
        try:
            s1_scorer("/nonexistent", "/nonexistent")
            assert False, "should raise without torch"
        except Exception:
            assert True
    finally:
        if saved is not None:
            sys.modules["torch"] = saved
        else:
            sys.modules.pop("torch", None)
