#### Preparing image
- [How to build it locally](https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md#building-docker-locally) 
```
git clone https://github.com/ggml-org/llama.cpp.git
docker compose build
docker compose up -d 
```
#### Testing 

- Use curl to test streaming (Interactive) mode. Users can read as the model types, making the system feel faster.
```
curl http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d '{
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello!"
        }
    ],
    "top_k": 40,
    "top_p": 0.95,
    "min_p": 0.05,
    "frequency_penalty": 0.1
}'
```
