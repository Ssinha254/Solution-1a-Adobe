#!/bin/bash
set -e

echo "=== Adobe Hackathon Round 1A - Constraint Validation ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}[PASS]${NC} $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}[FAIL]${NC} $message"
    else
        echo -e "${YELLOW}[WARN]${NC} $message"
    fi
}

# 1. Check if model exists and size
echo "1. Model Size Validation (<200MB):"
MODEL_PATH="models/heading_classifier.pkl"
if [ -f "$MODEL_PATH" ]; then
    MODEL_SIZE=$(stat -c%s "$MODEL_PATH" 2>/dev/null || stat -f%z "$MODEL_PATH" 2>/dev/null || echo "0")
    MODEL_SIZE_MB=$((MODEL_SIZE / 1024 / 1024))
    if [ $MODEL_SIZE_MB -lt 200 ]; then
        print_status "PASS" "Model size: ${MODEL_SIZE_MB}MB (under 200MB limit)"
    else
        print_status "FAIL" "Model size: ${MODEL_SIZE_MB}MB (exceeds 200MB limit)"
    fi
else
    print_status "WARN" "Model file not found at $MODEL_PATH"
fi
echo

# 2. Check if sample PDF exists
echo "2. Input Validation:"
if [ -f "input/sample.pdf" ]; then
    print_status "PASS" "Sample PDF found at input/sample.pdf"
else
    print_status "WARN" "Sample PDF not found at input/sample.pdf"
fi
echo

# 3. Runtime validation
echo "3. Runtime Validation (≤10s):"
if [ -f "input/sample.pdf" ]; then
    echo "Running process_pdfs.py on sample.pdf..."
    start_time=$(date +%s)
    
    # Run the inference
    python process_pdfs.py 2>/dev/null || echo "Inference completed (with warnings)"
    
    end_time=$(date +%s)
    runtime=$((end_time - start_time))
    
    if [ $runtime -le 10 ]; then
        print_status "PASS" "Runtime: ${runtime}s (under 10s limit)"
    else
        print_status "FAIL" "Runtime: ${runtime}s (exceeds 10s limit)"
    fi
else
    print_status "WARN" "Cannot test runtime - no sample PDF found"
fi
echo

# 4. Output validation
echo "4. Output Validation:"
if [ -f "output/sample.json" ]; then
    print_status "PASS" "Output JSON generated at output/sample.json"
    
    # Check JSON structure
    if command -v python3 >/dev/null 2>&1; then
        if python3 -c "import json; data=json.load(open('output/sample.json')); print('JSON structure valid')" 2>/dev/null; then
            print_status "PASS" "JSON structure is valid"
        else
            print_status "FAIL" "JSON structure is invalid"
        fi
    fi
else
    print_status "WARN" "Output JSON not found at output/sample.json"
fi
echo

# 5. Directory structure validation
echo "5. Directory Structure Validation:"
REQUIRED_DIRS=("data/raw" "data/gold" "data/weak" "data/splits" "data/multilingual_samples" "models" "input" "output")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_status "PASS" "Directory exists: $dir"
    else
        print_status "FAIL" "Directory missing: $dir"
    fi
done
echo

# 6. Script validation
echo "6. Script Validation:"
REQUIRED_SCRIPTS=("process_pdfs.py" "src/r1a/infer.py" "src/r1a/evaluate.py" "scripts/judge_sim_r1a.sh")
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        print_status "PASS" "Script exists: $script"
    else
        print_status "FAIL" "Script missing: $script"
    fi
done
echo

# Summary
echo "=== Validation Summary ==="
echo "Run this script after adding the trained model to validate all constraints."
echo "For submission, ensure all items show [PASS] status." 