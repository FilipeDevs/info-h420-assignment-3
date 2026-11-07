# Contains environment variables for the pipeline

# Airflow
export AIRFLOW_HOME="$HOME/assignment-3/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$HOME/assignment-3/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__DAG_PROCESSOR__REFRESH_INTERVAL=30

# Google Drive synced folder (change to your own path !)
export LIBRARY_DIR="/mnt/c/Users/felix/Documents/ResearchLibrary"
export PAPERS_DIR="$LIBRARY_DIR/papers"
export OUTPUT_DIR="$LIBRARY_DIR/output"

# Local SQLite database (outside the synced folder)
export DB_PATH="$HOME/assignment-3/data/papers.db"

# Create env.local with your own DISCORD_WEBHOOK_URL
[ -f "$HOME/assignment-3/env.local" ] && source "$HOME/assignment-3/env.local"