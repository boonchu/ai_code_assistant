#### Add HF Download folder
```
mkdir -p llama_cache/huggingface/hub
chmod -R 2775 ./llama_cache
sudo chgrp -R $(id -g) ./llama_cache
```

#### Avoid to get models from inside docker, Download HF models with 'hf' cli
```
export HF_TOKEN=<TOKEN>
export HF_HUB_DISABLE_XET=1
export HF_HUB_DOWNLOAD_TIMEOUT=300
hf models info Qwen/Qwen3.5-4B
hf download Qwen/Qwen3.5-4B --cache-dir ../llama_cache/huggingface/hub/
```

#### Checking Cache from HF
```
hf cache list --cache-dir ../llama_cache/huggingface/hub/

ID                              SIZE LAST_ACCESSED     LAST_MODIFIED     REFS
----------------------------- ------ ----------------- ----------------- ----
model/Qwen/Qwen3.5-4B           9.3G 22 minutes ago    1 minute ago      main
model/z-lab/Qwen3.5-4B-DFlash 424.0K a few seconds ago a few seconds ago main

Found 2 repo(s) for a total of 2 revision(s) and 9.3G on disk.
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
    "stream": true
}'
```
