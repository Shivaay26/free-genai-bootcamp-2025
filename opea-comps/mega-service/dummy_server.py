#!/usr/bin/env python3
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn
import json

app = FastAPI()

class EchoRequest(BaseModel):
    content: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/echo")
async def echo(request: Request):
    try:
        # Get the request body
        body = await request.body()
        # Convert bytes to string
        body_str = body.decode('utf-8')
        # Return the same content
        return body_str
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run it:
    # uvicorn dummy_service:app --host 127.0.0.1 --port 5000

if __name__ == "__main__":
    print("Starting dummy server on http://127.0.0.1:5000")
    uvicorn.run(app, host="127.0.0.1", port=5000)
