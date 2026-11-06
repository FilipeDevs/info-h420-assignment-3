"""SQL queries used by PaperRepository."""

CREATE_PAPERS_TABLE = """
    CREATE TABLE IF NOT EXISTS papers (
        filename     TEXT PRIMARY KEY,
        title        TEXT NOT NULL,
        summary      TEXT NOT NULL,
        keywords     TEXT NOT NULL,   -- 
        category     TEXT NOT NULL,
        processed_at TEXT NOT NULL
    )
""" # The json is stored in 'keywords' as a string

SELECT_ALL_FILENAMES = """
    SELECT filename
    FROM papers
"""

# Insert a paper or update it if the filename already exists
UPSERT_PAPER = """
    INSERT INTO papers (filename, title, summary, keywords, category, processed_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(filename) DO UPDATE SET
        title = excluded.title,
        summary = excluded.summary,
        keywords = excluded.keywords,
        category = excluded.category,
        processed_at = excluded.processed_at
"""

SELECT_ALL_PAPERS = """
    SELECT filename, title, summary, keywords, category, processed_at
    FROM papers
    ORDER BY processed_at DESC
"""
