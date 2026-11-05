import json, time
from pathlib import Path
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "gemma4:12b"
MAX_CHARS = 100_000  

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

text = Path("test-papers/paper1.md").read_text(encoding="utf-8")[:MAX_CHARS]

start = time.time()
response = client.chat.completions.create(
    model=MODEL,
    temperature=0,
    reasoning_effort="none",
    messages=[
        {"role": "system", "content": "You extract metadata from research papers. Answer with JSON only."},
        {"role": "user", "content": f"Paper text:\n{text}\n\nGive the title, a 2-3 sentence summary, 3 to 6 keywords, and one category."},
    ],
    response_format={"type": "json_schema", "json_schema": {"name": "paper_metadata", "schema": SCHEMA}},
)
print(json.dumps(json.loads(response.choices[0].message.content), indent=2))
print(f"\nTook {time.time() - start:.1f} s for {len(text):,} characters")
