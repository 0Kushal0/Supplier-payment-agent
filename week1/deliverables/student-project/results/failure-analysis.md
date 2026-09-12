# Failure Analysis — Supplier Payment Agent (Week 1)

Five distinct failure modes found while evaluating `agent_v1.py` on
`data/emails_v0.csv` (100 emails, 70 safe / 30 dangerous).

| # | Failure | Type |
|---|---------|------|
| 1 | Threshold too sensitive to single-clue cases | Wrong threshold |
| 2 | Silent LLM fallback | Evidence-reading reliability |
| 3 | LLM non-determinism | Evidence-reading reliability |
| 4 | LLM evidence hallucination | Bad evidence |
| 5 | vendor_registry designed but never implemented | Scope gap |

---

## 1. Threshold too sensitive to single-clue cases

**Root cause:** When only `bank_change` fires with no corroborating clue,
the posterior lands at 14% — under the 20% HOLD threshold — so a genuinely
dangerous email is released.

**Example:** IDs 76, 100 — truth HOLD, predicted RELEASE, danger 14%,
evidence: `bank_change` only.

**Fix direction:** Lower the threshold, or increase the likelihood weight
for `bank_change` fired alone.

## 2. Silent LLM fallback

**Root cause:** If the Ollama call fails (e.g. not running), `agent_v1.py`
silently falls back to keyword matching — the printout still labels the
run "LLM," with no indication anything changed.

**Example:** Full run in GitHub Codespaces with no Ollama running: recall
dropped from ~90% to 63.3%, failures rose from 3 to 11, no warning shown
in the output.

**Fix direction:** Print a visible warning on each fallback, or a summary
count of how many rows fell back, at the end of the run.

## 3. LLM non-determinism

**Root cause:** Same code, same data, same email — different evidence
readings on different runs. The LLM call isn't deterministic by default.

**Example:** Three identical `exp_v1.py` runs produced 4, then 3, then 1
failures.

**Fix direction:** Use a fixed seed / temperature 0 if the model supports
it, or run multiple trials and report a range instead of one number.

## 4. LLM evidence hallucination

**Root cause:** The LLM claimed evidence that isn't present in the email
text at all.

**Example:** ID 25 — email: *"Routine supplier payment confirmation from
the established company email."* (label: safe). LLM flagged
`bank_change` + `new_contact` (danger 53.7%, wrongly predicted HOLD)
despite the text containing neither — "established" is the opposite of
new_contact. First false positive seen; precision dropped from 100% to
96.6% in that run.

**Fix direction:** Ask the LLM to quote the exact phrase that triggered
each clue, so hallucinated evidence is visible and checkable.

## 5. vendor_registry — designed, never implemented

**Root cause:** `vendor_registry` was added as an evidence source in
`decisions/probability-decision-record.md` (Part B), but was never wired
into `agent_v1.py`.

**Example:** Across all 100 rows of a full `--verbose` run, evidence is
always some combination of `bank_change` / `urgency` / `new_contact` /
`none` — `vendor_registry` never appears once.

**Fix direction:** Either implement it, or note it explicitly as a known
scope gap in the paper.