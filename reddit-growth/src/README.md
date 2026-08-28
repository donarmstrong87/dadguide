# Growth engine service

The service is intentionally split into discovery and publishing. Discovery can run on a schedule. Publishing is an explicit approval action and is not implemented as an unattended spam loop.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/discover.py
```

Reddit credentials are required for discovery. Keep `.env` out of git.
