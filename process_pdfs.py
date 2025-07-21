from pathlib import Path
from utils.extract_text import extract_elements
from utils.title_detector import detect_title
from utils.detect_headings import detect_heading_structure
from utils.json_builder import build_outline_json

def process_pdfs():
    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf in input_dir.glob("*.pdf"):
        print(f"Processing: {pdf.name}")
        elements = extract_elements(pdf)
        title = detect_title(elements, pdf)
        outline = detect_heading_structure(elements)
        build_outline_json(pdf, title, outline, output_dir)

if __name__ == "__main__":
    process_pdfs()
