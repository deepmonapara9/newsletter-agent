#!/bin/bash

# Newsletter Agent Setup Script
echo "🚀 Setting up Newsletter Agent..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Check if uv is installed
if command -v uv >/dev/null 2>&1; then
    echo "✅ uv is already installed"
else
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create virtual environment using uv
echo "� Creating virtual environment with uv..."
uv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies using uv
echo "📚 Installing dependencies with uv..."
uv pip install -r requirements.txt

# Install development dependencies (optional)
echo "�️  Installing development dependencies..."
uv pip install -e ".[dev]"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual API keys and configuration"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p generated
mkdir -p temp

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate the environment: source .venv/bin/activate"
echo "3. Start the server: uvicorn main:app --reload"
echo ""
echo "📖 Check README.md for detailed configuration instructions"
echo ""
echo "💡 Pro tip: Use 'uv pip install <package>' for lightning-fast package installation!"
