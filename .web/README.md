# .web — AI Resume & Cover Letter Tailor

Self-contained FastAPI app that tailors the CV in this repository to a job description
(Gemini) and compiles the result to PDF. It only **reads** the CV sources in the repo root
(`cv.tex`, `cover_letter.tex`, `tex/`, `refs/`, `images/`) and never writes to them.

| Run | Command |
|---|---|
| Local | `./.web/start_app.sh` (needs `pip install -r .web/requirements.txt` and a TeX installation) |
| Docker | `docker build -f .web/Dockerfile -t resume-tailor . && docker run -p 8000:8000 -e GEMINI_API_KEY=... resume-tailor` (run from the repo root) |

Environment: `GEMINI_API_KEY`, `GEMINI_MODEL`, `RESUME_REPO_DIR` (defaults to the parent folder),
`LATEXMK_PATH` / `PDFLATEX_PATH` (default: found on `PATH`).

This folder is identical on every branch (`dev`, `Deutsch`). Change it on one branch and
cherry-pick the commit to the other.
