from comps import MicroService, ServiceOrchestrator, ServiceType, ServiceRoleType
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        logger.info(f"Registering echo service at {DUMMY_SERVICE_HOST_IP}:{DUMMY_SERVICE_PORT}")
        echo_service = MicroService(
            name="echo_service",
            host=DUMMY_SERVICE_HOST_IP,
            port=DUMMY_SERVICE_PORT,
            endpoint="/echo",
            use_remote_service=True,
            service_type=ServiceType.LLM,
            input_datatype=dict,
            output_datatype=dict
        )
        self.megaservice.add(echo_service)
        logger.info("Echo service registered successfully")

    async def handle_request(self, request: dict):
        logger.info(f"Received request: {request}")
        try:
            result_dict, runtime_graph = await self.megaservice.schedule(
                initial_inputs=request
            )
            logger.info(f"Service response received: {result_dict}")
            
            # Get the response from the echo service
            service_key = "echo_service/MicroService"
            if service_key in result_dict:
                response = result_dict[service_key]
                
                # If it's a StreamingResponse, get the content
                if hasattr(response, "body"):
                    body = await response.body()
                    logger.info(f"Extracted response body: {body}")
                    return body
                
                # If it's a regular response, return it directly
                return response
                
            logger.error("No valid response from echo service")
            return {"error": "No response from echo service"}
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {"error": f"Failed to process request: {str(e)}"}

    def start(self):
        logger.info("Starting MegaService...")
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
