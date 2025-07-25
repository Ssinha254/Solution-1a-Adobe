import logging
from pathlib import Path
from utils.extract_text import extract_elements
from utils.title_detector import detect_title
from utils.detect_headings import detect_heading_structure
from utils.json_builder import build_outline_json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

def process_pdfs():
    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf in input_dir.glob("*.pdf"):
        logging.info(f"Processing: {pdf.name}")
        try:
            elements = extract_elements(pdf)
            title = detect_title(elements, pdf)
            outline = detect_heading_structure(elements)
            build_outline_json(pdf, title, outline, output_dir)
            logging.info(f"Successfully processed: {pdf.name}")
        except Exception as e:
            logging.error(f"Failed to process {pdf.name}: {e}", exc_info=True)

if __name__ == "__main__":
    process_pdfs()
