# agent_v1.py — one step past v0.
#
# v0 : Input -> Agent -> Decision           (LLM scores the stories directly)
# v1 : Input -> Hidden states -> Beliefs -> Evidence -> Posterior -> Action
#
# The difference: the story we cannot see (hidden state) is named up front,
# we start from a written-down prior, we read a few clues off the email,
# and Bayes moves the prior to a posterior. Nothing is "felt" in one shot.
#
# Where the LLM sits: the EVIDENCE step only. It answers three yes/no
# questions about the email and nothing else — it never scores a story and
# never picks an action. The belief comes from LIKELIHOOD + Bayes.
#
# UNCERTAIN (hand-typed, no owner has signed these off yet):
#   - PRIOR       : base rate of each hidden state in our real mail flow
#   - LIKELIHOOD  : P(clue = yes | hidden state)
#   - the LLM's own clue-reading error rate, which posterior() ignores:
#     it treats every reported clue as observed with certainty.
# Everything downstream inherits that uncertainty.

import csv, json, os, re

# Must precede the ollama import: the corporate proxy otherwise swallows
# 127.0.0.1:11434 and returns a 403 page.
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"

from ollama import chat

MODEL = "llama3.2:3b"

# 1. HIDDEN STATES — what actually sent the mail; never observed directly.
STATES = ["genuine", "copied", "hacked", "spam"]

# 2. BELIEFS — prior over the hidden states, before reading anything. UNCERTAIN.
PRIOR = {"genuine": 0.80, "copied": 0.08, "hacked": 0.04, "spam": 0.08}

# 3. EVIDENCE — clues we can actually observe, and how likely each clue is
#    under each hidden state. P(clue = yes | state). UNCERTAIN.
LIKELIHOOD = {
    "bank_change": {"genuine": 0.10, "copied": 0.95, "hacked": 0.90, "spam": 0.60},
    "urgency":     {"genuine": 0.15, "copied": 0.80, "hacked": 0.70, "spam": 0.75},
    "new_contact": {"genuine": 0.05, "copied": 0.85, "hacked": 0.20, "spam": 0.80},
}

CLUE_QUESTIONS = (
    "Read the supplier email below and answer three yes/no questions about it.\n"
    "bank_change: does it ask us to use changed or different bank/payment details?\n"
    "urgency: does it push for speed, or name a deadline?\n"
    "new_contact: does it come from an unfamiliar or personal address, or ask us "
    "to reply somewhere new?\n"
    'Reply with JSON only, like '
    '{"bank_change":true,"urgency":false,"new_contact":false}.\n\nEmail:\n'
)

# Fallback only — brittle, catches just these hand-typed phrases.
CLUE_WORDS = {
    "bank_change": ["bank detail", "bank account", "new account", "change our bank",
                    "changed our bank", "update our supplier bank", "new bank"],
    "urgency":     ["urgent", "immediately", "time sensitive", "today", "due at noon",
                    "asap"],
    "new_contact": ["new email", "personal email", "different address", "reply to this",
                    "gmail.com", "outlook.com"],
}

ACTION_THRESHOLD = 0.20


def load_rows(path="data/emails_v0.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_evidence_words(email):
    text = email.lower()
    return {clue: any(w in text for w in words) for clue, words in CLUE_WORDS.items()}


def read_evidence(email, use_llm=True):
    """Observed clues: clue name -> True/False. Returns (evidence, source)."""
    if not use_llm:
        return read_evidence_words(email), "words"
    try:
        reply = chat(model=MODEL, messages=[
            {"role": "user", "content": CLUE_QUESTIONS + email}]).message.content
        raw = json.loads(re.sub(r"```json\s*|\s*```", "", reply).strip())
        return {clue: bool(raw[clue]) for clue in CLUE_WORDS}, "llm"
    except Exception:
        return read_evidence_words(email), "words"   # model down, or junk JSON


def posterior(prior, evidence):
    """Bayes: multiply the prior by P(evidence | state), then normalise."""
    belief = dict(prior)
    for clue, seen in evidence.items():
        for s in STATES:
            p_yes = LIKELIHOOD[clue][s]
            belief[s] *= p_yes if seen else (1 - p_yes)
    total = sum(belief.values())
    if total <= 0:
        return {s: 1 / len(STATES) for s in STATES}
    return {s: v / total for s, v in belief.items()}


def danger(belief):
    return belief["copied"] + belief["hacked"]


def decide(belief, threshold=ACTION_THRESHOLD):
    """Map posterior danger to an action using a fixed policy threshold."""
    return "HOLD" if danger(belief) > threshold else "RELEASE"


def run(email, use_llm=True):
    evidence, _ = read_evidence(email, use_llm)
    posterior_belief = posterior(PRIOR, evidence)
    action = decide(posterior_belief)
    return {"input": email,
            "hidden_states": list(STATES),
            "belief": dict(PRIOR),
            "evidence": evidence,
            "posterior": {s: round(posterior_belief[s], 3) for s in STATES},
            "action": action}


if __name__ == "__main__":
    receipt = run("Urgent: we changed our bank account today. "
                  "Please use the new details for the payment due at noon.")
    for k, v in receipt.items():
        print(f"{k:16}: {v}")
