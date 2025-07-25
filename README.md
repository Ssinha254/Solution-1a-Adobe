# Adobe India Hackathon Round 1A: Heading Extraction

## Overview
This project extracts headings from PDF documents using rule-based and lightweight NLP techniques. It is designed for the Adobe India Hackathon Round 1A.

## Usage
1. Place your input PDF files in the `input/` directory.
2. Run the main script:
   ```bash
   python process_pdfs.py
   ```
3. Extracted headings and document titles will be saved as JSON files in the `output/` directory, one per input PDF.

## Hackathon Constraints
- **CPU-only**: No GPU dependencies or requirements.
- **Model size**: All models used are ≤200MB (uses spaCy's `en_core_web_sm` only).
- **Runtime**: Designed to process each PDF in ≤10 seconds.

## Input/Output
- **Input**: PDF files in `input/`
- **Output**: JSON files in `output/` with the following structure:
  ```json
  {
    "title": "Document Title",
    "outline": [
      {"level": "H1", "text": "Heading Text", "page": 1},
      ...
    ]
  }
  ```

## Requirements
See `requirements.txt` for dependencies.
