import os
import json
import time
import logging
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

LEVELS = ["title", "H1", "H2", "H3"]


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize(text):
    return text.strip().lower()

def extract_headings(data):
    # Returns dict: level -> set of (text, page)
    result = defaultdict(set)
    if "title" in data and data["title"]:
        result["title"].add((normalize(data["title"]), 1))
    for h in data.get("outline", []):
        lvl = h["level"].upper()
        if lvl in LEVELS:
            result[lvl].add((normalize(h["text"]), h["page"]))
    return result

def compute_metrics(pred, gold):
    metrics = {}
    f1s = []
    for lvl in LEVELS:
        pred_set = pred.get(lvl, set())
        gold_set = gold.get(lvl, set())
        tp = len(pred_set & gold_set)
        fp = len(pred_set - gold_set)
        fn = len(gold_set - pred_set)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        metrics[lvl] = {"precision": prec, "recall": rec, "f1": f1, "tp": tp, "fp": fp, "fn": fn}
        f1s.append(f1)
    macro_f1 = np.mean(f1s)
    metrics["macro_f1"] = macro_f1
    return metrics

def evaluate(pred_path, gold_path, log_runtime=False):
    start = time.time()
    pred = load_json(pred_path)
    gold = load_json(gold_path)
    pred_headings = extract_headings(pred)
    gold_headings = extract_headings(gold)
    metrics = compute_metrics(pred_headings, gold_headings)
    runtime = time.time() - start
    if log_runtime:
        logging.info(f"Evaluation runtime: {runtime:.2f} seconds")
    return metrics, runtime

def print_report(metrics):
    print("\n===== Evaluation Report =====")
    for lvl in LEVELS:
        m = metrics[lvl]
        print(f"{lvl:>6}: Precision={m['precision']:.3f} Recall={m['recall']:.3f} F1={m['f1']:.3f} (TP={m['tp']} FP={m['fp']} FN={m['fn']})")
    print(f"Macro-F1: {metrics['macro_f1']:.3f}")
    print("============================\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate heading extraction.")
    parser.add_argument('--pred', required=True, help='Predicted JSON file')
    parser.add_argument('--gold', required=True, help='Gold (reference) JSON file')
    parser.add_argument('--runtime', action='store_true', help='Log runtime (for 50-page PDFs)')
    parser.add_argument('--report', default=None, help='Output metrics report as JSON')
    args = parser.parse_args()

    metrics, runtime = evaluate(args.pred, args.gold, log_runtime=args.runtime)
    print_report(metrics)
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)
    if args.runtime:
        print(f"Total evaluation runtime: {runtime:.2f} seconds")

if __name__ == "__main__":
    main() 