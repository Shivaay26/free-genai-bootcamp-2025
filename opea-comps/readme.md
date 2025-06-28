### Basic Installation
1. Install docker
2. Copy the docker-compose.yml from https://github.com/opea-project/GenAIComps/tree/main/comps/third_parties/ollama
3. add the required values in a .env file by using chatgpt
4. run it using :- "docker compose -d"
5. Now for installing the required model say ollama , perform the following tasks:-
6. "docker exec -it ollama-server bash"
7. "ollama pull deepseek-r1:1.5b"
8. "exit"
10. now you can try to check the endpoint using:- "curl http://localhost:8008/api/generate \
  -d '{"model":"deepseek-r1:1.5b","prompt":"Say hello"}' \
  -H "Content-Type: application/json"
"
