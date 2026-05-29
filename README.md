### Spending weekends to explore how AI assist me coding...

#### Setup `docker-llama-cpp-app`
- Use Linux WSL2 on Windows.
- Have already setup WSL2 Linux Docker service.
- Must [Read this first](https://docs.nvidia.com/cuda/wsl-user-guide/index.html#cuda-support-for-wsl-2)

Once a Windows NVIDIA GPU driver is installed on the system, CUDA becomes available within WSL 2. The CUDA driver installed on Windows host will be stubbed inside the WSL 2 as libcuda.so, therefore users must not install any NVIDIA GPU Linux driver within WSL 2. One has to be very careful here as the default CUDA Toolkit comes packaged with a driver, and it is easy to overwrite the WSL 2 NVIDIA driver with the default installation. We recommend developers to use a separate CUDA Toolkit for WSL 2 (Ubuntu) available from the CUDA Toolkit Downloads page to avoid this overwriting. This WSL-Ubuntu CUDA toolkit installer will not overwrite the NVIDIA driver that was already mapped into the WSL 2 environment. Check latest version from web page.

```
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-13-3
```

- Ensure to have Nvidia GPU, project has tested with 12GB RTX-4070
- Ensure [Nvidia Tool Kit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed.
```
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
   ca-certificates \
   curl \
   gnupg2

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update

export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.19.1-1
  sudo apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}

sudo nvidia-ctk runtime configure --runtime=docker

sudo systemctl restart docker
```

- Running a sample workload with docker
```
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```


#### Setup extension with vscode
- Apply `Continue` or `Cline` extension from vscode and have settings to use gemma4:E4B
    - `Continue` is better since it pass through my prompt to service.
- Can monitor GPU when docker services started, http://localhost:1312
- Review docker image types [here](https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md) llama.cpp. When you can see nvidia-smi with good output, then environment setup has no issue.
```
docker run --gpus 1 ghcr.io/ggml-org/llama.cpp:server-cuda --port 8080 --host 0.0.0.0 -n 512 --n-gpu-layers 1 --docker-repo ai/gemma4:E4B
```

#### Before `running docker compose up -d`
- Note that the current docker compose still need to tune llama.cpp to incorparate with model in docker model-runner. not sure yet if this is the right way to do so when use docker model with llama.cpp. 
- Create directory models_cache and set the Setgid Bit (For Shared Access)
```
mkdir -p models_cache/slots
chmod -R 2775 ./models_cache
sudo chgrp -R $(id -g) ./models_cache
```
- Create docker network for connecting multiple docker projects.
```
docker network create ai-network
```
- When model download start, you should see this:
```
$ rg --files  models_cache/

models_cache/ai_gemma4_E4B.gguf.downloadInProgress
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
#### You can help to improve LLM with challenge in this project, ['Pelicans on a bicycle'](https://github.com/simonw/pelican-bicycle#pelicans-on-a-bicycle)
- Access http://localhost:8080/
- Type this Prompt `Generate an SVG of a pelican riding a bicycle`
- Dump SVG in vscode to see what image look like.
- Tune Llama.CPP in docker-compose.yml to get image better natually.

#### Testing with Opencode
- Setup with `npm install -g opencode-ai@latest`
- Copy `./configs/opencode.json` to `~/.config/opencode/opencode.json`. See this [link](https://docs.docker.com/guides/opencode-model-runner/) for details.
- Launch opencode and use Ctrl+p to enable prompt and use '/connect' to find LLAMA.CPP (local) in the list, also add ai/gemma4:E4B model.
- Optionally, try with `opencode serve` and open http://127.0.0.1:4096

#### Pairing with AI
- Chat with AI for couple hours to let assistant to write typescript codes
    * Ask for new tickets system schema
    * Help on Plant UML for schema diagram
    * Setup typescript project (needs human to guide this one)
    * Can connect to database 
    * Bootstrap the new database and push schema changes with typescript code (node human as well)
    * Search tickets and users information from dataset
    * ~~Contain code bug that query resultset from sqlite3 and AI cannot find good answer~~  Fix in [this commit](https://github.com/boonchu/ai_code_assistant/commit/66bb8647560abfee685823f58f86125eeed2a374)
    * "MUST" commit git every time before AI made code changes. Otherwise lost all codes since AI can wipe out 30-50% original codes.

* schema design

![Schema Diagram](schema.png)

* setup database

```
# create database with defined schema in code.
npx tsx src/setupDatabase.ts

# export schema
sqlite3 tickets.db .schema

# append new dataset
sqlite3 tickets.db < ./data/data.sql 
```

* search from dataset

```
# Charlie buys tickets for the Tech Summit
SELECT
    T.seat_number,
    T.purchase_date
FROM
    Tickets T
JOIN
    Users U ON T.user_id = U.user_id
JOIN
    Events E ON T.event_id = E.event_id
WHERE
    U.username = 'charlie_coder' AND E.name = 'Annual Tech Summit';

# who attend Music Festival
SELECT
    U.username AS user_name,
    E.name AS event_name,
    T.seat_number,
    T.purchase_date
FROM
    Tickets T
JOIN
    Users U ON T.user_id = U.user_id
JOIN
    Events E ON T.event_id = E.event_id
WHERE
    E.name = 'Local Music Festival';

# never attend Music Festival
SELECT
    username,
    email
FROM
    Users
WHERE
    user_id NOT IN (
        SELECT
            T.user_id
        FROM
            Tickets T
        JOIN
            Events E ON T.event_id = E.event_id
        WHERE
            E.name = 'Local Music Festival'
    );
```

#### Use OpenCode to assist me to create `Tic-Tac-Toe` React app.
```
npm start
```
![Tic-Tac-Toe](Tic-Tac-Toe.png)
