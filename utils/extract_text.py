import pdfplumber
from collections import defaultdict

def extract_elements(pdf_path):
    elements = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            words = page.extract_words(use_text_flow=True)
            lines_by_top = defaultdict(list)
            for word in words:
                key = round(word['top'], 1)
                lines_by_top[key].append(word)

            for top in sorted(lines_by_top):
                line_words = sorted(lines_by_top[top], key=lambda w: w['x0'])
                line_text = " ".join(w['text'] for w in line_words)
                font_size = float(line_words[0].get('size', 12.0))
                elements.append({
                    "text": line_text.strip(),
                    "font_size": font_size,
                    "page": i + 1
                })
    return elements
