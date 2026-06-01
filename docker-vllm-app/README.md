#### Add HF Download folder
```
mkdir -p models_cache/huggingface/hub
sudo chmod -R 2775 ./models_cache
sudo chgrp -R $(id -g) ./models_cache
```

#### Avoid to get models from inside docker, Download HF models with 'hf' cli
```
export HF_TOKEN=<TOKEN>
export HF_HUB_DISABLE_XET=1
export HF_HUB_DOWNLOAD_TIMEOUT=300

# https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
hf download mistralai/Mistral-7B-v0.1  --cache-dir ../models_cache/huggingface/hub/
hf models info mistralai/Mistral-7B-v0.1
```

#### Checking Cache from HF
```
hf cache list --cache-dir ../models_cache/huggingface/hub/
```

#### Testing 

- Use curl to test streaming (Interactive) mode. Users can read as the model types, making the system feel faster.
```
curl -qs http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d '{
        "messages": [
            {
                "role": "system",
                "content": "You are a senior TypeScript architect. All code examples must be strictly typed, follow the latest TypeScript standards, and use clear annotations."
            },
            {
                "role": "user",
                "content": "Show me a basic Next.js App Router component fetching data, following modern best practices."
            }
        ],
        "temperature": 0.5,
        "top_p": 0.85,
        "top_k": 40
}' | jq -r '.choices[0].message.content' | bat -l md
```

#### Running in PI
```
cat ~/.pi/agent/models.json
{
  "providers": {
    "vllm": {
      "baseUrl": "http://localhost:8080/v1",
      "api": "openai-completions",
      "apiKey": "vllm",
      "models": [
        { "id": "mistralai/Mistral-7B-v0.1" }
      ]
    }
  }
}

cat ~/.pi/agent/settings.json
{
  "lastChangelogVersion": "0.75.5",
  "packages": [
    "npm:pi-web-access",
    "npm:pi-subagents"
  ],
  "agent": {
    "compactionThreshold": 7168,
    "maxCompactionTokens": 2048
  }
}

pi update

pi
```

#### Benchmark
```
brew install uv
uv init benchmark
cd benchmark
uv add llama-benchy

uv run llama-benchy --base-url http://localhost:8080/v1 --model mistralai/Mistral-7B-v0.1 --pp 1024  --tg 512 --runs 3

uv run llama-benchy --base-url http://localhost:8080/v1 --model mistralai/Mistral-7B-v0.1 --pp 1024  --tg 256 --depth 8192  --runs 3

uv run llama-benchy --base-url http://localhost:8080/v1 --model mistralai/Mistral-7B-v0.1 --enable-prefix-caching --pp 1024 --depth 4096

pp (Prompt Processing): Reported in tokens per second (\(t/s\)). This isolates how fast vLLM absorbs incoming text or massive histories.

tg (Token Generation): Output tokens per second (\(t/s\)). Tells you the fluid scrolling speed experienced by the agent loop.

est_ppt (Estimated Prompt Processing Time): The underlying raw compute time required to handle the context, factoring out networking/API overhead layer lag
```
