"""Fail if likely secret material is staged for commit."""
import re, sys, pathlib
roots = ["src", "platforms", "evals", "docs", "scripts", "library", "memory"]
pat = re.compile(r"(TYPESAFE_API_KEY\s*=\s*['\"][^'\"]+|sk-ant-|sk-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]+|cookies\.json)", re.I)
bad = []
for r in roots:
    for p in pathlib.Path(r).rglob("*"):
        if p.name == "check_no_secrets.py":
            continue
        if p.is_file() and p.suffix in (".py", ".md", ".yaml", ".yml", ".json", ".sh"):
            try: t = p.read_text(errors="ignore")
            except Exception: continue
            if pat.search(t): bad.append(str(p))
if bad:
    print("possible secrets in:", *bad); sys.exit(1)
print("secrets-check ok")
