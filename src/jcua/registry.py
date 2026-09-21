"""Library registry — versioned skills/tools/workflows with file<->DB audit."""
import json, os, re, sqlite3
try:
    import yaml
    HAVE_YAML = True
except Exception:
    HAVE_YAML = False
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LIB = os.path.join(ROOT, "library")
DB = os.path.join(ROOT, "library.db")

def _frontmatter(path):
    txt = open(path).read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    if not m:
        return {}, txt
    fm = yaml.safe_load(m.group(1)) if HAVE_YAML else {}
    return fm or {}, m.group(2)

def load_skills():
    out, base = [], os.path.join(LIB, "skills")
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base)):
        ndir = os.path.join(base, name)
        if not os.path.isdir(ndir):
            continue
        for ver in sorted(os.listdir(ndir)):
            fp = os.path.join(ndir, ver, "SKILL.md")
            if not os.path.exists(fp):
                continue
            fm, body = _frontmatter(fp)
            out.append({"kind": "skill", "ref": f"{name}/{ver}",
                "name": fm.get("name", name), "version": fm.get("version", ver),
                "path": fp, "cluster": fm.get("cluster", "general"),
                "value_score": float(fm.get("value_score", 0.5)),
                "triggers": list(fm.get("triggers", []) or []),
                "status": fm.get("status", "candidate"),
                "text": (fm.get("name", name) + " " + body[:2000])})
    return out

def validate_skill(item):
    errors = []
    if not item.get("name"):
        errors.append("missing name")
    if not re.match(r"^\d+\.\d+\.\d+$", str(item.get("version", ""))):
        errors.append(f"bad version {item.get('version')}")
    if item.get("status") not in ("candidate", "default", "pinned", "quarantine", "draft", "archived"):
        errors.append(f"bad status {item.get('status')}")
    return errors

def _db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS stats(ref TEXT PRIMARY KEY, uses INT DEFAULT 0, wins INT DEFAULT 0, value REAL DEFAULT 0.5, status TEXT DEFAULT 'candidate')")
    con.execute("CREATE TABLE IF NOT EXISTS traces(id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, goal TEXT, ref TEXT, reused INT, reward REAL)")
    return con

def record_run(goal, ref, reused, reward):
    import time
    con = _db()
    con.execute("INSERT INTO traces(ts, goal, ref, reused, reward) VALUES(?,?,?,?,?)", (time.time(), goal, ref, int(reused), reward))
    con.execute("INSERT INTO stats(ref, uses, wins, value, status) VALUES(?,?,?,?,'candidate') ON CONFLICT(ref) DO UPDATE SET uses=uses+1, wins=wins+?, value=(value*uses+?)/(uses+1)",
        (ref, 1, int(reward >= 0.5), reward, int(reward >= 0.5), reward))
    con.commit()
    con.close()

def audit():
    files = {s["ref"]: s["status"] for s in load_skills()}
    con = _db()
    rows = {r[0]: r[1] for r in con.execute("SELECT ref, status FROM stats")}
    con.close()
    mismatches = [{"ref": r, "file": f, "db": rows.get(r, "absent")} for r, f in files.items() if rows.get(r, f) != f]
    orphans = [r for r in rows if r not in files]
    return {"checked": len(files), "mismatches": mismatches, "orphans": orphans,
        "audit": "pass" if not mismatches else "fail"}
