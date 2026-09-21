"""Sync GitHub repo description/homepage/topics from .github/repo-meta.yaml. Source of truth, never the web UI."""
import json, subprocess, sys, pathlib
try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: pip install pyyaml")
REPO = "1deat0r/Jcua"
meta = yaml.safe_load(pathlib.Path(".github/repo-meta.yaml").read_text())
want = {"description": meta["description"], "homepage": meta.get("homepage") or ""}
live = json.loads(subprocess.run(["gh", "api", f"repos/{REPO}", "--jq", "{description,homepage}"],
    capture_output=True, text=True, check=True).stdout)
live_topics = json.loads(subprocess.run(["gh", "api", f"repos/{REPO}/topics", "--jq", ".names"],
    capture_output=True, text=True, check=True).stdout)
drift = {k: (live.get(k) or "", want[k]) for k in ("description", "homepage") if (live.get(k) or "") != want[k]}
topics_drift = sorted(live_topics or []) != sorted(meta.get("topics", []))
if "--check" in sys.argv:
    if drift or topics_drift:
        print("repo-meta drift:", drift, "topics:", live_topics, "want:", meta.get("topics")); sys.exit(1)
    print("repo-meta ok"); sys.exit(0)
if drift:
    subprocess.run(["gh", "api", f"repos/{REPO}", "-X", "PATCH", "-f", f"description={want['description']}",
        "-f", f"homepage={want['homepage']}"], check=True)
    print("updated:", list(drift))
else:
    print("description/homepage ok")
if topics_drift:
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"names": meta.get("topics", [])}, f)
        tmp = f.name
    subprocess.run(["gh", "api", f"repos/{REPO}/topics", "-X", "PUT", "--input", tmp], check=True)
    print("topics updated")
else:
    print("topics ok")
