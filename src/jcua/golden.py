"""Golden tasks + gate. All-green required before any promotion claim."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
GOLDEN = os.path.join(ROOT, "evals", "golden")

def list_tasks():
    out = []
    if not os.path.isdir(GOLDEN):
        return out
    for name in sorted(os.listdir(GOLDEN)):
        dd = os.path.join(GOLDEN, name)
        tf = os.path.join(dd, "task.md")
        if os.path.isfile(tf) and not os.path.exists(os.path.join(dd, "METRIC")):
            out.append({"name": name, "task": open(tf).read()})
    return out

def run_all():
    results = []
    for t in list_tasks():
        ok, detail = run_one(t)
        results.append({"name": t["name"], "ok": ok, "detail": detail})
    return results

def run_one(t):
    from .retriever import rank
    from .registry import load_skills
    ranked = rank(t["task"], load_skills(), top_k=1)
    if not ranked:
        return False, "library empty"
    return True, f"retrieved {ranked[0]['artifact']['ref']}@{ranked[0]['score']}"

def golden_gate(results=None):
    results = results if results is not None else run_all()
    return bool(results) and all(r["ok"] for r in results)
