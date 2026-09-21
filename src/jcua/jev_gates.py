"""Single shared Jev transport. Decider only — never generation."""
import os
import httpx

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = os.environ.get("TYPESAFE_MODEL", "jev-latest")

def ask_choice(question, options, criteria=None):
    """One Jev choice call. Returns (choice_id, probs) or (None, {}) on fallback."""
    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key:
        return None, {}
    try:
        r = httpx.post(ENDPOINT, headers={"Authorization": f"Bearer {key}"},
            json={"model": MODEL, "question": question, "options": options,
                  "criteria": criteria or {}}, timeout=15)
        r.raise_for_status()
        d = r.json()
        return d.get("choice"), d.get("probabilities", {})
    except Exception:
        return None, {}
