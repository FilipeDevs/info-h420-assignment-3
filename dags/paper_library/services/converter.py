from pathlib import Path

import pymupdf4llm


class PdfToMarkdownConverter:
    """
    Converts a PDF from the papers folder into a markdown file.
    """

    def __init__(self, papers_dir: Path, markdown_dir: Path):
        self.papers_dir = papers_dir
        self.markdown_dir = markdown_dir

    def convert(self, filename: str) -> Path:
        pdf_path = self.papers_dir / filename
        markdown = pymupdf4llm.to_markdown(str(pdf_path))
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = self.markdown_dir / f"{pdf_path.stem}.md"
        markdown_path.write_text(markdown, encoding="utf-8")

        return markdown_path
