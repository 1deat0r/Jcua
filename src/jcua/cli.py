"""jcua CLI skeleton."""
import argparse, json, time

def cmd_run(a):
    print(f"[jcua] target={a.target} budget=${a.budget} task: {a.task}")
    print("[jcua] skeleton: wire Computer + jev_gates + traces/trace.jsonl here.")

def cmd_list(a):
    print("[jcua] library list (skeleton — connect library.db next)")

def cmd_eval(a):
    print("[jcua] eval --golden (skeleton — add golden tasks in evals/golden/)")

def main():
    p = argparse.ArgumentParser(prog="jcua")
    s = p.add_subparsers(dest="c", required=True)
    r = s.add_parser("run"); r.add_argument("task"); r.add_argument("--budget", default="0.50"); r.add_argument("--target", default="linux"); r.set_defaults(f=cmd_run)
    l = s.add_parser("library"); l.add_argument("rest", nargs="*"); l.set_defaults(f=cmd_list)
    e = s.add_parser("eval"); e.add_argument("--golden", action="store_true"); e.set_defaults(f=cmd_eval)
    a = p.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
