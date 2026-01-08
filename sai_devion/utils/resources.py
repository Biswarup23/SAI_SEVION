import os
import sys
from pathlib import Path

def resource_path(relative_path: str) -> str:
    # PyInstaller safe
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return str(Path(base_path) / relative_path)
