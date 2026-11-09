from datetime import datetime, timedelta
from airflow.sdk import dag, task, task_group

# Each task imports only the libraries it needs, to prevent unnecessary imports and speed up the scheduler.

"""
The research library pipeline.
This is what airflow uses to orchestrate the tasks. 
"""
@dag(
    dag_id="paper_pipeline",
    schedule=timedelta(minutes=5), # look for new papers every 5 minutes
    start_date=datetime(2026, 11, 1),
    catchup=False,
    max_active_runs=1, # never two runs working on the same files
    default_args={"retries": 2, "retry_delay": timedelta(seconds=30)},
    tags=["info-h420"],
)
def paper_pipeline():

    @task
    def find_new_pdfs() -> list[str]:
        from paper_library.config import Settings
        from paper_library.db.paper_repository import PaperRepository
        from paper_library.services.paper_finder import NewPaperFinder

        settings = Settings.from_env()
        repository = PaperRepository(settings.db_path)
        finder = NewPaperFinder(settings.papers_dir, repository)
        new_files = finder.find()
        print(f"Found {len(new_files)} new PDF(s): {new_files}")

        return new_files

    @task.short_circuit
    def has_new_papers(new_files: list[str]) -> bool:
        # Returning False skips every task after this one
        return len(new_files) > 0

    @task
    def convert_to_markdown(filename: str) -> dict:
        from paper_library.config import Settings
        from paper_library.services.converter import PdfToMarkdownConverter

        settings = Settings.from_env()
        converter = PdfToMarkdownConverter(settings.papers_dir, settings.markdown_dir)
        markdown_path = converter.convert(filename)

        return {"filename": filename, "markdown_path": str(markdown_path)}

    # one LLM call at a time on the GPU, and no Airflow retry: the single retry is done inside MetadataExtractor
    @task(max_active_tis_per_dag=1, retries=0)
    def extract_metadata(document: dict) -> dict:
        from pathlib import Path
        from paper_library.config import Settings
        from paper_library.services.metadata_extractor import MetadataExtractor

        settings = Settings.from_env()
        extractor = MetadataExtractor(settings.llm_base_url, settings.llm_model, settings.max_chars)
        markdown = Path(document["markdown_path"]).read_text(encoding="utf-8")
        metadata = extractor.extract(markdown)
        print(f"Metadata for {document['filename']}: {metadata}")

        return {"filename": document["filename"], "metadata": metadata.to_dict()}

    @task
    def save_to_database(record: dict) -> dict:
        from paper_library.config import Settings
        from paper_library.db.paper_repository import PaperRepository
        from paper_library.models import PaperMetadata

        settings = Settings.from_env()
        repository = PaperRepository(settings.db_path)
        metadata = PaperMetadata.from_dict(record["metadata"])
        repository.save(record["filename"], metadata)

        return record

    @task
    def notify_discord(record: dict) -> None:
        from paper_library.config import Settings
        from paper_library.models import PaperMetadata
        from paper_library.services.notifier import DiscordNotifier

        settings = Settings.from_env()
        notifier = DiscordNotifier(settings.discord_webhook_url)
        metadata = PaperMetadata.from_dict(record["metadata"])
        notifier.notify_new_paper(record["filename"], metadata)

    @task(trigger_rule="all_done")  # rebuild the page even if one paper failed
    def render_html() -> None:
        from paper_library.config import Settings
        from paper_library.db.paper_repository import PaperRepository
        from paper_library.services.html_renderer import LibraryPageRenderer

        settings = Settings.from_env()
        repository = PaperRepository(settings.db_path)
        renderer = LibraryPageRenderer(settings.output_dir)
        page_path = renderer.render(repository.all_papers())
        print(f"Page written to {page_path}")

    # task order
    new_files = find_new_pdfs()

    # Mapped task group: one group instance per new PDF. Inside an instance the
    # steps only depend on each other, so a paper that fails never blocks the others.
    @task_group
    def process_paper(filename: str):
        document = convert_to_markdown(filename)
        record = extract_metadata(document)
        saved = save_to_database(record)
        notify_discord(saved)

    papers = process_paper.expand(filename=new_files)
    has_new_papers(new_files) >> papers >> render_html()

paper_pipeline()
