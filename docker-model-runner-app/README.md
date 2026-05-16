#### Spending weekends to explore how AI assist me coding...

#### Setup
- Use Linux WSL2 on Windows
- Ensure to have GPU, project has tested with 12GB RTX-4070
- Apply `Continue` or `Cline` extension from vscode and have settings to use gemma4:E4B
    - `Continue` is better since it pass through my prompt to service.
- Can monitor GPU when docker services started, http://localhost:1312
- Ensure [Nvidia Tool Kit](https://oneuptime.com/blog/post/2026-01-16-docker-nvidia-gpu-ai-ml/view#ubuntu-debian) installed
```
# Add NVIDIA package repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install the toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker
sudo systemctl restart docker
```
- When you can see nvidia-smi with good output, then environment setup has no issue.
```
$ docker run --rm -it --gpus all nvidia/cuda:13.0.2-devel-ubuntu24.04 nvidia-smi
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 595.58.04              Driver Version: 596.21         CUDA Version: 13.2     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4070        On  |   00000000:01:00.0  On |                  N/A |
|  0%   36C    P8              5W /  200W |    1210MiB /  12282MiB |      1%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
```
- Add Docker Model Runner support
```
# support docker model-runner plugin
sudo apt-get update
sudo apt-get install docker-model-plugin
docker model version
```
- Pulling using document [here](https://medium.com/google-cloud/running-an-ai-agent-locally-adk-gemma-4-and-docker-model-runner-95ca9e6f506d), and [setup docker model runner](https://medium.com/@bhaskaro/docker-model-runner-demystified-a-practical-guide-to-running-local-llms-like-containers-895af3ddcb0c) and [docker model pull](https://theaiops.substack.com/p/docker-model-runner-pull-llms-from) and llm image info [offical gemma4 in docker hub](https://hub.docker.com/r/ai/gemma4)
```
docker model pull ai/gemma4:E4B

$ docker model list
MODEL NAME  PARAMETERS  QUANTIZATION   ARCHITECTURE  MODEL ID      CREATED      CONTEXT  SIZE
gemma4:E4B  7.52B       MOSTLY_Q4_K_M  gemma4        1163f19dcd97  2 weeks ago           4.74GiB

$ docker model show gemma4:E4B | head -10
Model:       sha256:1163f19dcd973b865c35d8e1a2c03736f4eb0a98c71e2b4425b7f84d183a423f
Tags:        docker.io/ai/gemma4:E4B
Created:     2026-04-08T08:44:04-07:00

Format:       gguf
Architecture: gemma4
Parameters:   7.52B
Size:         4.74GiB
Quantization: MOSTLY_Q4_K_M

# enable model runner
docker desktop enable model-runner --tcp 12434

$ curl 'http://127.0.0.1:12434/v1/models/gemma4:E4B' -s | jq
{
  "id": "docker.io/ai/gemma4:E4B",
  "object": "model",
  "created": 1775663044,
  "owned_by": "docker",
  "dmr": {
    "architecture": "gemma4",
    "parameters": "7.52B",
    "quantization": "MOSTLY_Q4_K_M",
    "size": "4.74GiB"
  }
}

# Send chat example to say hello.
curl http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/gemma4:E4B",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 20
  }'
```
#### Before `running docker compose up -d`
- Watch logs in docker model.
```
docker model logs -f
```
- Start `docker compose up -d`
#### Use the [first example](https://github.com/tosun-si/football-agent-adk-gemma-dmr/tree/main#) 
```
git clone https://github.com/tosun-si/football-agent-adk-gemma-dmr.git
direnv allow
uv sync
uv run adk web
```