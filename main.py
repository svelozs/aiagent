import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import speech_v1p1beta1 as speech
from fastapi import FastAPI, WebSocket
from fastapi.responses import Response

# Autenticación para Google Speech-to-Text
google_credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if google_credentials_json:
    credentials_info = json.loads(google_credentials_json)  # Convertir el string a un diccionario
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    client = speech.SpeechClient(credentials=credentials)
else:
    print("❌ No se encuentran las credenciales.")
    client = None

# Autenticación para Google Sheets (u otros servicios)
credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if credentials_json:
    credentials_info = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
else:
    raise ValueError("No se encuentran las credenciales para Google Sheets. Asegúrate de haber configurado correctamente la variable de entorno 'GOOGLE_APPLICATION_CREDENTIALS_JSON'.")

# Construir el cliente de la API de Google Sheets
service = build('sheets', 'v4', credentials=credentials)

# Ejemplo de llamada para leer datos de una hoja de cálculo
spreadsheet_id = 'your-spreadsheet-id'
range_name = 'Sheet1!A1:D10'
result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()

values = result.get('values', [])
if not values:
    print('No data found.')
else:
    for row in values:
        print(row)

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

    if not client:
        await websocket.send_text("❌ No se pudieron cargar las credenciales.")
        return

    try:
        while True:
            data = await websocket.receive()

            print(f"📥 Recibido: {data}")

            if "text" in data:
                print("📜 Twilio envió texto:", data["text"])
            elif "bytes" in data:
                print(f"🔊 Twilio envió {len(data['bytes'])} bytes de audio")

                audio = speech.RecognitionAudio(content=data["bytes"])

                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="es-ES",
                )

                response = client.recognize(config=config, audio=audio)

                for result in response.results:
                    transcript = result.alternatives[0].transcript
                    print(f"🎤 Transcripción: {transcript}")

                    await websocket.send_text(f"Respuesta transcrita: {transcript}")

    except Exception as e:
        print(f"❌ Error en WebSocket: {e}")
    finally:
        print("🔌 WebSocket desconectado")
