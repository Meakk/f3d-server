#!/opt/sweetbot/venv/bin/python3

from pathlib import Path
import time
import os

UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER"))

cutoff = time.time() - (90 * 24 * 60 * 60)

for file in UPLOAD_FOLDER.iterdir():
    if file.is_file() and file.stat().st_mtime < cutoff:
        print(f"Removing {file}")
        file.unlink()
