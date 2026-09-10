# Supplier Payment Agent — Week 1 (AI-Native Shipping Sprint)

## Problem

The agent observes an email requesting a change to a supplier's bank
details. It must decide **RELEASE** or **HOLD** the payment, because the
sender's true identity — genuine, copied, hacked, spam, synthetic-vendor,
or something-else — is not known.

## Setup

### 1. Python environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ollama (required for LLM-based evidence reading)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:3b
```

**GitHub Codespaces note:** the default 2-core/8GB machine can crash
Ollama (`llama-server process has terminated`) — not enough RAM to load
the model. Resize to 4-core/16GB: Codespaces list → **"..."** → *Change
machine type* → *Update codespace* → then fully **stop and restart** the
Codespace (a reconnect alone won't apply the resize).

## Repo structure

```
week1/deliverables/student-project/
├── research-file.md                     problem statement, background research
├── discussion-record.md                 public Reddit/X discussion log
├── review-record.md                     AI-tool review log
├── decisions/
│   └── probability-decision-record.md   hand-worked Bayes updates
├── src/
│   └── agent_v1.py                      the agent: hidden states, priors, evidence, policy
├── experiments/
│   └── exp_v1.py                        runs the agent over data/emails_v0.csv, scores it
├── data/
│   └── emails_v0.csv                    100 labeled test emails (70 safe / 30 dangerous)
├── paper/
│   ├── main.tex
│   └── references.bib
└── social/
    ├── linkedin-post.md
    └── x-thread.md
```

## Running the experiment

```bash
cd week1/deliverables/student-project/experiments
python exp_v1.py                 # baseline (P0) + V1 agent, default
python exp_v1.py --baseline-only # always-RELEASE baseline only
python exp_v1.py --v1-only       # posterior-threshold agent only
python exp_v1.py --no-llm        # V1 reads evidence via keyword match, not Ollama
python exp_v1.py --verbose       # print every case, not just failures
```

## The agent

- **Hidden states:** genuine, copied, hacked, spam
- **Evidence:**
  - `bank_change`, `urgency`, `new_contact` — read from email text via LLM, with keyword fallback if the LLM call fails
  - `vendor_registry` — external lookup, hand-labeled per test email (no live registry API yet)
- **Decision rule:** HOLD when P(copied or hacked | evidence) > 20%

## Results (100 test emails, local LLM run)

| Policy                       | Accuracy | Precision | Recall | F1    |
|-------------------------------|---------:|----------:|-------:|------:|
| P0 baseline (always RELEASE) |    70.0% |      0.0% |   0.0% |  0.0% |
| V1 (posterior threshold)     |    96.0% |    100.0% |  86.7% | 92.9% |

## Known limitations

- **Silent LLM fallback.** If the Ollama call fails, `agent_v1.py` falls
  back to keyword matching without a visible warning — the printout still
  labels the run "LLM" even when every row silently fell back. Observed in
  GitHub Codespaces with Ollama not running: recall dropped from ~90% to
  63.3%.
- **Threshold too sensitive to single-clue cases.** When only one weak
  clue fires (e.g. `bank_change` alone), the posterior lands around 14% —
  just under the 20% HOLD threshold — causing missed dangerous cases.
- Priors and clue likelihoods are hand-typed assumptions, not measured
  from real fraud/AP data (no domain-expert contact yet).
- `vendor_registry` evidence is manually labeled per test email since no
  live registry API is available.