#!/bin/bash
cd "$(dirname "$0")"
# Activate virtual environment and run the app
source venv/bin/activate
python3 desktop_app.py
deactivate
