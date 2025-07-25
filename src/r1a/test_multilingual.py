import os
import json
from pathlib import Path
from utils.extract_text import extract_elements
from utils.detect_headings import detect_heading_structure

def main():
    data_dir = Path('data/multilingual_samples')
    for pdf_file in data_dir.glob('*.pdf'):
        print(f'File: {pdf_file.name}')
        elements = extract_elements(pdf_file)
        result = detect_heading_structure(elements)
        lang = result.get('language', 'unknown')
        print(f'  Detected language: {lang}')
        for h in result['headings']:
            print(f'    [{h["level"]}] {h["text"]} (p{h["page"]}, conf={h["confidence"]:.2f})')
        print()

if __name__ == '__main__':
    main() 