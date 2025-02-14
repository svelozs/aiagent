from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()

@app.post("/webhook", response_class=Response)
async def webhook():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="Polly.Lupe" language="es-MX">Hola, mi nombre es Sonia Veloz y estoy aquí para atenderte. ¿En qué puedo ayudarte?</Say>
    </Response>"""
    return Response(content=xml_content, media_type="application/xml")
