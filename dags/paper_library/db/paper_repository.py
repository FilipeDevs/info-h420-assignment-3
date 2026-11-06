import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from paper_library.db import queries
from paper_library.models import Paper, PaperMetadata


class PaperRepository:
    """
    Stores one row per paper in a local sqlite db
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.create_table()

    @contextmanager
    def open_connection(self):
        """Open a connection and commit if everything went well, and always close it when done."""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def create_table(self) -> None:
        with self.open_connection() as connection:
            connection.execute(queries.CREATE_PAPERS_TABLE)

    def processed_filenames(self) -> set[str]:
        filenames = set()
        with self.open_connection() as connection:
            rows = connection.execute(queries.SELECT_ALL_FILENAMES)
            for row in rows:
                filenames.add(row["filename"])
        return filenames

    def save(self, filename: str, metadata: PaperMetadata) -> None:
        keywords_json = json.dumps(metadata.keywords)
        processed_at = datetime.now().isoformat(timespec="seconds")
        values = (
            filename,
            metadata.title,
            metadata.summary,
            keywords_json,
            metadata.category,
            processed_at,
        )
        with self.open_connection() as connection:
            connection.execute(queries.UPSERT_PAPER, values)

    def all_papers(self) -> list[Paper]:
        with self.open_connection() as connection:
            rows = connection.execute(queries.SELECT_ALL_PAPERS).fetchall()
        papers = []
        for row in rows:
            metadata = PaperMetadata(
                title=row["title"],
                summary=row["summary"],
                keywords=json.loads(row["keywords"]),
                category=row["category"],
            )
            paper = Paper(
                filename=row["filename"],
                metadata=metadata,
                processed_at=row["processed_at"],
            )
            papers.append(paper)

        return papers
