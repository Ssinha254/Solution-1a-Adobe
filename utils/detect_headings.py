import re
import spacy
from scipy.spatial.distance import cosine
import os
import pickle
import numpy as np

# Load lightweight spaCy model
nlp = spacy.load("en_core_web_sm")

MODEL_PATH = 'models/heading_classifier.pkl'
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        _ml = pickle.load(f)
    clf = _ml['model']
    label_map = {v: k for k, v in _ml['label_map'].items()}
else:
    clf = None
    label_map = None

def extract_features(elements):
    features = []
    for i, el in enumerate(elements):
        text = el['text']
        font_size = el.get('font_size', 12.0)
        is_bold = 0  # Placeholder
        is_italic = 0  # Placeholder
        text_len = len(text)
        cap_ratio = sum(1 for c in text if c.isupper()) / (len(text) or 1)
        whitespace_above = 0  # Placeholder
        y_pos = el.get('y', 0)
        y_pct = y_pos / (el.get('page_height', 1) or 1)
        num_pattern = 0
        if any([text.strip().startswith(p) for p in ['1.', '1.1', '1.1.1', 'I.', 'A.']]):
            num_pattern = 1
        features.append([
            font_size, is_bold, is_italic, text_len, cap_ratio, whitespace_above, y_pct, num_pattern
        ])
    return np.array(features)

def detect_heading_structure(elements):
    headings = []
    seen = set()

    texts = [el["text"].strip() for el in elements if el["text"].strip()]
    docs = [nlp(text) for text in texts]
    avg_vector = sum(doc.vector for doc in docs) / len(docs)
    font_sizes = sorted({round(el["font_size"], 1) for el in elements}, reverse=True)[:2]

    # ML prediction if model is available
    ml_preds = None
    if clf is not None:
        feats = extract_features(elements)
        ml_pred_idx = clf.predict(feats)
        ml_preds = [label_map.get(idx, 'O') for idx in ml_pred_idx]
    else:
        ml_preds = ['O'] * len(elements)

    for idx, el in enumerate(elements):
        text = el["text"].strip()
        font_size = round(el["font_size"], 1)
        if not text or text in seen:
            continue
        word_count = len(text.split())
        if word_count < 2 or word_count > 12:
            continue
        if text[0] in {"-", "•", "—", "|"} or re.search(r"\.{5,}", text):
            continue
        if font_size not in font_sizes:
            continue
        sim = 1 - cosine(nlp(text).vector, avg_vector)
        if sim > 0.9:
            continue
        # Heuristic level
        if re.match(r"^\d+\.\d+\.\d+\.\d+\s", text):
            level = "H4"
        elif re.match(r"^\d+\.\d+\.\d+\s", text):
            level = "H3"
        elif re.match(r"^\d+\.\s", text):
            level = "H1"
        elif text.endswith(":"):
            level = "H3"
        else:
            level = "H2"
        # ML adjustment
        ml_level = ml_preds[idx]
        if ml_level != 'O':
            level = ml_level
        headings.append({
            "level": level,
            "text": text if text.endswith(" ") else text + " ",
            "page": el["page"]
        })
        seen.add(text)
    return headings
