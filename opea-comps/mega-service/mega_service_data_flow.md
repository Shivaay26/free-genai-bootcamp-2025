

## Mega-Service Architecture Documentation

## 1. Component Overview

### 1.1 Mega-Service Component (megaservice.py)

The mega-service acts as an orchestrator that manages and coordinates multiple microservices. It's implemented in `megaservice.py`.

#### Core Components:

1. **Service Configuration**
```python
DUMMY_SERVICE_HOST_IP = os.getenv("DUMMY_SERVICE_HOST_IP", "127.0.0.1")
DUMMY_SERVICE_PORT = int(os.getenv("DUMMY_SERVICE_PORT", 5000))
```
- Configures connection details for microservices
- Uses environment variables for configuration
- Falls back to default values if not set

2. **Main Service Class**
```python
class MyFirstMegaService:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.megaservice = ServiceOrchestrator()
        self.service = None
```
- Initializes the mega-service with host and port
- Creates a ServiceOrchestrator instance
- Sets up the main service object

3. **Service Registration**
```python
def add_microservice(self):
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
```
- Registers microservices with the orchestrator
- Configures service details like endpoint and data types
- Adds the service to the orchestrator

4. **Request Handling**
```python
async def handle_request(self, request: dict):
    # Schedule request using default flow
    result_dict, runtime_graph = await self.megaservice.schedule(
        initial_inputs=request
    )
    service_key = "echo_service/MicroService"
    if service_key in result_dict:
        response = result_dict[service_key]
        return response
```
- Processes incoming requests
- Schedules requests to microservices
- Returns the response from the appropriate service

### 1.2 Echo Service Component (dummy_server.py)

The echo service is a simple microservice that returns the same content it receives.

#### Core Components:

1. **FastAPI Setup**
```python
app = FastAPI()
```
- Creates a FastAPI application instance

2. **Health Check Endpoint**
```python
@app.get("/health")
def health_check():
    return {"status": "ok"}
```
- Provides a health check endpoint
- Returns status information

3. **Echo Endpoint**
```python
@app.post("/echo")
async def echo(request: Request):
    try:
        # Get the request body
        body = await request.body()
        # Convert bytes to string
        body_str = body.decode('utf-8')
        # Parse the JSON body
        body_json = json.loads(body_str)
        # Return the same content as JSON
        return body_json
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```
- Processes POST requests to /echo
- Handles request body as JSON
- Returns the same JSON content
- Includes error handling for invalid JSON and other errors

## 2. Data Flow

### 2.1 Request Flow

1. **Client Request**
```bash
curl -X POST http://localhost:8000/process -H "Content-Type: application/json" -d '{"message": "Hello World"}'
```

2. **Mega-Service Processing**
```python
# In megaservice.py
async def handle_request(self, request: dict):
    # 1. Receives request
    logger.info(f"Received request: {request}")
    
    # 2. Forwards to orchestrator
    result_dict, runtime_graph = await self.megaservice.schedule(
        initial_inputs=request
    )
    
    # 3. Gets response
    response = result_dict["echo_service/MicroService"]
    return response
```

3. **Echo Service Processing**
```python
# In dummy_server.py
@app.post("/echo")
async def echo(request: Request):
    # 1. Gets request body
    body = await request.body()
    
    # 2. Processes JSON
    body_json = json.loads(body.decode('utf-8'))
    
    # 3. Returns same content
    return body_json
```

### 2.2 Response Flow

1. **Echo Service Response**
- Returns JSON content directly
- No streaming response
- Proper JSON formatting

2. **Mega-Service Response**
- Gets response from echo service
- Returns it directly to client
- No additional processing needed

## 3. Adding New Microservices

To add a new microservice:

1. **Create Service Class**
```python
def add_new_service(self):
    new_service = MicroService(
        name="new_service_name",
        host="service_host",
        port=service_port,
        endpoint="/service_endpoint",
        use_remote_service=True,
        service_type=ServiceType.LLM,
        input_datatype=dict,
        output_datatype=dict
    )
    self.megaservice.add(new_service)
```

2. **Create Service Implementation**
```python
@app.post("/new_endpoint")
async def new_service(request: Request):
    # Your service logic here
    return {"result": "processed_data"}
```

3. **Update Request Handling**
```python
async def handle_request(self, request: dict):
    # Schedule request using default flow
    result_dict, runtime_graph = await self.megaservice.schedule(
        initial_inputs=request
    )
    # Get response from new service
    new_service_response = result_dict.get("new_service_name/MicroService")
    return new_service_response
```

## 3. Service-to-Service Communication

When adding new microservices, it's crucial to understand how services communicate with each other. The ServiceOrchestrator manages this communication through a directed acyclic graph (DAG) of services.

