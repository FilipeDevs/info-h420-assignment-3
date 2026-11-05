import sys
from pathlib import Path
import pymupdf4llm

pdf_path = Path(sys.argv[1])
markdown = pymupdf4llm.to_markdown(str(pdf_path))

out_path = pdf_path.with_suffix(".md")
out_path.write_text(markdown, encoding="utf-8")

print(markdown[:1500])
print(f"\n--- {len(markdown):,} characters, roughly {len(markdown)//4:,} tokens ---")
print(f"Saved to {out_path}")
