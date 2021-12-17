## Getting Started

Python
```
python -m virtualenv .venv
.venv/Scripts/activate.ps1
pip install -r requirements.txt -r requirements.dev.txt
cp sample.env .env
```

Docker
```
docker compose build
docker compose up -d
```

Ngrok
```
ngrok http 8000
```
