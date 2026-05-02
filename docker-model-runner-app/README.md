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
- Add Docker LLM model pulling support (model-runner from Docker Desktop)
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
```
- Review docker image types [here](https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md) llama.cpp. When you can see nvidia-smi with good output, then environment setup has no issue.
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

docker run --gpus 1 ghcr.io/ggml-org/llama.cpp:server-cuda --port 8080 --host 0.0.0.0 -n 512 --n-gpu-layers 1 --docker-repo ai/gemma4:E4B

#### Before `running docker compose up -d`
- Note that the current docker compose still need to tune llama.cpp to incorparate with model in docker model-runner. not sure yet if this is the right way to do so when use docker model with llama.cpp. 
- Create directory llama_cache and set the Setgid Bit (For Shared Access)
```
mkdir -p llama_cache/slots
chmod -R 2775 ./llama_cache
sudo chgrp -R $(id -g) ./llama_cache
```
- When model download start, you should see this:
```
$ rg --files  llama_cache/

llama_cache/ai_gemma4_E4B.gguf.downloadInProgress
```
- Watch logs in docker model.
```
docker model logs -f
```
#### Find best model to fit your local machine
```
git clone git@github.com:AlexsJones/llmfit.git
cd llmfit

# pipe to jq to find best "fit" model for "llama.cpp".
$ docker build -t llmfit-tui-image . && docker run --gpus all -it llmfit-tui-image | jq '.models[] | select(.runtime | contains("llama.cpp"))' | jq -r 

  "name": "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
  "notes": [
    "Context capped at 8192 tokens for estimation (model supports up to 6553600; use --max-context to override)",
    "GPU: model loaded into VRAM",
    "MoE: all 64 experts loaded in VRAM (optimal)",
    "Baseline estimated speed: 119.2 tok/s"
  ],
  "parameter_count": "15.7B",

  "name": "Intel/Qwen3-Coder-Next-int4-AutoRound",
  "notes": [
    "Context capped at 8192 tokens for estimation (model supports up to 262144; use --max-context to override)",
    "GPU: model loaded into VRAM",
    "MoE: all 512 experts loaded in VRAM (optimal)",
    "Best quantization for hardware: Q6_K (model default: Q4_K_M)",
    "Baseline estimated speed: 139.4 tok/s"
  ],
  "parameter_count": "11.8B",
```