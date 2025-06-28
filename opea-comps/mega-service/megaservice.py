from comps import MicroService, ServiceOrchestrator, ServiceType, ServiceRoleType
import os

# Service Configuration
DUMMY_SERVICE_HOST_IP = os.getenv("DUMMY_SERVICE_HOST_IP", "127.0.0.1")
DUMMY_SERVICE_PORT = int(os.getenv("DUMMY_SERVICE_PORT", 5000))

class MyFirstMegaService:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.megaservice = ServiceOrchestrator()
        self.service = None

    def add_microservice(self):
        dummy_service = MicroService(
            name="dummy_service",
            host=DUMMY_SERVICE_HOST_IP,
            port=DUMMY_SERVICE_PORT,
            endpoint="/health",  # Our dummy service has this endpoint
            use_remote_service=True,
            service_type=ServiceType.LLM,  # Using LLM as an example
        )
        self.megaservice.add(dummy_service)

    async def handle_request(self, request: dict):
        # Handle incoming requests
        result_dict, runtime_graph = await self.megaservice.schedule(
            initial_inputs=request
        )
        return result_dict

    def start(self):
        self.add_microservice()
        print(f"🚀 Starting MegaService at {self.host}:{self.port}")
        
        # Create a MicroService for our mega service
        self.service = MicroService(
            name=self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint="/process",
            input_datatype=dict,
            output_datatype=dict,
        )
        
        # Add route handler
        self.service.add_route("/process", self.handle_request, methods=["POST"])
        
        # Start the service
        self.service.start()

if __name__ == "__main__":
    service = MyFirstMegaService() 
    service.start()
