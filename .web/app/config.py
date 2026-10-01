import os
import shutil
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent.parent       # .web/
REPO_DIR = Path(os.getenv("RESUME_REPO_DIR", WEB_DIR.parent))  # CV repo root

TEX_DIR = REPO_DIR / "tex"
REFS_DIR = REPO_DIR / "refs"
IMAGES_DIR = REPO_DIR / "images"
CV_TEX = REPO_DIR / "cv.tex"
COVER_LETTER_TEX = REPO_DIR / "cover_letter.tex"
STATIC_DIR = WEB_DIR / "app" / "static"

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LATEXMK_PATH = os.getenv("LATEXMK_PATH") or shutil.which("latexmk") or "/usr/local/bin/latexmk"
PDFLATEX_PATH = os.getenv("PDFLATEX_PATH") or shutil.which("pdflatex") or "/usr/local/bin/pdflatex"
