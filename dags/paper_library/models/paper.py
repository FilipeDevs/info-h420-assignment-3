from dataclasses import dataclass

from paper_library.models.paper_metadata import PaperMetadata


@dataclass
class Paper:
    """
    Data class representing a paper.
    """

    filename: str
    metadata: PaperMetadata
    processed_at: str
