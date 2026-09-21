"""jcua CLI: run (retrieve-or-create) / library list|audit / eval --golden."""
import argparse, json, os, time

def cmd_run(a):
    from .retriever import rank, should_create
    from .registry import load_skills, record_run
    skills = load_skills()
    ranked = rank(a.task, skills)
    top = ranked[0] if ranked else None
    create, reason = should_create(top["score"] if top else None)
    ref = top["artifact"]["ref"] if (top and not create) else "draft:new"
    line = {"ts": time.time(), "goal": a.task, "target": a.target,
        "ref": ref, "reused": bool(top and not create), "reason": reason}
    os.makedirs("traces", exist_ok=True)
    open("traces/trace.jsonl", "a").write(json.dumps(line) + "\n")
    record_run(a.task, ref, line["reused"], 0.64 if line["reused"] else 0.5)
    print(json.dumps({"reused": line["reused"], "ref": ref, "reason": reason}))

def cmd_library(a):
    from .registry import load_skills, validate_skill, audit
    if a.action == "audit":
        print(json.dumps(audit()))
        return
    for s in load_skills():
        errs = validate_skill(s)
        print(f"{s['ref']} [{s['status']}] cluster={s['cluster']} value={s['value_score']}" + (f" ERR:{errs}" if errs else ""))

def cmd_eval(a):
    from .golden import run_all, golden_gate
    results = run_all()
    for r in results:
        print(f"{r['name']}: {'PASS' if r['ok'] else 'FAIL'} ({r['detail']})")
    print(json.dumps({"passed": sum(1 for r in results if r['ok']), "total": len(results), "gate": "pass" if golden_gate(results) else "fail"}))

def main():
    p = argparse.ArgumentParser(prog="jcua")
    s = p.add_subparsers(dest="c", required=True)
    r = s.add_parser("run"); r.add_argument("task"); r.add_argument("--budget", default="0.50"); r.add_argument("--target", default="linux"); r.set_defaults(f=cmd_run)
    l = s.add_parser("library"); l.add_argument("action", nargs="?", default="list"); l.set_defaults(f=cmd_library)
    e = s.add_parser("eval"); e.add_argument("--golden", action="store_true"); e.set_defaults(f=cmd_eval)
    a = p.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
