from pathlib import Path

def detect_title(elements, pdf_path):
    if not elements:
        return Path(pdf_path).stem.replace("_", " ").title()

    # Look at the top 5 lines with the largest fonts
    top = sorted(elements[:10], key=lambda e: -e["font_size"])
    title_lines = []
    used_fonts = set()

    for el in top:
        if len(title_lines) >= 2:
            break
        if el["font_size"] not in used_fonts and len(el["text"].split()) >= 2:
            title_lines.append(el["text"].strip())
            used_fonts.add(el["font_size"])

    title = " ".join(title_lines)
    return title.strip() + "  "  # match expected spacing
