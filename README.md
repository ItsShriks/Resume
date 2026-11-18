# CV & Cover Letter — Shrikar Nakhye

LaTeX sources for my CV and cover letters. One branch per language, same structure on both:

| Branch | Language | PDFs |
|---|---|---|
| `dev` | English | `Shrikar_Nakhye_CV.pdf`, `Shrikar_Nakhye_Cover_Letter.pdf` |
| `Deutsch` | German | `Lebenslauf_Shrikar_Nakhye.pdf`, `Anschreiben_Shrikar_Nakhye.pdf` |

Each commit is one application (`<Company> - <Role>`), so the git history is the application log.

## Layout

```
refs/              MASTER content in plain English (.txt): every job, project, degree, skill…
                   Never tailored; add new things here in your own words.
tex/               TAILORED LaTeX sections for the current application
                   + preamble.tex / header.tex: shared layout (identical on all branches)
                   + Contact.tex: contact details and labels for the header (per language)
.web/              AI tailoring web app (standalone) + portfolio website
images/            photo
docs/              old CV versions (.docx / .pages)
cv.tex             CV: section order, which tex/ files are included
cover_letter.tex   cover letter, rewritten per application
job_description.txt  paste a job ad here and hand the file to an AI assistant
build.sh           builds the PDFs (temporary files go to the hidden .build/)
```

## How refs → tex works

`refs/` is written like notes, not LaTeX (format explained in `refs/README.txt`):

```text
## Student Assistant
When: Jul 2025 -- Apr 2026
Where: Navilan Solutions, Bonn, Germany
Tech: C++, Qt, Python, DocTR, Tesseract, EasyOCR
- Built a fully offline OCR ensemble: 90--95% accuracy on low-end CPUs.
Notes: release / usage figures are confidential.
```

For each application the AI assistant picks what fits the job and writes it as LaTeX into
`tex/` (e.g. `tex/Work_Experience.tex`). Only facts from `refs/` may appear in `tex/`.
Projects carry a `\repo{ItsShriks/<repo>}` GitHub link as evidence; keep it when tailoring.

## Workflow

0. Did something new (job, project, result)? Write it into the right `refs/*.txt` file first.
1. Paste the job ad into `job_description.txt`, give the file to the AI assistant.
2. It edits `tex/` and `cover_letter.tex` only (never `refs/`).
3. `./build.sh` → review PDFs → commit as `<Company> - <Role>`.

`./build.sh cv`, `./build.sh cover_letter` and `./build.sh clean` also work.

## Keeping branches in sync

- `tex/preamble.tex`, `tex/header.tex`, `.web/`, `docs/`, `build.sh`, `README.md`, `.gitignore`
  are identical on both branches.
  Change them in a separate commit and `git cherry-pick` it to the other branch.
- `refs/` is English on **both** branches (the AI translates when writing a German CV).
  Change it in a separate commit and `git cherry-pick` it to the other branch.
- `tex/Contact.tex` is per language (labels, date format, photo on/off).
- Never merge `dev` and `Deutsch` into each other.
