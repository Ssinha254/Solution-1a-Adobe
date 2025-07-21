import re
import spacy
from scipy.spatial.distance import cosine

# Load lightweight spaCy model
nlp = spacy.load("en_core_web_sm")

def detect_heading_structure(elements):
    headings = []
    seen = set()

    # Get all unique lines
    texts = [el["text"].strip() for el in elements if el["text"].strip()]
    docs = [nlp(text) for text in texts]
    avg_vector = sum(doc.vector for doc in docs) / len(docs)

    # Get top 2 font sizes
    font_sizes = sorted({round(el["font_size"], 1) for el in elements}, reverse=True)[:2]

    for el in elements:
        text = el["text"].strip()
        font_size = round(el["font_size"], 1)

        if not text or text in seen:
            continue

        # 📏 Word count rule
        word_count = len(text.split())
        if word_count < 2 or word_count > 12:
            continue

        # 🔢 Visual symbols / fillers / dot-lines
        if text[0] in {"-", "•", "—", "|"} or re.search(r"\.{5,}", text):
            continue

        # 🔠 Font filter
        if font_size not in font_sizes:
            continue

        # 🧠 Semantic uniqueness score
        sim = 1 - cosine(nlp(text).vector, avg_vector)
        if sim > 0.9:
            continue  # too similar to rest of text → likely paragraph

        # 📐 Assign heading level by number pattern
        if re.match(r"^\d+\.\d+\.\d+\.\d+\s", text):
            level = "H4"
        elif re.match(r"^\d+\.\d+\.\d+\s", text):
            level = "H3"
        elif re.match(r"^\d+\.\d+\s", text):
            level = "H2"
        elif re.match(r"^\d+\.\s", text):
            level = "H1"
        elif text.endswith(":"):
            level = "H3"
        else:
            level = "H2"

        headings.append({
            "level": level,
            "text": text if text.endswith(" ") else text + " ",
            "page": el["page"]
        })
        seen.add(text)

    return headings
