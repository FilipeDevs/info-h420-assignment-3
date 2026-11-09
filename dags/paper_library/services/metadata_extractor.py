import json

from openai import OpenAI

from paper_library.models import CATEGORIES, InvalidMetadataError, PaperMetadata


class MetadataExtractor:
    """
    Asks the local LLM for a paper's metadata as JSON.
    """

    MAX_ATTEMPTS = 2 # one retry
    SYSTEM_PROMPT = "You extract metadata from research papers. Answer with JSON only."
    OLLAMA_PLACEHOLDER_API_KEY = "ollama" # placeholder key

    def __init__(self, base_url: str, model: str, max_chars: int = 100_000): # 100k chars ~25k tokens
        self.model = model
        self.max_chars = max_chars
        self.client = OpenAI(base_url=base_url, api_key=self.OLLAMA_PLACEHOLDER_API_KEY)

    def extract(self, markdown: str) -> PaperMetadata:
        prompt = self.build_prompt(markdown)
        last_error = None

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            # If retry then icrease temperature to get a different response
            if attempt == 1:
                temperature = 0.0
            else:
                temperature = 0.3
            raw_response = self.ask_model(prompt, temperature)

            try:
                data = json.loads(raw_response)
                return PaperMetadata.from_dict(data)
            except (json.JSONDecodeError, InvalidMetadataError) as error:
                last_error = error
                print(f"Attempt {attempt} returned invalid metadata: {error}")

        raise InvalidMetadataError(
            f"The LLM returned invalid metadata {self.MAX_ATTEMPTS} times: {last_error}"
        )

    def build_prompt(self, markdown: str) -> str:
        paper_text = markdown[: self.max_chars]
        category_list = ", ".join(CATEGORIES)

        return (
            f"Paper text:\n{paper_text}\n\n"
            "Give the title, a 4-5 sentence summary, 3 to 6 keywords, "
            f"and the best-fitting category among: {category_list}."
        )

    def ask_model(self, prompt: str, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            reasoning_effort="none",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "paper_metadata", "schema": self.json_schema()},
            },
        )
        return response.choices[0].message.content

    @staticmethod
    def json_schema() -> dict:
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "category": {"type": "string", "enum": CATEGORIES},
            },
            "required": ["title", "summary", "keywords", "category"],
        }
