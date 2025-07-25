# Adobe India Hackathon Round 1A: Heading Extraction

## Overview
This project extracts hierarchical headings from PDF documents using a hybrid of rule-based and machine learning (LightGBM) techniques. It is designed for the Adobe India Hackathon Round 1A and supports multilingual documents (including English, Hindi, Japanese).

## Features
- **PDF parsing** with font, style, and layout feature extraction
- **Hybrid heading detection**: heuristics + LightGBM classifier
- **Confidence scores** and hierarchical outline in output
- **Multilingual support** with language-adaptive rules
- **Dataset creation, manual labeling, and evaluation pipeline**
- **Dockerized, CPU-only, ≤200MB model, ≤10s per PDF**

---

## Directory Structure
```
input/                  # Input PDFs for inference
output/                 # Output JSONs (predictions)
data/
  raw/                  # Raw PDFs for dataset creation
  gold/                 # Manually labeled gold JSONs
  weak/                 # Weakly labeled data (optional)
  splits/               # Train/val/test splits (optional)
  multilingual_samples/ # PDFs for multilingual testing
models/                 # Trained LightGBM model
notebooks/              # Analysis and error analysis notebooks
scripts/                # Utility and judge simulation scripts
src/r1a/                # Training, evaluation, and labeling scripts
utils/                  # Core feature extraction and heading logic
```

---

## Quick Start
### 1. Inference
1. Place PDFs in `input/`.
2. Run:
   ```bash
   python process_pdfs.py
   ```
3. Find extracted headings in `output/*.json`.

### 2. Dataset Creation & Labeling
- Ensure dataset folders:
  ```bash
  python src/r1a/make_dataset.py
  ```
- Place raw PDFs in `data/raw/`.
- For each PDF, run:
  ```bash
  python src/r1a/label_ui.py --pdf data/raw/yourfile.pdf --csv data/gold/yourfile.csv --out data/gold/yourfile.json
  # Fill in the CSV, then:
  python src/r1a/label_ui.py --pdf data/raw/yourfile.pdf --csv data/gold/yourfile.csv --out data/gold/yourfile.json --import_csv
  ```

### 3. Training the Classifier
- After labeling, run:
  ```bash
  python src/r1a/train_heading_classifier.py
  ```
- Model is saved to `models/heading_classifier.pkl`.

### 4. Evaluation
- Single file:
  ```bash
  python src/r1a/evaluate.py --pred output/sample.json --gold data/gold/sample.json
  ```
- Batch evaluation:
  ```bash
  python src/r1a/batch_evaluate.py --pred_dir output --gold_dir data/gold
  ```

### 5. Judge Simulation (Docker, CPU-only, no internet)
- Build and run with timing and evaluation:
  ```bash
  bash scripts/judge_sim_r1a.sh input output data/gold
  ```

### 6. Multilingual Testing
- Place PDFs in `data/multilingual_samples/`.
- Run:
  ```bash
  python src/r1a/test_multilingual.py
  ```

### 7. Error Analysis
- Open `notebooks/error_analysis.ipynb` for confusion matrix, feature importance, and misclassification review.

---

## Output Format
Each output JSON contains:
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Heading Text",
      "page": 1,
      "confidence": 0.98,
      "children": [ ... ]
    },
    ...
  ]
}
```

---

## Requirements
- Python 3.10+
- See `requirements.txt` for all dependencies (pdfplumber, spacy[small], scipy, numpy, pandas, lightgbm, langdetect, polyglot, etc.)
- For Docker: `docker` (CPU-only, no internet required after build)

---

## Hackathon Constraints
- **CPU-only**: No GPU dependencies or requirements
- **Model size**: ≤200MB (LightGBM + spaCy small model)
- **Runtime**: ≤10 seconds per PDF (typical)
- **No internet access** during inference

---

## Contact / Support
For questions or issues, please contact the repository maintainer or open an issue.
