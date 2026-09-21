"""Sandboxed jcua-vs-cua offline benchmark. No network, no keys. Prints JSON + table."""
import json, subprocess, sys, time

OUT = {}
def stage(name, fn):
    t0 = time.time()
    try:
        OUT[name] = {"ok": True, "result": fn()}
    except Exception as e:
        OUT[name] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:200]}
    OUT[name]["seconds"] = round(time.time() - t0, 2)

def jcua_pytest():
    r = subprocess.run([sys.executable, "-m", "pytest", "/bench/jcua/tests/", "-q"],
        capture_output=True, text=True, cwd="/bench/jcua")
    last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l]
    return {"summary": last[-1] if last else r.stdout[-200:], "rc": r.returncode}

def jcua_golden():
    import os
    os.chdir("/bench/jcua")
    sys.path.insert(0, "/bench/jcua/src")
    from jcua.golden import run_all, golden_gate
    res = run_all()
    return {"passed": sum(1 for r in res if r["ok"]), "total": len(res),
        "gate": "pass" if golden_gate(res) else "fail"}

def jcua_retrieval_latency():
    sys.path.insert(0, "/bench/jcua/src")
    from jcua.retriever import rank
    from jcua.registry import load_skills
    skills = load_skills()
    goals = ["capture the linux desktop and click element", "open android settings",
             "run the test suite", "fill the patient form", "list files here"]
    t0 = time.time()
    for _ in range(40):
        for gl in goals:
            rank(gl, skills)
    dt = (time.time() - t0) / 200
    top = rank(goals[0], skills)[0]
    return {"ms_per_rank": round(dt * 1000, 3), "top_ref": top["artifact"]["ref"],
        "top_score": top["score"]}

def jcua_guard_fallback():
    sys.path.insert(0, "/bench/jcua/src")
    import os
    os.environ.pop("TYPESAFE_API_KEY", None)
    from jcua.jev_gates import guard_action
    t0 = time.time()
    v1 = guard_action("list files in the current directory", enabled=True)
    v2 = guard_action("rm -rf /", enabled=True)
    dt = (time.time() - t0) / 2
    return {"harmless": v1["verdict"], "dangerous": v2["verdict"],
        "modes": [v1["mode"], v2["mode"]], "ms_per_guard": round(dt * 1000, 3)}

def cua_s1_demo():
    import torch
    from cua_s1.model import load_checkpoint, validate_example
    rows = [json.loads(l) for l in open("/bench/demo.jsonl")]
    model, collator, _ = load_checkpoint("/bench/checkpoint.safetensors", "cpu")
    examples = [validate_example(r) for r in rows]
    t0, correct, bs = time.time(), 0, 32
    with torch.no_grad():
        for i in range(0, len(examples), bs):
            batch = collator(examples[i:i + bs])
            logits = model(batch)
            logits[~batch["option_mask"]] = float("-inf")
            for e, p in zip(examples[i:i + bs], logits.argmax(dim=1).tolist()):
                correct += (p == e.label)
    dt = time.time() - t0
    return {"n": len(examples), "top1": round(correct / len(examples), 4),
        "ms_per_element": round(dt / len(examples) * 1000, 2),
        "params": sum(p.numel() for p in model.parameters())}

stage("jcua_pytest", jcua_pytest)
stage("jcua_golden", jcua_golden)
stage("jcua_retrieval_latency", jcua_retrieval_latency)
stage("jcua_guard_fallback", jcua_guard_fallback)
stage("cua_s1_demo", cua_s1_demo)
print(json.dumps(OUT, indent=1))
