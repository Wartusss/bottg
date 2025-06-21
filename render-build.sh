#!/usr/bin/env bash

# Install specific Python version if needed
echo "🔧 Installing Python 3.10.12 manually..."
pyenv install 3.10.12
pyenv global 3.10.12
python --version

# Install dependencies
pip install -r requirements.txt
