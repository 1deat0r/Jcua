"""jcua CLI: run (retrieve-or-create) / library list|audit / eval --golden."""
import argparse, json, os, time

def cmd_guard(a):
    from .jev_gates import guard_action, load_jev_config
    _, floor = load_jev_config()
    print(json.dumps(guard_action(a.action, enabled=True, floor=a.floor or floor)))

def cmd_run(a):
    from .retriever import rank, should_create
    from .registry import load_skills, record_run
    from .jev_gates import guard_action, load_jev_config
    enabled, floor = load_jev_config()
    verdict = guard_action(a.task, enabled=enabled, floor=floor)
    if verdict["verdict"] == "ESCALATE" and not a.force:
        line = {"ts": time.time(), "goal": a.task, "target": a.target,
            "ref": "blocked:escalated", "reused": False, "guard": verdict}
        os.makedirs("traces", exist_ok=True)
        open("traces/trace.jsonl", "a").write(json.dumps(line) + "\n")
        print(json.dumps({"blocked": True, "guard": verdict, "hint": "re-run with --force to override"}))
        raise SystemExit(2)
    skills = load_skills()
    ranked = rank(a.task, skills)
    top = ranked[0] if ranked else None
    create, reason = should_create(top["score"] if top else None)
    ref = top["artifact"]["ref"] if (top and not create) else "draft:new"
    line = {"ts": time.time(), "goal": a.task, "target": a.target,
        "ref": ref, "reused": bool(top and not create), "reason": reason,
        "guard": verdict, "forced": bool(a.force)}
    os.makedirs("traces", exist_ok=True)
    open("traces/trace.jsonl", "a").write(json.dumps(line) + "\n")
    record_run(a.task, ref, line["reused"], 0.64 if line["reused"] else 0.5)
    print(json.dumps({"reused": line["reused"], "ref": ref, "reason": reason}))

def cmd_evolve(a):
    from .evolve import evolve_once, tighten_preview
    from .registry import load_skills
    if not a.once:
        print(json.dumps({"hint": "usage: jcua evolve --once [--apply]"}))
        return
    plan = evolve_once(apply=a.apply)
    print(json.dumps(plan))
    if a.apply and plan.get("ref"):
        print(json.dumps(tighten_preview(plan["ref"])))

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
    r = s.add_parser("run"); r.add_argument("task"); r.add_argument("--budget", default="0.50"); r.add_argument("--target", default="linux"); r.add_argument("--force", action="store_true"); r.set_defaults(f=cmd_run)
    gd = s.add_parser("guard"); gd.add_argument("action"); gd.add_argument("--floor", type=float, default=None); gd.set_defaults(f=cmd_guard)
    ev = s.add_parser("evolve"); ev.add_argument("--once", action="store_true"); ev.add_argument("--apply", action="store_true"); ev.set_defaults(f=cmd_evolve)
    l = s.add_parser("library"); l.add_argument("action", nargs="?", default="list"); l.set_defaults(f=cmd_library)
    e = s.add_parser("eval"); e.add_argument("--golden", action="store_true"); e.set_defaults(f=cmd_eval)
    a = p.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
