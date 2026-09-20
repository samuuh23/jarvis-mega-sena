from fastapi import FastAPI, Request
from datetime import datetime, timezone
import json
import os

app = FastAPI(title="JARVIS Kiwify Webhook")

# Arquivo local para registrar os eventos recebidos.
# Nesta etapa é apenas um registro temporário.
EVENTS_FILE = "kiwify_events.json"


def save_event(event):
    events = []

    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, "r", encoding="utf-8") as file:
                events = json.load(file)

            if not isinstance(events, list):
                events = []

        except Exception:
            events = []

    events.append(event)

    # Mantém somente os últimos 500 eventos
    events = events[-500:]

    with open(EVENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, ensure_ascii=False, indent=2)


@app.get("/")
def health():
    return {
        "status": "online",
        "service": "jarvis-kiwify-webhook"
    }


@app.post("/webhook")
async def receive_webhook(request: Request):
    received_at = datetime.now(timezone.utc).isoformat()

    # Lê o corpo original recebido
    raw_body = await request.body()

    # Tenta interpretar como JSON
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        payload = {
            "raw_body": raw_body.decode("utf-8", errors="replace")
        }

    # Guarda informações básicas do recebimento
    event = {
        "received_at": received_at,
        "content_type": request.headers.get("content-type"),
        "payload": payload
    }

    save_event(event)

    # Log no Render
    print("========================================")
    print("JARVIS WEBHOOK RECEBIDO")
    print("Horário:", received_at)
    print("Payload:", json.dumps(payload, ensure_ascii=False))
    print("========================================")

    return {
        "received": True
    }
