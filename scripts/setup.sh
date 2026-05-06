#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env created — edit as needed"
fi
echo "Setup complete. Run: scripts/run_local.sh"
