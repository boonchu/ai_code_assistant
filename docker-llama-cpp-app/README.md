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
    "stream": true
}'
```
