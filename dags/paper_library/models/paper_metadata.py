from dataclasses import asdict, dataclass


class InvalidMetadataError(ValueError):
    """
    Custom exception raised when the LLM response does not have the expected fields.
    """


@dataclass
class PaperMetadata:
    """
    Data class representing the metadata of a paper.
    """
    title: str
    summary: str
    keywords: list[str]
    category: str

    @classmethod
    def from_dict(cls, data: dict) -> "PaperMetadata":
        """
        Build metadata from a dict, checking that every field exists and has the right type.
        """
        if not isinstance(data, dict):
            raise InvalidMetadataError("The response is not a JSON object")

        expected_types = {
            "title": str,
            "summary": str,
            "keywords": list,
            "category": str,
        }
        for field_name, expected_type in expected_types.items():
            value = data.get(field_name)
            if not isinstance(value, expected_type):
                raise InvalidMetadataError(
                    f"Field '{field_name}' is missing or is not a {expected_type.__name__}"
                )

        for keyword in data["keywords"]:
            if not isinstance(keyword, str):
                raise InvalidMetadataError("Every keyword must be a string")

        return cls(
            title=data["title"],
            summary=data["summary"],
            keywords=data["keywords"],
            category=data["category"],
        )

    def to_dict(self) -> dict:
        return asdict(self)
