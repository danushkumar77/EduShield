#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python requirements
pip install -r requirements.txt

# Initialize database schema and pre-populate test users
python -c "from utils.database import init_db; init_db()"

echo "[+] Build script execution completed successfully!"
