#!/bin/bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
python3 -c "import shutil; shutil.rmtree('$HERE/ctx', ignore_errors=True)"
mkdir -p "$HERE/ctx/jcua" "$HERE/ctx/cua-s1"
cp -r "$ROOT/src" "$ROOT/tests" "$ROOT/pyproject.toml" "$ROOT/jcua.config.yaml" "$ROOT/evals" "$ROOT/library" "$HERE/ctx/jcua/"
[ -d "$HERE/ctx/jcua/evals/bench/ctx" ] && python3 -c "import shutil; shutil.rmtree('$HERE/ctx/jcua/evals/bench/ctx', ignore_errors=True)"
CUA="${CUA_CHECKOUT:-$HOME/.cua/cbregistry}"
[ -d "$CUA/libs/cua-s1" ] || { echo "need cua checkout with libs/cua-s1 (CUA_CHECKOUT)"; exit 1; }
cp -r "$CUA/libs/cua-s1/python/src" "$HERE/ctx/cua-s1/"
cp "$ROOT/evals/s1-forms/demo.jsonl" "$HERE/ctx/demo.jsonl"
if [ ! -f "$HERE/ctx/checkpoint.safetensors" ]; then
  curl -sL -o "$HERE/ctx/checkpoint.safetensors" "https://huggingface.co/cua-ai/cua-s1-forms/resolve/main/cua-s1-forms.safetensors"
  curl -sL -o "$HERE/ctx/checkpoint.json" "https://huggingface.co/cua-ai/cua-s1-forms/resolve/main/cua-s1-forms.json"
fi
cp "$HERE/bench.py" "$HERE/Dockerfile" "$HERE/ctx/"
docker build -t jcua-bench "$HERE/ctx"
