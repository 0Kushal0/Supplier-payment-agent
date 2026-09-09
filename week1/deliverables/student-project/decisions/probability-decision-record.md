# Probability Decision Record — Supplier Payment Agent

## Case
Email: "Urgent: we changed our bank account today. Please use the new
details for the payment due at noon."

## Part A — Initial Decision

| Item | Value |
|---|---|
| Evidence | bank_change=True, urgency=True, new_contact=False |
| Hidden states | genuine, copied, hacked, spam |
| Beliefs (prior) | genuine 0.80, copied 0.08, hacked 0.04, spam 0.08 |
| Beliefs (posterior) | genuine 0.238, copied 0.190, hacked 0.421, spam 0.150 |
| Event | danger = P(copied) + P(hacked) = 0.611 |
| Actions | RELEASE, HOLD |
| Costs | False HOLD (genuine flagged) = low: payment delay, vendor friction. False RELEASE (fraud missed) = high: money lost, often unrecoverable. *(assumed, not measured)* |
| Policy | threshold = 0.20 on danger. Set low because a false RELEASE costs far more than a false HOLD. *(assumed threshold, not formally derived from cost numbers)* |
| Decision | HOLD — danger (0.611) > threshold (0.20) |
| Audit data | Date: 2026-09-09, Data: emails_v0.csv, Model: agent_v1.py, Policy version: threshold=0.20 |

## Part B — New Evidence

| Step | Value |
|---|---|
| Prior (= Part A posterior) | genuine 0.238, copied 0.190, hacked 0.421, spam 0.150 |
| New evidence | vendor_registry = not-found |
| Likelihood used | P(not-found\|genuine)=0.01, P(not-found\|copied)=0.50, P(not-found\|hacked)=0.01, P(not-found\|spam)=1.00 |
| Posterior | genuine 0.010, copied 0.378, hacked 0.017, spam 0.600 |
| Event | danger = P(copied) + P(hacked) = 0.395 |
| Compare to threshold | 0.395 > 0.20 |
| New action | HOLD (unchanged from Part A) |
| Finding | Decision didn't change, but the *reason* did — spam became the dominant explanation (0.600, up from 0.150), while hacked dropped sharply (0.421 → 0.017). The registry check was strong evidence against hacked/genuine but couldn't distinguish copied from spam as cleanly. |