#### Example: Two Microservices Communication

1. **Service A (Producer)**
```python
@app.post("/process_data")
async def process_data(request: Request):
    # Process data
    result = {"processed_data": "some_value"}
    return result
```

2. **Service B (Consumer)**
```python
@app.post("/analyze_data")
async def analyze_data(request: Request):
    try:
        # Get input data from Service A
        data = await request.json()
        # Process the data
        analysis = analyze_function(data["processed_data"])
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3.2 Registering Services with Dependencies
```python
def add_services(self):
    # Register Service A
    service_a = MicroService(
        name="data_processor",
        host="service_a_host",
        port=9000,
        endpoint="/process_data",
        service_type=ServiceType.LLM,
        input_datatype=dict,
        output_datatype=dict
    )
    
    # Register Service B
    service_b = MicroService(
        name="data_analyzer",
        host="service_b_host",
        port=9001,
        endpoint="/analyze_data",
        service_type=ServiceType.LLM,
        input_datatype=dict,
        output_datatype=dict
    )
    
    # Add services
    self.megaservice.add(service_a)
    self.megaservice.add(service_b)
    
    # Define data flow using flow parameter
    self.megaservice.set_flow([
        {
            "service": "data_processor",
            "next": ["data_analyzer"]
        }
    ])
```

### 3.3 Data Flow Definition

The `flow` parameter in ServiceOrchestrator defines how data flows between services. Here's how it works:

1. **Basic Flow Definition**
```python
# Define a simple flow where Service B depends on Service A
flow = [
    {
        "service": "service_a",
        "next": ["service_b"]
    }
]
```

2. **Complex Flow with Multiple Paths**
```python
# Define multiple service paths
flow = [
    {
        "service": "data_collector",
        "next": ["data_processor", "data_validator"]
    },
    {
        "service": "data_processor",
        "next": ["data_analyzer"]
    },
    {
        "service": "data_validator",
        "next": ["data_analyzer"]
    }
]
```

3. **Flow with Conditions**
```python
# Define conditional flows
flow = [
    {
        "service": "data_processor",
        "next": [
            {"service": "data_analyzer", "condition": "success"},
            {"service": "error_handler", "condition": "error"}
        ]
    }
]
```

### 3.4 Request Handling with Flow

```python
async def handle_request(self, request: dict):
    # Schedule request using default flow
    result_dict, runtime_graph = await self.megaservice.schedule(
        initial_inputs=request
    )
    
    # Get results from each service
    service_a_result = result_dict.get("data_processor/MicroService")
    service_b_result = result_dict.get("data_analyzer/MicroService")
    
    # Combine results
    final_result = {
        "service_a": service_a_result,
        "service_b": service_b_result
    }
    return final_result
```

### 3.5 Best Practices for Flow Definition

1. **Flow Definition Location**
   - Define flows once using `set_flow()`
   - Use `schedule()` flow parameter only for request-specific overrides
   - Keep flow definitions centralized for easier maintenance

2. **Keep Flows Simple**
   - Avoid complex nested flows
   - Use clear service boundaries
   - Document flow paths

3. **Use Conditions Wisely**
   - Define clear success/failure paths
   - Implement fallbacks
   - Handle edge cases

4. **Monitor Flow Performance**
   - Track flow execution time
   - Monitor bottlenecks
   - Optimize critical paths

5. **Error Handling in Flows**
   - Define error paths
   - Implement retries
   - Handle timeouts

### 3.6 Example: Complex Flow with Conditions

```python
def add_complex_flow(self):
    # Define services
    service_a = MicroService(
        name="data_collector",
        host="collector_host",
        port=9000,
        endpoint="/collect",
        service_type=ServiceType.LLM
    )
    
    service_b = MicroService(
        name="data_processor",
        host="processor_host",
        port=9001,
        endpoint="/process",
        service_type=ServiceType.LLM
    )
    
    service_c = MicroService(
        name="data_analyzer",
        host="analyzer_host",
        port=9002,
        endpoint="/analyze",
        service_type=ServiceType.LLM
    )
    
    # Add services
    self.megaservice.add(service_a)
    self.megaservice.add(service_b)
    self.megaservice.add(service_c)
    
    # Define complex flow with conditions
    self.megaservice.set_flow([
        {
            "service": "data_collector",
            "next": [
                {"service": "data_processor", "condition": "success"},
                {"service": "error_handler", "condition": "error"}
            ]
        },
        {
            "service": "data_processor",
            "next": [
                {"service": "data_analyzer", "condition": "success"},
                {"service": "retry_processor", "condition": "retry"}
            ]
        }
    ])
```

{{ ... }}
