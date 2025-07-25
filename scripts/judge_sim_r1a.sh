#!/bin/bash
set -e

INPUT_DIR=$(realpath "$1")
OUTPUT_DIR=$(realpath "$2")
GOLD_DIR=$(realpath "$3")
IMG_NAME=adobe_r1a_eval

# Build Docker image
DOCKER_BUILDKIT=1 docker build -t $IMG_NAME .

# Run inference in Docker, timing it
start=$(date +%s)
docker run --rm \
  -v "$INPUT_DIR":/app/input \
  -v "$OUTPUT_DIR":/app/output \
  $IMG_NAME
end=$(date +%s)
runtime=$((end-start))

echo "Inference runtime: ${runtime}s"

# Evaluate
python3 src/r1a/batch_evaluate.py --pred_dir "$OUTPUT_DIR" --gold_dir "$GOLD_DIR" 