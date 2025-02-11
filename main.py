from fastapi import FastAPI
from fastapi.responses import XMLResponse

app = FastAPI()

@app.post("/incoming_call")
async def incoming_call():
    response = """
    <Response>
        <Say voice="alice">Hola, esta es una prueba de Twilio con FastAPI.</Say>
        <Hangup/>
    </Response>
    """
    return XMLResponse(content=response)
