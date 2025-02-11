from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()

@app.post("/webhook", response_class=Response)
async def webhook():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>Hola, gracias por llamar. ¿En qué puedo ayudarte?</Say>
    </Response>"""
    return Response(content=xml_content, media_type="application/xml")
