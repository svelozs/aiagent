import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import speech_v1p1beta1 as speech
from fastapi import FastAPI, WebSocket
from fastapi.responses import Response

# Cargar credenciales desde las variables de entorno
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not google_credentials_json:
    raise ValueError("❌ No se encuentran las credenciales de Google.")

credentials_info = json.loads(google_credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Inicializar clientes de Google
speech_client = speech.SpeechClient(credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)

# Configuración de la hoja de cálculo para guardar logs
SPREADSHEET_ID = "your-spreadsheet-id"
RANGE_NAME = "Logs!A:D"

def guardar_en_sheets(datos):
    body = {"values": [datos]}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()

# Inicializar FastAPI
app = FastAPI()

@app.post("/webhook", response_class=Response)
async def webhook():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="wss://web-production-1ca6a.up.railway.app" />
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

            if "bytes" in data:
                audio = speech.RecognitionAudio(content=data["bytes"])
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="es-ES",
                )
                response = speech_client.recognize(config=config, audio=audio)
                
                for result in response.results:
                    transcript = result.alternatives[0].transcript
                    print(f"🎤 Transcripción: {transcript}")
                    await websocket.send_text(f"Respuesta transcrita: {transcript}")
                    
                    # Guardar en Google Sheets
                    guardar_en_sheets(["Twilio", transcript])
    except Exception as e:
        print(f"❌ Error en WebSocket: {e}")
    finally:
        print("🔌 WebSocket desconectado")
