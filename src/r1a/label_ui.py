import argparse
import csv
import json
from pathlib import Path
from utils.extract_text import extract_elements

LEVELS = ['O', 'title', 'H1', 'H2', 'H3']

def export_csv(elements, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['idx', 'text', 'level'])
        for i, el in enumerate(elements):
            writer.writerow([i, el['text'], 'O'])
    print(f'Exported to {csv_path}')

def import_csv(csv_path):
    labels = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels.append(row.get('level', 'O'))
    return labels

def save_gold(elements, labels, pdf_path, out_path):
    title = ''
    outline = []
    for el, lvl in zip(elements, labels):
        if lvl == 'title':
            title = el['text']
        elif lvl in {'H1', 'H2', 'H3'}:
            outline.append({'level': lvl, 'text': el['text'], 'page': el['page']})
    gold = {'title': title, 'outline': outline}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(gold, f, indent=2)
    print(f'Saved gold labels to {out_path}')

def main():
    parser = argparse.ArgumentParser(description='Label PDF lines as heading levels and save to gold.')
    parser.add_argument('--pdf', required=True, help='PDF file to label')
    parser.add_argument('--csv', required=True, help='CSV for export/import')
    parser.add_argument('--out', required=True, help='Output gold JSON file')
    parser.add_argument('--import_csv', action='store_true', help='Import labels from CSV')
    args = parser.parse_args()

    elements = extract_elements(args.pdf)
    if not args.import_csv:
        export_csv(elements, args.csv)
        print('Fill in the CSV and rerun with --import_csv')
        return
    labels = import_csv(args.csv)
    save_gold(elements, labels, args.pdf, args.out)

if __name__ == '__main__':
    main() 