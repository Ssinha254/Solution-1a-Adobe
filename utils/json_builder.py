import json
from pathlib import Path

def build_outline_json(pdf_path, title, outline, output_dir):
    result = {
        "title": title,
        "outline": outline
    }

    output_path = output_dir / f"{Path(pdf_path).stem}.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
