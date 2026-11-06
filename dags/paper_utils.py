import html
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"


# ---------- Database ----------

def get_connection():
    db_path = Path(os.environ["DB_PATH"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            filename     TEXT PRIMARY KEY,
            title        TEXT NOT NULL,
            summary      TEXT NOT NULL,
            keywords     TEXT NOT NULL,   -- JSON list stored as text
            category     TEXT NOT NULL,
            processed_at TEXT NOT NULL
        )
    """)
    return conn


def processed_filenames():
    with get_connection() as conn:
        return {row[0] for row in conn.execute("SELECT filename FROM papers")}


def save_paper(filename, meta):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO papers (filename, title, summary, keywords, category, processed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(filename) DO UPDATE SET
                title = excluded.title,
                summary = excluded.summary,
                keywords = excluded.keywords,
                category = excluded.category,
                processed_at = excluded.processed_at
            """,
            (filename, meta["title"], meta["summary"], json.dumps(meta["keywords"]),
             meta["category"], datetime.now().isoformat(timespec="seconds")),
        )


def all_papers():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM papers ORDER BY processed_at DESC").fetchall()
    return [{**dict(row), "keywords": json.loads(row["keywords"])} for row in rows]


# ---------- HTML page ----------

def render_card(paper):
    esc = html.escape
    search_text = " ".join(
        [paper["title"], paper["summary"], paper["filename"], *paper["keywords"]]
    ).lower()
    keywords = "".join(f'<span class="kw">{esc(k)}</span>' for k in paper["keywords"])
    return f"""
    <article class="card" data-category="{esc(paper['category'])}" data-search="{esc(search_text)}">
      <h2><a href="../papers/{esc(paper['filename'])}">{esc(paper['title'])}</a></h2>
      <p class="meta"><span class="cat">{esc(paper['category'])}</span> &middot; {esc(paper['filename'])} &middot; added {paper['processed_at'][:10]}</p>
      <p>{esc(paper['summary'])}</p>
      <div>{keywords}</div>
    </article>"""


def render_html():
    papers = all_papers()
    categories = sorted({p["category"] for p in papers})

    cards = "".join(render_card(p) for p in papers) or '<p class="empty">No papers yet.</p>'
    options = "".join(
        f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in categories
    )

    template = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
    page = (template
            .replace("__UPDATED__", datetime.now().strftime("%Y-%m-%d %H:%M"))
            .replace("__OPTIONS__", options)
            .replace("__CARDS__", cards))

    out_dir = Path(os.environ["OUTPUT_DIR"])
    out_dir.mkdir(parents=True, exist_ok=True)

    # The page links to these, so they must sit next to index.html
    for asset in ("style.css", "script.js"):
        shutil.copyfile(TEMPLATES_DIR / asset, out_dir / asset)

    # Write to a temp file, then rename, so Drive never syncs a half-written page
    tmp = out_dir / "index.html.tmp"
    tmp.write_text(page, encoding="utf-8")
    os.replace(tmp, out_dir / "index.html")
    return str(out_dir / "index.html")
