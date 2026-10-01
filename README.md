# CV & Cover Letter — Shrikar Nakhye

LaTeX sources for my CV and cover letters. One branch per language, same structure on both:

| Branch | Language | PDFs |
|---|---|---|
| `dev` | English | `Shrikar_Nakhye_CV.pdf`, `Shrikar_Nakhye_Cover_Letter.pdf` |
| `Deutsch` | German | `Lebenslauf_Shrikar_Nakhye.pdf`, `Anschreiben_Shrikar_Nakhye.pdf` |

Each commit is one application (`<Company> - <Role>`), so the git history is the application log.

## Layout

```
refs/              MASTER content: every job, project, degree, skill… (never tailored)
tex/               TAILORED sections for the current application
template/          shared layout: preamble, commands, header        (identical on all branches)
.web/              AI tailoring web app, fully standalone            (identical on all branches)
images/            icons + photo
portfolio/         personal website
cv.tex             CV: section order, which tex/ files are included
cover_letter.tex   cover letter, rewritten per application
job_description.txt  paste a job ad here and hand the file to an AI assistant
build.sh           builds the PDFs
```

## How refs → tex works

Every master entry in `refs/` has a name:

```latex
% refs/Work_Experience.tex
\defref{exp:navilan}{ \resumeSubheading{Student Assistant}{Jul 2025 -- Apr 2026}... }
```

A tailored section either pulls it in unchanged or writes its own version of it:

```latex
% tex/Work_Experience.tex
\section{Experience}
\resumeSubHeadingListStart
  \useref{exp:bitbots}          % master version, as-is
  \resumeSubheading{...}        % tailored rewrite of exp:navilan
\resumeSubHeadingListEnd
```

A typo in a ref name stops the build with `Unknown ref`. Projects carry a `\repo{ItsShriks/<repo>}`
GitHub link as evidence; keep it when tailoring.

## Workflow

1. Paste the job ad into `job_description.txt`, give the file to the AI assistant.
2. It edits `tex/` and `cover_letter.tex` only (never `refs/`).
3. `./build.sh` → review PDFs → commit as `<Company> - <Role>`.

`./build.sh cv`, `./build.sh cover_letter` and `./build.sh clean` also work.

## Keeping branches in sync

- `template/`, `.web/`, `build.sh`, `README.md`, `.gitignore` are identical on both branches.
  Change them in a separate commit and `git cherry-pick` it to the other branch.
- `refs/` holds the same facts on both branches, only translated. When something changes
  (new job, new project, new date), update `refs/` on **both** branches.
- Never merge `dev` and `Deutsch` into each other.
