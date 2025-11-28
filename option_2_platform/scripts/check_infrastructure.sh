#!/bin/bash
echo "🔍 Checking Infrastructure..."

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not installed"
    exit 1
fi
echo "✅ Ollama installed: $(ollama --version)"

# Check Ollama server
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama server not running"
    exit 1
fi
echo "✅ Ollama server running"

# Check required model
if ! ollama list | grep -q "qwen2.5:7b"; then
    echo "❌ Model qwen2.5:7b not found"
    exit 1
fi
echo "✅ Model qwen2.5:7b available"

echo "🎉 Infrastructure check passed!"
