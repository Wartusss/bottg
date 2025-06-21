#!/usr/bin/env bash
echo "----> Using Python 3.10.12 manually"
pyenv install 3.10.12
pyenv global 3.10.12
pip install -r requirements.txt