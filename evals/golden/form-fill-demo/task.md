# form-fill-demo

Fill the Northwind Clinic patient-registration form from the referral document, then submit.

Measured by `scripts/score_s1_demo.py` on `evals/s1-forms/demo.jsonl` (196 real rows):
reported top-1 metric in docs/S1-FORMS.md. Not part of `golden_gate()` (needs torch);
the retrieval gate stays the promotion criterion.
