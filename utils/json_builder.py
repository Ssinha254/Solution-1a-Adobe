import json
from pathlib import Path

def build_outline_json(pdf_path, title, outline, output_dir):
    # Sort headings by page, then by y-position if available, else as-is
    outline_sorted = sorted(
        outline,
        key=lambda h: (h.get('page', 0), h.get('top', 0))
    )

    # Build hierarchy: Title > H1 > H2 > H3
    hierarchy = []
    current_h1 = None
    current_h2 = None
    for h in outline_sorted:
        h_entry = {
            "level": h["level"],
            "text": h["text"],
            "page": h["page"],
            "confidence": h.get("confidence", 1.0),
            "children": []
        }
        if h["level"] == "H1":
            current_h1 = h_entry
            hierarchy.append(current_h1)
            current_h2 = None
        elif h["level"] == "H2":
            if current_h1 is not None:
                current_h1["children"].append(h_entry)
            else:
                hierarchy.append(h_entry)
            current_h2 = h_entry
        elif h["level"] == "H3":
            if current_h2 is not None:
                current_h2["children"].append(h_entry)
            elif current_h1 is not None:
                current_h1["children"].append(h_entry)
            else:
                hierarchy.append(h_entry)
        else:
            hierarchy.append(h_entry)

    result = {
        "title": title,
        "outline": hierarchy
    }

    output_path = output_dir / f"{Path(pdf_path).stem}.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
