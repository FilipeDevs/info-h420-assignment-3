# INFO-H420 Assignment 3: Workflows with Airflow - Research Paper Library

## Requirements

- Linux, macOS, or Windows with WSL2 (tested on Ubuntu 24.04 under WSL2)
- Python 3.12
- Ollama
- Google Drive for Desktop
- A Discord webhook

## Setup

**1. Clone the repository and create a virtual environment**

```bash
git clone https://github.com/FilipeDevs/info-h420-assignment-3.git ~/assignment-3
cd ~/assignment-3
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

**2. Install Airflow and the dependencies**

```bash
pip install "apache-airflow==3.3.2" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt"
pip install -r requirements.txt
```

**3. Install Ollama and the model**

We used `gemma4:12b`. 

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:12b
```

If you want to use another model, pull it and add `export LLM_MODEL="<model-name>"` to `env.local`.

```bash
ollama pull llama3.2
echo 'export LLM_MODEL="llama3.2"' >> env.local
```

For our pipeline we send up to 100 000 characters of each paper to the LLM, which needs a 32k context window. Ollama's default context is smaller so to increase it:

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
printf '[Service]\nEnvironment="OLLAMA_CONTEXT_LENGTH=32768"\n' | sudo tee /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

But if instead you keep Ollama's default context, lower the number of characters sent to the LLM:

```bash
echo 'export LLM_MAX_CHARS=12000' >> env.local
```

**4. Set up the synced folder**
 
The pipeline reads PDFs from a folder on your machine that Google Drive keeps in sync.
 
1. Create a folder named `ResearchLibrary` with two empty folders inside it named `papers` and `output`.
2. In Google Drive for Desktop sync the folder `ResearchLibrary` to your machine.
3. Add the path of your folder to `env.local` (if not set, it defaults to `~/ResearchLibrary`):

```bash
echo 'export LIBRARY_DIR="<your-path-to-ResearchLibrary>"' >> env.local
```

**5. Discord webhook**

```bash
echo 'export DISCORD_WEBHOOK_URL="<your-webhook-url>"' >> env.local
```

## Usage

Open a new terminal:

```bash
cd ~/assignment-3 && source .venv/bin/activate && source env.sh
```

And to start airflow:

```bash
airflow standalone
```

1. Open http://localhost:8080 and log in as `admin` (the password is printed at startup or you can find it in the airflow folder named `simple_auth_manager_passwords.json.generated`).
2. Switch on the `paper_pipeline` DAG. By default it runs every 5 minutes, but you can trigger it manually.
3. Put PDFs in `ResearchLibrary/papers/` (examples are in `papers/`).
4. Open `ResearchLibrary/output/index.html` to browse the library when airflow has finished processing the papers.

If you want to reset all the papers just delete the database: `rm data/papers.db`.