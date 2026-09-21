# Sandbox bench harness

Locked-down Docker benchmark (no network at run, no keys, capped CPU/RAM).

```bash
cd evals/bench
./stage.sh        # stage context (repo files + HF checkpoint), build image
./run.sh          # run sandboxed, prints JSON
```

`ctx/` is gitignored build staging. Checkpoint + config download from
HuggingFace at stage time (MIT).
