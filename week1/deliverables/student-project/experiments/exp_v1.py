# exp_v1.py — run agent_v1 over the whole email set and score it.
#
# Nothing clever here: one pass, one receipt per email, then accuracy.
# The numbers only mean as much as the hand-typed PRIOR and LIKELIHOOD
# inside agent_v1.py — those are still UNCERTAIN.
#
# usage: python experiment/exp_v1.py [--baseline-only | --v1-only] [--no-llm] [--verbose]
#        default runs both: V0 baseline first, then V1
#        --baseline-only runs just the always-RELEASE V0 policy
#        --v1-only runs just the posterior-threshold V1 agent
#        --no-llm makes V1 read clues with keywords (fast, brittle, offline)
#        --verbose prints every case instead of failures only

import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from agent_v1 import ACTION_THRESHOLD, load_rows, run

TRUE_ACTION = {"safe": "RELEASE", "dangerous": "HOLD"}


def baseline(email):
    return "RELEASE"


def ratio(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def format_duration(seconds):
    total_seconds = max(0, round(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"


def show_progress(completed, total, started_at, current_id=None):
    elapsed = time.perf_counter() - started_at
    fraction = ratio(completed, total)
    bar_width = 24
    filled = round(bar_width * fraction)
    bar = "#" * filled + "-" * (bar_width - filled)

    if completed:
        eta = elapsed / completed * (total - completed)
        eta_text = format_duration(eta)
    else:
        eta_text = "calculating"

    status = f"[{bar}] {completed}/{total} ({fraction:.0%})"
    if current_id is not None:
        status += f" | processing ID {current_id}"
    status += f" | elapsed {format_duration(elapsed)} | ETA {eta_text}"

    if sys.stderr.isatty():
        end = "\n" if completed == total else ""
        print(f"\r{status:<110}", end=end, file=sys.stderr, flush=True)
    elif completed == total or completed % max(1, total // 10) == 0:
        print(status, file=sys.stderr, flush=True)


def show_evaluation(results, title, flow, evidence_reader, decision_rule, verbose):
    true_positive = sum(
        result["truth"] == "HOLD" and result["predicted"] == "HOLD"
        for result in results
    )
    true_negative = sum(
        result["truth"] == "RELEASE" and result["predicted"] == "RELEASE"
        for result in results
    )
    false_positive = sum(
        result["truth"] == "RELEASE" and result["predicted"] == "HOLD"
        for result in results
    )
    false_negative = sum(
        result["truth"] == "HOLD" and result["predicted"] == "RELEASE"
        for result in results
    )
    correct = true_positive + true_negative
    precision = ratio(true_positive, true_positive + false_positive)
    recall = ratio(true_positive, true_positive + false_negative)
    f1 = ratio(2 * precision * recall, precision + recall)

    print(f"\n{title}")
    print(f"Flow:            {flow}")
    print(f"Evidence reader: {evidence_reader}")
    print(f"Decision rule:   {decision_rule}")
    print(f"Samples:         {len(results)}\n")

    print("PERFORMANCE")
    print(f"Accuracy:              {ratio(correct, len(results)):>6.1%}  ({correct}/{len(results)})")
    print(f"Dangerous precision:   {precision:>6.1%}")
    print(f"Dangerous recall:      {recall:>6.1%}")
    print(f"Dangerous F1:          {f1:>6.1%}\n")

    print("CONFUSION MATRIX")
    print("                         Actual")
    print("                    Dangerous  Safe")
    print(f"Predicted HOLD        {true_positive:>9}  {false_positive:>4}")
    print(f"Predicted RELEASE     {false_negative:>9}  {true_negative:>4}")

    displayed = results if verbose else [
        result for result in results if result["predicted"] != result["truth"]
    ]
    heading = "ALL CASES" if verbose else "FAILURES"
    print(f"\n{heading} ({len(displayed)})")
    if not displayed:
        print("None")
        return

    print(f"{'ID':>4}  {'Actual':<7}  {'Action':<7}  {'Danger':>6}  Evidence")
    for result in displayed:
        danger = result["danger"]
        danger_text = "N/A" if danger is None else f"{danger:.1%}"
        print(f"{result['id']:>4}  {result['truth']:<7}  {result['predicted']:<7}  "
              f"{danger_text:>6}  {result['clues']}")


def run_baseline(verbose=False):
    print("\n=== Running V0 baseline (always RELEASE) ===")
    rows = load_rows(os.path.join(ROOT, "data", "emails_v0.csv"))
    results = []
    started_at = time.perf_counter()

    for completed, row in enumerate(rows):
        show_progress(completed, len(rows), started_at, row["id"])
        results.append({
            "id": row["id"],
            "truth": TRUE_ACTION[row["label"]],
            "predicted": baseline(row["email"]),
            "danger": None,
            "clues": "not read",
        })
    show_progress(len(rows), len(rows), started_at)

    show_evaluation(
        results,
        title="BASELINE EVALUATION",
        flow="Input -> Always RELEASE",
        evidence_reader="none",
        decision_rule="Always RELEASE",
        verbose=verbose,
    )
    return results


def run_v1(use_llm=True, verbose=False):
    print("\n=== Running V1 agent (posterior threshold) ===")
    rows = load_rows(os.path.join(ROOT, "data", "emails_v0.csv"))
    results = []
    started_at = time.perf_counter()

    for completed, row in enumerate(rows):
        show_progress(completed, len(rows), started_at, row["id"])
        receipt = run(row["email"], use_llm)
        truth = TRUE_ACTION[row["label"]]
        danger = receipt["posterior"]["copied"] + receipt["posterior"]["hacked"]
        clues = ",".join(
            clue for clue, observed in receipt["evidence"].items() if observed
        ) or "none"
        results.append({
            "id": row["id"],
            "truth": truth,
            "predicted": receipt["action"],
            "danger": danger,
            "clues": clues,
        })
    show_progress(len(rows), len(rows), started_at)

    show_evaluation(
        results,
        title="V1 EVALUATION",
        flow="Input -> Hidden states -> Belief -> Evidence -> Posterior -> Action",
        evidence_reader="LLM (keyword fallback on error)" if use_llm else "keywords",
        decision_rule=(
            f"HOLD when P(copied or hacked | evidence) > {ACTION_THRESHOLD:.0%}"
        ),
        verbose=verbose,
    )
    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate the V0 baseline and/or V1 agent.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--baseline-only", action="store_true", help="Run only the always-RELEASE V0 baseline.")
    mode.add_argument("--v1-only", action="store_true", help="Run only the V1 posterior-threshold agent.")
    parser.add_argument("--no-llm", action="store_true", help="Make V1 read evidence with deterministic keywords.")
    parser.add_argument("--verbose", action="store_true", help="Print every evaluated case.")
    args = parser.parse_args()

    use_llm = not args.no_llm

    if args.baseline_only:
        run_baseline(args.verbose)
        return
    if args.v1_only:
        run_v1(use_llm, args.verbose)
        return

    run_baseline(args.verbose)
    run_v1(use_llm, args.verbose)


if __name__ == "__main__":
    main()
