#!/bin/bash
echo "Starting Textverarbeitung Platform (Option 2)..."

# Ensure we are in the correct directory
cd "$(dirname "$0")"

# Run with uv
export PYTHONPATH=$PWD
uv run uvicorn frontend.main:app --reload --port 8000
