# Supplier Payment Agent

An AI agent that decides whether to **RELEASE** or **HOLD** a supplier payment
when an email asks to change the supplier's bank details, a common
business-email-compromise (BEC) fraud pattern.

The LLM is used only as a sensor. It answers three yes/no questions about the
email, and the decision comes from explicit Bayesian inference over the hidden
state of the sender plus a fixed risk threshold. Every decision can therefore
be traced back to its evidence and probabilities.

```
Email ──► local LLM (Llama 3.2 3B via Ollama) answers 3 yes/no clues:
          bank change? urgency? new contact?   (keyword fallback if the model is down)
            │
            ▼
      Bayes' rule: prior x P(clues | state) -> posterior over 4 hidden states
      (genuine, copied, hacked, spam)
            │
            ▼
      HOLD if P(copied or hacked) > 0.20, otherwise RELEASE
```

## Results

100 labeled test emails (70 safe, 30 dangerous), local LLM run:

| Policy                         | Accuracy | Precision | Recall | F1    |
|--------------------------------|---------:|----------:|-------:|------:|
| Baseline: always RELEASE       |    70.0% |      0.0% |   0.0% |  0.0% |
| Bayesian agent (V1)            |    96.0% |    100.0% |  86.7% | 92.9% |

## Failure analysis

Five failure modes are documented with root cause, example and fix direction
in [failure-analysis.md](week1/deliverables/student-project/results/failure-analysis.md):

1. Threshold too sensitive when only one weak clue fires
2. Silent LLM fallback: recall dropped from ~90% to 63.3% with no warning
3. LLM non-determinism: identical runs gave 4, 3 and 1 failures
4. LLM evidence hallucination: clues reported that are not in the email
5. Vendor-registry evidence designed but not yet implemented

## Paper

*A Bayesian Supplier Payment Agent for Bank-Change Requests*:
[preprint (PDF)](week1/deliverables/student-project/paper/preprint.pdf)

## Run it

```bash
cd week1/deliverables/student-project
pip install -r requirements.txt
ollama pull llama3.2:3b
cd experiments
python exp_v1.py            # baseline + Bayesian agent
python exp_v1.py --no-llm   # keyword evidence only, no model needed
```

Full setup, repository structure and known limitations:
[project README](week1/deliverables/student-project/README.md).

Built during an AI-Native Shipping Sprint (course project).
