import html
import os
import shutil
from datetime import datetime
from pathlib import Path

from paper_library.models import Paper


class LibraryPageRenderer:
    """
    Builds the html page from the templates and writes it to the output folder.
    """
    # templates are in paper_library/templates/
    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
    ASSET_FILES = ["style.css", "script.js"]

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def render(self, papers: list[Paper]) -> Path:
        page = self.build_page(papers)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.copy_assets()
        return self.write_page(page)

    def build_page(self, papers: list[Paper]) -> str:
        template = (self.TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")

        page = template.replace("__UPDATED__", last_updated)
        page = page.replace("__OPTIONS__", self.build_category_options(papers))
        page = page.replace("__CARDS__", self.build_cards(papers))
        return page

    def build_cards(self, papers: list[Paper]) -> str:
        if not papers:
            return '<p class="text-center text-body-secondary py-5">No papers yet.</p>'

        cards = []
        for paper in papers:
            cards.append(self.build_card(paper))
        return "\n".join(cards)

    def build_card(self, paper: Paper) -> str:
        # Everything coming from the LLM is escaped before going into the HTML
        metadata = paper.metadata
        title = html.escape(metadata.title)
        summary = html.escape(metadata.summary)
        category = html.escape(metadata.category)
        filename = html.escape(paper.filename)
        added_on = paper.processed_at[:10]

        keyword_tags = ""
        for keyword in metadata.keywords:
            keyword_tags += f'<span class="badge rounded-pill keyword me-1">{html.escape(keyword)}</span>'

        # The text the search box looks in, lowercase so the search ignores case
        searchable_parts = [metadata.title, metadata.summary, paper.filename] + metadata.keywords
        search_text = html.escape(" ".join(searchable_parts).lower())

        return f"""
    <article class="card paper-card shadow-sm mb-3" data-category="{category}" data-search="{search_text}">
      <div class="card-body">
        <h2 class="h5 card-title mb-2">
          <a class="link-body-emphasis text-decoration-none" href="../papers/{filename}">{title}</a>
        </h2>
        <p class="small text-body-secondary mb-3">
          <span class="badge category-badge me-1">{category}</span>
          {filename} &middot; added {added_on}
        </p>
        <p class="card-text">{summary}</p>
        <div>{keyword_tags}</div>
      </div>
    </article>"""

    def build_category_options(self, papers: list[Paper]) -> str:
        categories = set()
        for paper in papers:
            categories.add(paper.metadata.category)

        options = []
        for category in sorted(categories):
            escaped = html.escape(category)
            options.append(f'<option value="{escaped}">{escaped}</option>')
        return "\n".join(options)

    def copy_assets(self) -> None:
        # index.html links to these files, so they must sit next to it
        for filename in self.ASSET_FILES:
            shutil.copyfile(self.TEMPLATES_DIR / filename, self.output_dir / filename)

    def write_page(self, page: str) -> Path:
        # Write to a temporary file, then rename it: Google Drive never syncs a half-written page
        final_path = self.output_dir / "index.html"
        temp_path = self.output_dir / "index.html.tmp"

        temp_path.write_text(page, encoding="utf-8")
        os.replace(temp_path, final_path)
        return final_path
