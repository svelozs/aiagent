from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

@app.post("/webhook", response_class=Response)
async def webhook(request: Request):
    # Verifica que Twilio esté enviando la solicitud
    print("Recibiendo solicitud de Twilio:", await request.json())
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say language="es-ES" voice="Polly.Latino-ES">Hola, gracias por llamar. ¿En qué puedo ayudarte?</Say>
    </Response>"""
    
    return Response(content=xml_content, media_type="application/xml")
