import os
import json
from pathlib import Path
from evaluate import evaluate, print_report

def find_pairs(pred_dir, gold_dir):
    pred_files = {f.stem: f for f in Path(pred_dir).glob('*.json')}
    gold_files = {f.stem: f for f in Path(gold_dir).glob('*.json')}
    pairs = [(pred_files[k], gold_files[k]) for k in pred_files if k in gold_files]
    return pairs

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Batch evaluation of heading extraction.')
    parser.add_argument('--pred_dir', default='output', help='Directory with predicted JSONs')
    parser.add_argument('--gold_dir', default='gold', help='Directory with gold/reference JSONs')
    parser.add_argument('--report', default=None, help='Output metrics report as JSON')
    args = parser.parse_args()

    pairs = find_pairs(args.pred_dir, args.gold_dir)
    all_metrics = []
    for pred, gold in pairs:
        metrics, _ = evaluate(pred, gold)
        print(f'File: {pred.name}')
        print_report(metrics)
        all_metrics.append(metrics)
    # Compute average macro-F1
    macro_f1s = [m['macro_f1'] for m in all_metrics]
    avg_macro_f1 = sum(macro_f1s) / len(macro_f1s) if macro_f1s else 0.0
    print(f'Average Macro-F1: {avg_macro_f1:.3f}')
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump({'files': len(all_metrics), 'avg_macro_f1': avg_macro_f1, 'all_metrics': all_metrics}, f, indent=2)

if __name__ == '__main__':
    main() 