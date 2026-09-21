# S1 forms eval corpus (vendored)

`demo.jsonl`: 196 real rows (3 real form pages x 3 real demo PDFs), from
`cua-ai/cua-s1-forms` dataset (HuggingFace, 2026-09-18, MIT). Eval only —
never training material. Provenance: https://huggingface.co/datasets/cua-ai/cua-s1-forms
Model: https://huggingface.co/cua-ai/cua-s1-forms (706k params, 2.8MB, MIT).
Run: `python3 scripts/score_s1_demo.py --upstream <cua-checkout> [--n 196]`
(requires torch + safetensors; prints skip JSON without them so CI stays green).
