import re
from pathlib import Path
from app.config import WORKSPACE_DIR, TEX_DIR

class ProfileService:
    @staticmethod
    def get_master_profile():
        """Reads all master TeX files and returns structured and raw representation."""
        sections = {}
        tex_files = {
            "personal_info": TEX_DIR / "Personal_Info.tex",
            "work_experience": TEX_DIR / "Work_Experience.tex",
            "projects": TEX_DIR / "Projects.tex",
            "education": TEX_DIR / "Education.tex",
            "skills": TEX_DIR / "Skills.tex",
            "certifications": TEX_DIR / "Training_And_Certifications.tex",
            "publications": TEX_DIR / "Publications.tex",
            "interests": TEX_DIR / "Interests.tex"
        }
        
        for key, filepath in tex_files.items():
            if filepath.exists():
                sections[key] = filepath.read_text(encoding="utf-8")
            else:
                sections[key] = ""
                
        main_resume = ""
        main_resume_path = WORKSPACE_DIR / "Shrikar_Nakhye.tex"
        if main_resume_path.exists():
            main_resume = main_resume_path.read_text(encoding="utf-8")

        cover_letter = ""
        cover_letter_path = WORKSPACE_DIR / "cover_letter.tex"
        if cover_letter_path.exists():
            cover_letter = cover_letter_path.read_text(encoding="utf-8")

        return {
            "name": "Shrikar Nakhye",
            "title": "M.Sc. Autonomous Systems & Robotics Engineer",
            "location": "Bonn, Germany",
            "email": "nakhyeshrikar@icloud.com",
            "linkedin": "https://www.linkedin.com/in/shrikar-nakhye-053262188/",
            "github": "https://github.com/ItsShriks",
            "google_scholar": "https://scholar.google.com/citations?user=-kVcoO8AAAAJ&hl=en",
            "sections": sections,
            "main_resume_tex": main_resume,
            "cover_letter_tex": cover_letter
        }
