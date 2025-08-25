# Quick Start (macOS)

cd /PATH/TO/ai-receptionist-pro/backend
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

cp .env.example .env
open -e .env   # fill TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, NUMBER_TENANT_MAP

./.venv/bin/python seed_demo.py
./.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8080
