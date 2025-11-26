#!/bin/bash
echo "Starting IFB Frontend V2 (Platform)..."

# Activate venv if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

export PYTHONPATH=$PWD
python -m uvicorn frontend.main:app --reload --port 8000
