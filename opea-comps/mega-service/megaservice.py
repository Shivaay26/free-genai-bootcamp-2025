import os
from fastapi import FastAPI
from comps import MicroService, ServiceOrchestrator, ServiceType

# Dummy values (Assuming the pseudo microservice is running on this port)
DUMMY_SERVICE_HOST_IP = os.getenv("DUMMY_SERVICE_HOST_IP", "127.0.0.1")
DUMMY_SERVICE_PORT = int(os.getenv("DUMMY_SERVICE_PORT", 5000))  # Ensure PORT is integer

class MyFirstMegaService:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.megaservice = ServiceOrchestrator()
        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy"}

        @self.app.post("/process")
        async def process_request(data: dict):
            return await self.megaservice.schedule(data)

    def add_microservice(self):
        dummy_service = MicroService(
            name="dummy_service",
            host=DUMMY_SERVICE_HOST_IP,
            port=DUMMY_SERVICE_PORT,
            endpoint="/health",  # Assuming your dummy microservice has a simple health endpoint
            use_remote_service=True,
            service_type=ServiceType.LLM,  # Just for example, could be anything
        )
        self.megaservice.add(dummy_service)

    def start(self):
        import uvicorn
        self.add_microservice()
        print(f"🚀 Starting MegaService at {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)

if __name__ == "__main__":
    service = MyFirstMegaService()
    service.start()
