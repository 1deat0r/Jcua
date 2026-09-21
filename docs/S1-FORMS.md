# S1 forms — offline decider eval

Upstream: `cua-ai/cua-s1-forms` model + dataset (HuggingFace, 2026-09-18, MIT, 84 likes).
Generator + training code: `libs/cua-s1` in trycua/cua (covered by `scripts/sync-upstream.sh`).

## Verdict: useful, with a role

- Offline form-filling decider (706k params, ~3MB) behind cua-driver duty: no key,
  no latency, CPU-runnable, small enough for Android later.
- `demo.jsonl` (196 real rows) is Jcua's first real-transfer form metric.
- Recipe (synthetic episodes + confuser pairs + disjoint splits) is the template for
  Jcua's own future deciders.

## Local benchmark (this machine, CPU)

| corpus | n | top-1 | ms/element |
| --- | --- | --- | --- |
| `evals/s1-forms/demo.jsonl` | 196 | 1.0 (196/196) | 6.7 |

Run: `python3 scripts/score_s1_demo.py --upstream <cua-checkout> [--n 196]`
(`jcua eval --s1`). Skips cleanly without torch (CI-safe); the retrieval
`golden_gate()` stays the promotion criterion until the S1 number is reproduced here.

## Integration plan

- 0.1.3: vendored corpus + scorer + this doc (no torch in CI).
- 0.1.5: `src/jcua/fill.py` plans fills from elements + entities (heuristic fallback),
  `jcua fill --s1` scores with the checkpoint (fixture 3/3 @~1.0 live, heuristic 3/3).
- Later: ONNX export for dependency-free inference; `set_value`/`click` dispatch into
  `platforms/linux` via cua-driver; synth-recipe reuse for non-form tasks.
