"""Form-fill planner: elements + document entities -> ordered driver actions."""
import re

FIXED = ("check", "click", "skip")

def build_examples(task, form, elements, entities):
    out = []
    for el in elements:
        opts = [f"fill {e['label']}: {e['value']}" for e in entities] + list(FIXED)
        out.append({
            "context": f"TASK {task}\nFORM {form}\nELEMENT {el['role']} \"{el['label']}\" value=\"{el.get('value', '')}\"",
            "options": opts,
            "element": el,
        })
    return out

def _overlap(a, b):
    ta = set(re.findall(r"[a-z0-9]+", a.lower()))
    tb = set(re.findall(r"[a-z0-9]+", b.lower()))
    return len(ta & tb) / max(1, len(ta | tb))

def heuristic_pick(example):
    m = re.search(r'ELEMENT \S+ "(.*)" value=', example["context"])
    label = m.group(1) if m else ""
    fills = [o for o in example["options"] if o.startswith("fill ")]
    best = max(fills, key=lambda o: _overlap(label, o[5:].split(":")[0]))
    if _overlap(label, best[5:].split(":")[0]) <= 0:
        return "skip"
    return best

def order_actions(decided):
    fills = [d for d in decided if d["action"].startswith("fill ")]
    checks = [d for d in decided if d["action"] == "check"]
    clicks = [d for d in decided if d["action"] == "click"]
    plan = fills + checks + clicks[:1]
    return [p for p in plan if p["action"] != "skip"]

def decide(examples, scorer=None):
    decided = []
    for ex in examples:
        if scorer is None:
            action, mode, conf = heuristic_pick(ex), "heuristic", None
        else:
            action, conf = scorer(ex)
            mode = "s1-live"
        decided.append({"element": ex["element"]["label"], "action": action,
            "confidence": conf, "mode": mode})
    return order_actions(decided)

def s1_scorer(checkpoint, upstream):
    import torch
    import sys, os
    sys.path.insert(0, os.path.join(upstream, "libs", "cua-s1", "python", "src"))
    from cua_s1.model import load_checkpoint
    model, collator, _ = load_checkpoint(checkpoint, "cpu")
    def run(example):
        from cua_s1.model import validate_example
        ex = validate_example({"context": example["context"],
            "options": example["options"], "label": 0})
        batch = collator([ex])
        with torch.no_grad():
            logits = model(batch)
            logits[~batch["option_mask"]] = float("-inf")
            probs = torch.softmax(logits, dim=1)[0].tolist()
        i = max(range(len(probs)), key=lambda k: probs[k])
        return example["options"][i], round(probs[i], 4)
    return run
