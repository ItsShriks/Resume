# Build from the repository root so the CV sources (tex/, refs/, template/, images/) are included:
#   docker build -f .web/Dockerfile -t resume-tailor .
#   docker run -p 8000:8000 -e GEMINI_API_KEY=... resume-tailor
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    latexmk \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /repo
COPY .web/requirements.txt .web/requirements.txt
RUN pip install --no-cache-dir -r .web/requirements.txt
COPY . .

WORKDIR /repo/.web
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
