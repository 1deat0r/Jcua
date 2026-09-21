"""Evolution: dry-run mutate preview + promotion gate. Mutations need --apply."""
import os, re, sqlite3
from .registry import ROOT, load_skills, _db

def bump_version(ver):
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", str(ver))
    if not m:
        return None
    major, minor, patch = map(int, m.groups())
    return f"{major}.{minor}.{patch + 1}"

def tighten_preview(ref):
    for s in load_skills():
        if s["ref"] == ref:
            body = open(s["path"]).read()
            tight = re.sub(r"[ \t]+(\n|\r)", r"\1", body).strip() + "\n"
            saved = len(body) - len(tight)
            return {"ref": ref, "next": bump_version(s["version"]),
                "bytes_saved": saved, "writes": False}
    return {"ref": ref, "error": "not found"}

def _stats():
    con = sqlite3.connect(os.path.join(ROOT, "library.db"))
    try:
        rows = con.execute("SELECT ref, uses, wins, value, status FROM stats").fetchall()
    except Exception:
        rows = []
    con.close()
    return [{"ref": r[0], "uses": r[1], "wins": r[2], "value": r[3], "status": r[4]} for r in rows]

def promotion_check(ref, stats=None, values=None, golden_ok=None):
    from .golden import golden_gate
    stats = stats if stats is not None else {s["ref"]: s for s in _stats()}
    s = stats.get(ref)
    if not s:
        return False, "no stats yet"
    if s["uses"] < 3:
        return False, f"uses {s['uses']} < 3"
    sr = s["wins"] / max(1, s["uses"])
    if sr < 0.8:
        return False, f"sr {sr:.2f} < 0.8"
    med = sorted(values if values is not None else [x["value"] for x in stats.values()])
    med = med[len(med) // 2] if med else 0.5
    if s["value"] < med:
        return False, f"value {s['value']} < median {med}"
    if golden_ok if golden_ok is not None else golden_gate():
        return True, "gate pass"
    return False, "golden gate fail"

def set_status(ref, status):
    from .registry import load_skills
    target = [s for s in load_skills() if s["ref"] == ref]
    if not target:
        return False
    fp = target[0]["path"]
    txt = open(fp).read()
    txt2 = re.sub(r"^status:\s*\S+", f"status: {status}", txt, count=1, flags=re.M)
    open(fp, "w").write(txt2)
    con = _db()
    con.execute("UPDATE stats SET status=? WHERE ref=?", (status, ref))
    con.commit()
    con.close()
    return True

def evolve_once(apply=False):
    from .registry import load_skills
    skills = [s for s in load_skills() if s["status"] == "candidate"]
    stats = {s["ref"]: s for s in _stats()}
    ranked = sorted(skills, key=lambda s: stats.get(s["ref"], {}).get("value", 0), reverse=True)
    if not ranked:
        return {"action": "none", "reason": "no candidates"}
    top = ranked[0]
    ok, reason = promotion_check(top["ref"], stats)
    plan = {"action": "promote", "ref": top["ref"], "gate": reason, "writes": False}
    if ok and apply:
        set_status(top["ref"], "default")
        plan["writes"] = True
    return plan
