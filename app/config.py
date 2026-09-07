import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR
TEX_DIR = BASE_DIR / "tex"
IMAGES_DIR = BASE_DIR / "images"
BUILD_CACHE_DIR = BASE_DIR / "build" / "web_sessions"
BUILD_CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LATEXMK_PATH = os.getenv("LATEXMK_PATH", "/usr/local/bin/latexmk")
PDFLATEX_PATH = os.getenv("PDFLATEX_PATH", "/usr/local/bin/pdflatex")
