docker-compose up --build -d && sleep 10
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -d 'username=demo&password=D3mo!Admin@2024' | jq -r '.access_token')

echo
echo 'run /v1/chat/completions'
echo
curl http://localhost:8000/v1/chat/completions \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "stream": false,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "messages": [
      {
        "role": "developer",
        "content": "You are a concise engineering assistant. Answer exclusively in Markdown format."
      },
      {
        "role": "user",
        "content": "Explain the architectural difference between a Process and a Thread."
      }
    ]
  }'

echo
echo
echo 'run /v1/models'
echo
curl http://localhost:8000/v1/models \
  -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN"
