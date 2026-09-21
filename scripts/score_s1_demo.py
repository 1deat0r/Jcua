"""Score cua-s1-forms checkpoint on vendored demo.jsonl. Skips cleanly without torch/upstream (CI-safe)."""
import argparse, json, os, sys, time, urllib.request

def skip(reason):
    print(json.dumps({"skip": reason}))
    sys.exit(0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", default=os.environ.get("CUA_CHECKOUT", ""))
    ap.add_argument("--checkpoint", default=os.environ.get("S1_CHECKPOINT", ""))
    ap.add_argument("--n", type=int, default=196)
    a = ap.parse_args()
    try:
        import torch  # noqa
    except ImportError:
        skip("torch not installed")
    if not a.upstream or not os.path.isdir(os.path.join(a.upstream, "libs", "cua-s1")):
        skip("cua checkout with libs/cua-s1 not provided (--upstream)")
    ckpt = a.checkpoint
    if not ckpt:
        cache = os.path.expanduser("~/.cache/jcua")
        os.makedirs(cache, exist_ok=True)
        ckpt = os.path.join(cache, "cua-s1-forms.safetensors")
        if not os.path.exists(ckpt):
            base = "https://huggingface.co/cua-ai/cua-s1-forms/resolve/main"
            urllib.request.urlretrieve(base + "/cua-s1-forms.safetensors", ckpt)
            urllib.request.urlretrieve(base + "/cua-s1-forms.json", os.path.join(cache, "cua-s1-forms.json"))
    sys.path.insert(0, os.path.join(a.upstream, "libs", "cua-s1", "python", "src"))
    import torch
    from cua_s1.model import load_checkpoint, validate_example
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rows = [json.loads(l) for l in open(os.path.join(root, "evals", "s1-forms", "demo.jsonl"))][:a.n]
    model, collator, _ = load_checkpoint(ckpt, "cpu")
    examples = [validate_example(r) for r in rows]
    t0, correct, bs = time.time(), 0, 32
    with torch.no_grad():
        for i in range(0, len(examples), bs):
            batch = collator(examples[i:i + bs])
            logits = model(batch)
            logits[~batch["option_mask"]] = float("-inf")
            for e, p in zip(examples[i:i + bs], logits.argmax(dim=1).tolist()):
                correct += (p == e.label)
    dt = time.time() - t0
    print(json.dumps({"n": len(examples), "top1": round(correct / len(examples), 4),
        "ms_per_element": round(dt / len(examples) * 1000, 2),
        "params": sum(p.numel() for p in model.parameters())}))

main()
