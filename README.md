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
AIRFLOW_VERSION=3.3.2
PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
pip install "apache-airflow==${AIRFLOW_VERSION}" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install -r requirements.txt
```

**3. Install Ollama and the model (we used gemma4:12b but you can use any model)**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:12b
```

Raise Ollama's context window (depends on your system/GPU) so it reads whole papers (Linux / WSL):

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
printf '[Service]\nEnvironment="OLLAMA_CONTEXT_LENGTH=32768"\n' | sudo tee /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

**4. Set up the synced folder**
 
The pipeline reads PDFs from a folder on your machine that Google Drive keeps in sync.
 
1. Create a folder named `ResearchLibrary` with two empty folders inside it, `papers` and `output`.
2. In Google Drive for Desktop sync the folder to your machine.
3. Open `env.sh` and replace the path on the `LIBRARY_DIR` line with the path of your folder:
```bash
   export LIBRARY_DIR="/mnt/c/Users/<you>/Documents/ResearchLibrary"
```

**5. Discord webhook**

```bash
echo 'export DISCORD_WEBHOOK_URL="<your-webhook-url>"' > env.local
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

1. Open http://localhost:8080 and log in as `admin` (the password is printed at startup).
2. Switch on the `paper_pipeline` DAG. By default it runs every 5 minutes, but you can trigger it manually.
3. Put PDFs in `ResearchLibrary/papers/` (examples are in `papers/`).
4. Open `ResearchLibrary/output/index.html` to browse the library when airflow has finished processing the papers.

If you want to reset every paper just delete the database: `rm data/papers.db`.