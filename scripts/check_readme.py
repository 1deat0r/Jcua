"""Fail when README managed block or layout drifts from source of truth. Fix with --write."""
import re, sys, pathlib, tomllib, subprocess

ROOT = pathlib.Path(".")
START, END = "<!-- JCUA-MANAGED-START -->", "<!-- JCUA-MANAGED-END -->"

def version():
    with open("pyproject.toml", "rb") as f:
        v = tomllib.load(f)["project"]["version"]
    try:
        tag = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True).stdout.strip()
    except Exception:
        tag = ""
    if not tag:
        m = re.search(re.escape(START) + r"\n> Version `[^`]+` · latest tag `([^`]+)`", pathlib.Path("README.md").read_text())
        tag = m.group(1) if m else ""
    return v, tag

def managed_block(v, tag):
    return (f"{START}\n> Version `{v}` · latest tag `{tag or 'none'}` · "
            f"[Releases](https://github.com/1deat0r/Jcua/releases) · "
            f"[Changelog](CHANGELOG.md) · [Roadmap](ROADMAP.md) · "
            f"[Milestones](https://github.com/1deat0r/Jcua/milestones) · "
            f"![ci](https://github.com/1deat0r/Jcua/actions/workflows/ci.yml/badge.svg)\n{END}")

def check_layout(readme):
    want = ["src/jcua/", "platforms/", "library/", "memory/", "traces/", "evals/", "docs/", "scripts/"]
    missing = [d for d in want if d not in readme]
    return missing

def main():
    v, tag = version()
    readme_p = ROOT / "README.md"
    readme = readme_p.read_text()
    errors = []
    if f"## {v}" not in pathlib.Path("CHANGELOG.md").read_text() and v not in pathlib.Path("CHANGELOG.md").read_text():
        errors.append(f"CHANGELOG has no entry mentioning {v}")
    if tag and tag != f"v{v}":
        errors.append(f"latest tag {tag} != pyproject v{v} (tag the release)")
    m = managed_block(v, tag)
    if m not in readme:
        errors.append("managed block stale (run: python3 scripts/check_readme.py --write)")
    ml = check_layout(readme)
    if ml:
        errors.append(f"README layout missing: {ml}")
    if "--write" in sys.argv:
        if START in readme and END in readme:
            readme = re.sub(re.escape(START) + r".*?" + re.escape(END), m, readme, flags=re.S)
        else:
            readme = readme.replace("# Jcua", "# Jcua\n\n" + m, 1)
        readme_p.write_text(readme)
        print("README managed block rewritten")
        return
    if errors:
        print("README stale:"); [print(" -", e) for e in errors]; sys.exit(1)
    print(f"README ok (v{v} {tag})")

main()
