#!/usr/bin/env python3
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "paperVI_submission_source"
OUT = ROOT / "arxiv_submission_source.zip"
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(SRC.rglob("*")):
        if path.is_file() and path.name not in {
            "main.pdf",
            "public_data_audit_supplement.pdf",
        } and not path.name.endswith((".aux", ".log", ".out", ".bbl", ".blg")):
            zf.write(path, path.relative_to(SRC))
print("ARXIV_SOURCE_BUILT")
