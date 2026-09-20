from fastapi import FastAPI, Request
from datetime import datetime, timezone

app = FastAPI(title="JARVIS Kiwify Webhook")


@app.get("/")
def health():
    return {
        "status": "online",
        "service": "jarvis-kiwify-webhook"
    }


@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()

    print({
        "received_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload
    })

    return {
        "received": True
  }
