from fastapi import FastAPI, WebSocket
from fastapi.responses import Response

app = FastAPI()

@app.post("/webhook", response_class=Response)
async def webhook():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="wss://web-production-1ca6a.up.railway.app/media" />
        </Connect>
    </Response>"""
    return Response(content=xml_content, media_type="application/xml")

@app.websocket("/media")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket conectado. Recibiendo datos...")

    try:
        while True:
            data = await websocket.receive()
            
            # 📌 Imprimimos lo que Twilio está enviando
            print(f"📥 Recibido: {data}")

            # 🔍 Verificamos si es texto o bytes
            if "text" in data:
                print("📜 Twilio envió texto:", data["text"])
            elif "bytes" in data:
                print(f"🔊 Twilio envió {len(data['bytes'])} bytes de audio")

    except Exception as e:
        print(f"❌ Error en WebSocket: {e}")
    finally:
        print("🔌 WebSocket desconectado")
