import os
import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import lightgbm as lgb
from tqdm import tqdm

# --- Feature extraction helpers ---
def extract_features(elements):
    features = []
    for i, el in enumerate(elements):
        text = el['text']
        font_size = el.get('font_size', 12.0)
        # Placeholder: bold/italic detection (not available, set to 0)
        is_bold = 0
        is_italic = 0
        text_len = len(text)
        cap_ratio = sum(1 for c in text if c.isupper()) / (len(text) or 1)
        whitespace_above = 0  # Placeholder: not available
        y_pos = el.get('y', 0)
        y_pct = y_pos / (el.get('page_height', 1) or 1)
        num_pattern = 0
        if any([text.strip().startswith(p) for p in ['1.', '1.1', '1.1.1', 'I.', 'A.']]):
            num_pattern = 1
        features.append([
            font_size, is_bold, is_italic, text_len, cap_ratio, whitespace_above, y_pct, num_pattern
        ])
    return np.array(features)

def get_labels(elements, gold_headings):
    # gold_headings: set of (normalized text, page, level)
    labels = []
    for el in elements:
        text = el['text'].strip().lower()
        page = el['page']
        label = 'O'
        for (gtext, gpage, glevel) in gold_headings:
            if text == gtext and page == gpage:
                label = glevel
                break
        labels.append(label)
    return labels

def load_gold_headings(gold_json):
    gold = set()
    if 'title' in gold_json and gold_json['title']:
        gold.add((gold_json['title'].strip().lower(), 1, 'title'))
    for h in gold_json.get('outline', []):
        gold.add((h['text'].strip().lower(), h['page'], h['level']))
    return gold

# --- Main training script ---
def main():
    input_dir = Path('input')
    output_dir = Path('output')
    X, y = [], []
    for pdf_file in tqdm(list(input_dir.glob('*.pdf'))):
        json_file = output_dir / (pdf_file.stem + '.json')
        if not json_file.exists():
            continue
        # Use extract_text from utils
        from utils.extract_text import extract_elements
        elements = extract_elements(pdf_file)
        with open(json_file, 'r', encoding='utf-8') as f:
            gold_json = json.load(f)
        gold_headings = load_gold_headings(gold_json)
        feats = extract_features(elements)
        labels = get_labels(elements, gold_headings)
        X.append(feats)
        y.extend(labels)
    if not X:
        print('No training data found.')
        return
    X = np.vstack(X)
    label_map = {l: i for i, l in enumerate(sorted(set(y)))}
    y_num = np.array([label_map[l] for l in y])
    clf = lgb.LGBMClassifier(n_estimators=100, max_depth=7)
    clf.fit(X, y_num)
    os.makedirs('models', exist_ok=True)
    with open('models/heading_classifier.pkl', 'wb') as f:
        pickle.dump({'model': clf, 'label_map': label_map}, f)
    print('Model saved to models/heading_classifier.pkl')

if __name__ == '__main__':
    main() 