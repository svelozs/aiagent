from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
import os
from google.cloud import speech_v1p1beta1 as speech
from google.protobuf.json_format import MessageToDict

# Configurar la API Key de Google
os.environ["GOOGLE_API_KEY"] = "AIzaSyAy9IV7l1Xj6_VW84qzX0CeYrv7A6A_LF0"

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

    # Inicializar el cliente de Google Speech-to-Text
    client = speech.SpeechClient()

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

                # Convertir los bytes de audio en texto usando Google Cloud Speech
                audio = speech.RecognitionAudio(content=data["bytes"])

                # Configuración de la solicitud (si es necesario, ajusta el idioma o detalles)
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="es-ES",  # Asegúrate de que sea el idioma adecuado
                )

                # Realizar la transcripción de audio a texto
                response = client.recognize(config=config, audio=audio)

                # Extraer el texto transcrito
                for result in response.results:
                    transcript = result.alternatives[0].transcript
                    print(f"🎤 Transcripción: {transcript}")

                    # Aquí puedes agregar lógica para procesar el texto y responder
                    # Usar la transcripción para enviar una respuesta dinámica
                    # por ejemplo:
                    # xml_response = """<Response><Say>{}</Say></Response>".format(transcript)
                    
                    # Enviar la respuesta (esta es solo un ejemplo)
                    await websocket.send_text(f"Respuesta transcrita: {transcript}")

    except Exception as e:
        print(f"❌ Error en WebSocket: {e}")
    finally:
        print("🔌 WebSocket desconectado")
