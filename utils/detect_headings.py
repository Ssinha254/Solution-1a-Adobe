import re
import spacy
from scipy.spatial.distance import cosine
import os
import pickle
import numpy as np
from langdetect import detect

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

def extract_features(elements, lang='en'):
    features = []
    for i, el in enumerate(elements):
        text = el['text']
        font_size = el.get('font_size', 12.0)
        is_bold = el.get('is_bold', 0)
        is_italic = el.get('is_italic', 0)
        text_len = len(text)
        if lang in ['ja', 'hi']:
            cap_ratio = 0.0
        else:
            cap_ratio = sum(1 for c in text if c.isupper()) / (len(text) or 1)
        whitespace_above = el.get('whitespace_above', 0)
        y_pos = el.get('top', 0)
        y_pct = y_pos / (el.get('page_height', 1) or 1)
        num_pattern = 0
        if any([text.strip().startswith(p) for p in ['1.', '1.1', '1.1.1', 'I.', 'A.']]):
            num_pattern = 1
        features.append([
            font_size, is_bold, is_italic, text_len, cap_ratio, whitespace_above, y_pct, num_pattern
        ])
    return np.array(features)

def detect_language(elements):
    # Use langdetect on the first 10 lines with text
    texts = [el['text'] for el in elements if el['text'].strip()]
    sample = ' '.join(texts[:10])
    try:
        lang = detect(sample)
    except Exception:
        lang = 'en'
    return lang

def detect_heading_structure(elements):
    headings = []
    seen = set()
    lang = detect_language(elements)

    texts = [el["text"].strip() for el in elements if el["text"].strip()]
    docs = [nlp(text) for text in texts]
    avg_vector = sum(doc.vector for doc in docs) / len(docs)
    font_sizes = sorted({round(el["font_size"], 1) for el in elements}, reverse=True)[:2]

    # ML prediction if model is available
    ml_preds = None
    ml_probs = None
    if clf is not None:
        feats = extract_features(elements, lang)
        ml_pred_idx = clf.predict(feats)
        ml_preds = [label_map.get(idx, 'O') for idx in ml_pred_idx]
        probas = clf.predict_proba(feats)
        ml_probs = [float(np.max(p)) for p in probas]
    else:
        ml_preds = ['O'] * len(elements)
        ml_probs = [1.0] * len(elements)

    for idx, el in enumerate(elements):
        text = el["text"].strip()
        font_size = round(el["font_size"], 1)
        top = el.get("top", 0)
        if not text or text in seen:
            continue
        word_count = len(text.split())
        if lang in ['ja', 'hi']:
            # Japanese/Hindi: skip capitalization, allow shorter/longer headings
            if word_count < 1 or word_count > 20:
                continue
        else:
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
        confidence = ml_probs[idx] if ml_level != 'O' else 1.0
        if ml_level != 'O':
            level = ml_level
        headings.append({
            "level": level,
            "text": text if text.endswith(" ") else text + " ",
            "page": el["page"],
            "confidence": confidence,
            "top": top
        })
        seen.add(text)
    return {"language": lang, "headings": headings}
