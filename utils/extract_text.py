import pdfplumber
from collections import defaultdict

def extract_elements(pdf_path):
    elements = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["fontname", "size", "top", "bottom"], use_text_flow=True)
            lines_by_top = defaultdict(list)
            for word in words:
                key = round(word['top'], 1)
                lines_by_top[key].append(word)

            prev_bottom = None
            for top in sorted(lines_by_top):
                line_words = sorted(lines_by_top[top], key=lambda w: w['x0'])
                line_text = " ".join(w['text'] for w in line_words)
                font_size = float(line_words[0].get('size', 12.0))
                fontname = line_words[0].get('fontname', '')
                is_bold = int('bold' in fontname.lower())
                is_italic = int('italic' in fontname.lower() or 'oblique' in fontname.lower())
                line_top = float(line_words[0].get('top', 0))
                line_bottom = float(line_words[0].get('bottom', 0))
                whitespace_above = 0.0
                if prev_bottom is not None:
                    whitespace_above = max(0.0, line_top - prev_bottom)
                prev_bottom = line_bottom
                elements.append({
                    "text": line_text.strip(),
                    "font_size": font_size,
                    "fontname": fontname,
                    "is_bold": is_bold,
                    "is_italic": is_italic,
                    "top": line_top,
                    "bottom": line_bottom,
                    "whitespace_above": whitespace_above,
                    "page": page.page_number
                })
    return elements
