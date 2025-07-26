#!/usr/bin/env python3
"""
Inference script for heading extraction from PDFs.
Uses hybrid heuristic + ML approach if model is available.
"""

import os
import json
import time
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional

# Import utility functions
from utils.extract_text import extract_elements
from utils.title_detector import detect_title
from utils.detect_headings import detect_heading_structure
from utils.json_builder import build_outline_json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def load_model(model_path: str) -> Optional[Dict]:
    """Load the trained LightGBM model if available."""
    try:
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            logging.info(f"Loaded model from {model_path}")
            return model_data
        else:
            logging.warning(f"Model not found at {model_path}, using heuristic-only approach")
            return None
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return None

def predict_with_model(elements: List[Dict], model_data: Dict) -> Dict:
    """Use trained model to predict heading structure."""
    try:
        from utils.detect_headings import extract_features
        import numpy as np
        import lightgbm as lgb
        
        # Extract features
        features = extract_features(elements)
        
        # Make predictions
        model = model_data['model']
        label_map = model_data['label_map']
        predictions = model.predict(features)
        
        # Convert predictions back to labels
        reverse_label_map = {v: k for k, v in label_map.items()}
        predicted_labels = [reverse_label_map[pred] for pred in predictions]
        
        # Build heading structure
        headings = []
        for i, (element, label) in enumerate(zip(elements, predicted_labels)):
            if label != 'O':
                headings.append({
                    'level': label,
                    'text': element['text'],
                    'page': element.get('page', 1),
                    'confidence': 0.8,  # Default confidence for model predictions
                    'children': []
                })
        
        return {'headings': headings, 'language': 'en'}
        
    except Exception as e:
        logging.error(f"Error in model prediction: {e}")
        return {'headings': [], 'language': 'en'}

def infer_single_pdf(pdf_path: Path, output_dir: Path, model_data: Optional[Dict] = None) -> Dict:
    """Process a single PDF and return results."""
    start_time = time.time()
    
    try:
        # Extract text elements
        elements = extract_elements(pdf_path)
        
        # Detect title
        title = detect_title(elements, pdf_path)
        
        # Detect heading structure
        if model_data:
            # Use hybrid approach with model
            outline = predict_with_model(elements, model_data)
        else:
            # Use heuristic-only approach
            outline = detect_heading_structure(elements)
        
        # Build output JSON
        result = build_outline_json(pdf_path, title, outline, output_dir)
        
        runtime = time.time() - start_time
        logging.info(f"Processed {pdf_path.name} in {runtime:.2f}s")
        
        return result
        
    except Exception as e:
        logging.error(f"Error processing {pdf_path.name}: {e}")
        # Return placeholder JSON on error
        return {
            'title': '',
            'outline': [],
            'error': str(e)
        }

def main():
    """Main inference function."""
    input_dir = Path("input")
    output_dir = Path("output")
    model_path = Path("models/heading_classifier.pkl")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load model if available
    model_data = load_model(str(model_path))
    
    # Process all PDFs in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logging.warning("No PDF files found in input/ directory")
        return
    
    total_start = time.time()
    
    for pdf_file in pdf_files:
        logging.info(f"Processing: {pdf_file.name}")
        result = infer_single_pdf(pdf_file, output_dir, model_data)
        
        # Save result to JSON file
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Saved results to {output_file}")
    
    total_runtime = time.time() - total_start
    logging.info(f"Total processing time: {total_runtime:.2f}s")
    
    # Validate runtime constraint (≤10s for typical PDFs)
    if total_runtime > 10.0:
        logging.warning(f"Runtime ({total_runtime:.2f}s) exceeds 10s constraint")
    else:
        logging.info("Runtime constraint satisfied (≤10s)")

if __name__ == "__main__":
    main() 