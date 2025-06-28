# dummy_service.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Run it:
# uvicorn dummy_service:app --host 127.0.0.1 --port 5000
