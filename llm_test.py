import json
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # key is ignored by Ollama
MODEL = "gemma4:12b"

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "category": {"type": "string"},
    },
    "required": ["title", "summary", "keywords", "category"],
}

TEXT = """Incremental Materialization for Workflow DAGs.
We study how data pipelines can avoid recomputing intermediate artifacts.
We model a workflow as a task-artifact graph and propose a greedy policy that
decides which artifacts to store, based on their recomputation cost and how
often later runs reuse them. On 40 production pipelines, the policy cuts total
compute time by 31% while using 12% extra storage."""

response = client.chat.completions.create(
    model=MODEL,
    temperature=0,
    reasoning_effort="none",
    messages=[
        {"role": "system", "content": "You extract metadata from research papers. Answer with JSON only."},
        {"role": "user", "content": f"Paper text:\n{TEXT}\n\nGive the title, a 2-3 sentence summary, 3 to 6 keywords, and one category."},
    ],
    response_format={"type": "json_schema", "json_schema": {"name": "paper_metadata", "schema": SCHEMA}},
)

raw = response.choices[0].message.content
print("RAW RESPONSE:\n", raw)

data = json.loads(raw)
print("\nPARSED:")
print(json.dumps(data, indent=2))
