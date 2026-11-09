# Contains environment variables for the pipeline

# Machine-specific values (LIBRARY_DIR, DISCORD_WEBHOOK_URL, LLM_MODEL, ...) go in env.local, which is not committed
[ -f "$HOME/assignment-3/env.local" ] && source "$HOME/assignment-3/env.local"

# Airflow
export AIRFLOW_HOME="$HOME/assignment-3/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$HOME/assignment-3/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__DAG_PROCESSOR__REFRESH_INTERVAL=30

# Google Drive synced folder (set your own path in env.local)
export LIBRARY_DIR="${LIBRARY_DIR:-$HOME/ResearchLibrary}"
export PAPERS_DIR="$LIBRARY_DIR/papers"
export OUTPUT_DIR="$LIBRARY_DIR/output"

# Local SQLite database (outside the synced folder)
export DB_PATH="$HOME/assignment-3/data/papers.db"
