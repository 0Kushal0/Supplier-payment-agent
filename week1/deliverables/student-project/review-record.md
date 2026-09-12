# Review Record — Supplier Payment Agent (Week 1)

Three AI tools reviewed the repo (README, `agent_v1.py`, `exp_v1.py`,
`probability-decision-record.md`) independently, each asked to find
issues with the design, code, and documentation.

---

## Review #1 — Qwen 3.8 Max

**Scope:** README + agent design

**Key findings:**
- Silent LLM fallback needs visible logging (`logging.warning()` on every
  fallback), plus consider a `--strict` flag to hard-fail instead of
  silently degrading
- Threshold too permissive for high-risk clues — suggested either a
  hard-stop override for `bank_change`, or recalibrated likelihood weights
- README is missing an architecture/pipeline section
- No written justification for why 86.7% recall (vs. higher) was accepted
- `vendor_registry` manual labeling is fine for Week 1, should become a
  mock API/DB in Week 2
- Verify `requirements.txt` actually lists real imports

**Action taken:** requirements.txt checked and rebuilt from a clean venv.
Architecture section, fallback logging, and threshold recalibration
logged as optional future work, not required for Week 1.

---

## Review #2 — ChatGPT

**Scope:** main branch — README, `agent_v1.py`, experiment code,
probability decision record

**Key findings:**
- **`vendor_registry` mismatch:** documented in the decision record but
  `posterior()` only actually processes `bank_change`, `urgency`,
  `new_contact` — the implemented agent and the documented model disagree
- **Independence assumption:** Bayes treats the three clues as
  conditionally independent (`P(c1,c2,c3|state)` = product of individual
  probabilities), a strong assumption since email clues can correlate —
  this makes the reported 96% accuracy look stronger than the evidence
  model actually justifies
- Silent LLM fallback (already known) — highest-priority code fix
- Priority order suggested: fix vendor_registry mismatch → make fallback
  visible → document independence assumption → don't chase higher
  accuracy yet

**Action taken:** vendor_registry gap confirmed as failure #5 (see
`failure-analysis.md`). Independence assumption logged as a new,
separate limitation to document in the paper.

---

## Review #3 — Grok

**Scope:** main branch, focused on README + related code

**Key findings (blocking):**
- `data/emails_v0.csv` returns 404 on GitHub — never committed, local-only
- `requirements.txt` missing entirely — README references it but it
  didn't exist
- `vendor_registry` mismatch (confirms #2's finding independently)
- Silent LLM fallback (confirms, again) — recommends counting and
  printing LLM-vs-keyword fallback rows per run

**Other findings:** hand-typed priors presented as if measured in the
results table; brittle relative paths in `load_rows`; no dependency
pinning; minor README formatting; repo-root `README.md` still an empty
stub separate from the student-project README; `posterior()` has no
observation-noise model; `run()`'s return key `"belief"` is a confusing
name for what's actually the prior.

**Action taken:** `data/emails_v0.csv` committed. `requirements.txt`
generated from a clean venv and committed. `.gitignore` added
(`venv/`, `__pycache__/`, `*.pyc`).

---

## Cross-cutting themes

All three reviewers independently flagged the same two issues without
being shown each other's output:

1. **`vendor_registry` documented but not implemented** — real gap
   between the decision record and the running agent (failure #5)
2. **Silent LLM fallback** — the run is labeled "LLM" even when it
   silently degraded to keyword matching (failure #2)

That two blind reviews converge on the same root causes independently
diagnosed earlier is a useful signal the failure analysis is accurate,
not just self-reported.

## What was fixed vs. documented

| Finding | Status |
|---|---|
| `data/emails_v0.csv` not committed | Fixed — committed |
| `requirements.txt` missing | Fixed — generated, committed |
| `.gitignore` missing | Fixed — added |
| `vendor_registry` mismatch | Documented (failure #5), not implemented yet |
| Silent LLM fallback | Documented (failure #2), not made loud yet |
| Independence assumption | Documented as a new limitation |
| Threshold sensitivity | Documented (failure #1), not recalibrated yet |
| Architecture diagram | Not added — optional polish |