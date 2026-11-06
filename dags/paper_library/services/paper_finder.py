import time
from pathlib import Path

from paper_library.db.paper_repository import PaperRepository


class NewPaperFinder:
    """
    Finds the PDFs in the papers folder that have not been processed yet.
    """

    def __init__(self, papers_dir: Path, repository: PaperRepository, min_age_seconds: int = 60):
        self.papers_dir = papers_dir
        self.repository = repository
        self.min_age_seconds = min_age_seconds

    def find(self) -> list[str]:
        already_processed = self.repository.processed_filenames()
        new_files = []

        for path in sorted(self.papers_dir.iterdir()):
            if not self.is_pdf(path):
                continue
            if path.name in already_processed:
                continue
            if self.was_modified_recently(path):
                # skip if the file was modified too recently (google drive sync can take a few seconds)
                continue
            new_files.append(path.name)

        return new_files

    @staticmethod
    def is_pdf(path: Path) -> bool:
        return path.is_file() and path.suffix.lower() == ".pdf"

    def was_modified_recently(self, path: Path) -> bool:
        age_in_seconds = time.time() - path.stat().st_mtime
        return age_in_seconds < self.min_age_seconds
