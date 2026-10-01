import re
from app.config import TEX_DIR, REFS_DIR, CV_TEX, COVER_LETTER_TEX

# section key -> file name, shared by tex/ (tailored) and refs/ (master)
SECTION_FILES = {
    "personal_info": "Personal_Info.tex",
    "work_experience": "Work_Experience.tex",
    "projects": "Projects.tex",
    "education": "Education.tex",
    "skills": "Skills.tex",
    "certifications": "Training_And_Certifications.tex",
    "publications": "Publications.tex",
    "interests": "Interests.tex",
}


def _read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _macro(tex, name):
    """Value of a simple \\newcommand{\\name}{value} definition."""
    m = re.search(r"\\newcommand\{\\" + name + r"\}\{(.*)\}\s*$", tex, re.M)
    return m.group(1).replace("\\&", "&") if m else ""


class ProfileService:
    @staticmethod
    def get_master_profile():
        """Reads tailored sections (tex/), master content (refs/) and the main documents."""
        sections = {key: _read(TEX_DIR / name) for key, name in SECTION_FILES.items()}
        refs = {key: _read(REFS_DIR / name) for key, name in SECTION_FILES.items()}
        info = refs["personal_info"]

        return {
            "name": _macro(info, "cvname") or "Candidate",
            "title": "M.Sc. Autonomous Systems & Robotics Engineer",
            "location": _macro(info, "cvlocation"),
            "email": _macro(info, "cvemail"),
            "linkedin": _macro(info, "cvlinkedin"),
            "github": _macro(info, "cvgithub"),
            "google_scholar": _macro(info, "cvscholar"),
            "sections": sections,
            "refs": refs,
            "main_resume_tex": _read(CV_TEX),
            "cover_letter_tex": _read(COVER_LETTER_TEX),
        }

    @staticmethod
    def refs_text(profile):
        """All master refs as one block, for AI prompts."""
        return "\n\n".join(
            f"--- [refs/{SECTION_FILES[k]}] ---\n{v}" for k, v in profile.get("refs", {}).items() if v
        )
