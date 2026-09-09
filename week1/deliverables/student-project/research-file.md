# Research File — Supplier Payment Verification Agent

## 1. Problem statement
> The agent reads a supplier bank-change request. It must approve, verify, or stop the request because the sender's true identity and intent are not directly observable.

## 2. Project objective
Design, build, and test an AI agent that makes this pay/verify/hold call under uncertainty. Pressure-test the design in public Reddit/X discussions. Write and publish an IJCAI-style preprint covering the design, experiment, and failure analysis. Post the findings on LinkedIn/X/Reddit.

## 3. Technical terms

**Probability & decision theory:** hidden state, prior, posterior, likelihood, belief distribution, Bayes' theorem, entropy, conditional entropy, information gain vs. expected information gain, mutual information, cross-entropy, KL divergence, Jensen–Shannon divergence, calibration, expected cost, value of information, break-even threshold, exploration vs. exploitation, distribution shift, stop rule, human escalation.

**Fraud/AP domain:** Business Email Compromise (BEC), vendor/supplier impersonation, invoice redirection fraud, mailbox compromise vs. account takeover, synthetic vendor, callback verification, vendor master file, SPF/DKIM/DMARC, domain spoofing, cost-sensitive thresholding, class imbalance, confusion matrix, precision/recall.

## 4. Search queries used
- business email compromise detection dataset
- business email compromise supplier bank change verification
- accounts payable fraud vendor bank account verification
- POMDP value of information fraud detection decision threshold
- cost-sensitive fraud detection threshold
- reddit accounts payable fraud community

## 5. Reddit communities
- **r/cybersecurity** — already posted once; automod removed it, needs a different framing next time
- **r/Accounting** — confirmed ~1.3M members, active daily
- **r/sysadmin**, **r/msp**, **r/AskNetsec** — established IT/security communities where BEC and email-auth controls come up regularly
- **r/LocalLLaMA** — relevant to the agent's implementation side (runs on local Ollama)
- **r/statistics** / **r/AskStatistics** — for sanity-checking the Bayesian-update and threshold math

## 6. Relevant X accounts
No currently-active, verified account found. @briankrebs looked like a fit, but his last post there was in 2025 — effectively inactive on X now. Use X's native search for "BEC," "vendor fraud," "AP fraud," "wire fraud," "invoice fraud" and follow active practitioners to hit the 15–25 target — this isn't something I can verify reliably through web search.

## 7. Five useful papers, articles, repositories, or datasets
_(Left empty for now. To be filled in only once a paper is actually read by me and confirmed useful — i.e. it changed a hidden state, a likelihood, an evidence source, or the threshold. Not pre-populated with AI-found sources I haven't personally verified.)_

## 8. Questions I want to answer
1. **Observation** — What does the agent actually receive? 
2. **Hidden state** — What is genuinely unknown and matters? Usually: who this really is, or what they intend.
3. **Possible worlds** — What are all the plausible explanations? 
4. **Prior belief** — What did the agent believe before this evidence? Where did that number come from?
5. **Evidence** — What new signals can arrive or be requested?
6. **Posterior belief** — How does belief change? 

## 9. AI errors
- **Qwen 3.8 Max:** asked for hidden-state suggestions beyond genuine/copied/hacked/spam. 8 of its 10 suggestions were duplicates or evidence sources mislabeled as hidden states. Only "synthetic vendor" survived.
- **Claude:** listed r/AccountsPayable, r/fraud, and @briankrebs in this file as if verified. Neither subreddit could be found, and the X account has been inactive since 2025. Claude can't fetch reddit.com or check X activity directly, and presented unverified names as fact instead of saying so.
