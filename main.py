from fastapi import FastAPI
from fastapi.responses import Response  # Cambié XMLResponse por Response

app = FastAPI()

@app.get("/", response_class=Response)
async def read_root():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <message>Hello, World!</message>"""
    return Response(content=xml_content, media_type="application/xml")
