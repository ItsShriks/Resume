import os
import re
import base64
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from app.config import WORKSPACE_DIR, IMAGES_DIR, LATEXMK_PATH, PDFLATEX_PATH

class LatexService:
    @staticmethod
    def inject_candidate_header(main_tex: str, candidate_data: Optional[Dict[str, Any]] = None) -> str:
        """Dynamically substitutes candidate metadata and strictly hides photos unless explicitly uploaded."""
        updated_tex = main_tex
        
        candidate_meta = candidate_data or {}
        name = candidate_meta.get("name") or candidate_meta.get("candidate_name")
        location = candidate_meta.get("location") or candidate_meta.get("candidate_location")
        email = candidate_meta.get("email") or candidate_meta.get("candidate_email")
        linkedin = candidate_meta.get("linkedin") or candidate_meta.get("candidate_linkedin")
        github = candidate_meta.get("github") or candidate_meta.get("candidate_github")
        photo_mode = candidate_meta.get("photo_mode", "none")  # Default is 'none' for privacy
        has_custom_photo = bool(candidate_meta.get("photo_base64")) and photo_mode == "custom"

        if name:
            updated_tex = re.sub(r"\{\\Huge\s*\\textbf\{[^}]+\}\}", lambda m: f"{{\\Huge \\textbf{{{name}}}}}", updated_tex)
        if location:
            updated_tex = re.sub(r"Address:\s*[^\\\n]+", lambda m: f"Address: {location}", updated_tex)
        if email:
            updated_tex = re.sub(r"\\href\{mailto:[^}]+\}\{[^}]+\}", lambda m: f"\\href{{mailto:{email}}}{{{email}}}", updated_tex)
        if linkedin:
            updated_tex = re.sub(r"\\href\{https://www\.linkedin\.com/[^}]+\}", lambda m: f"\\href{{{linkedin}}}", updated_tex)
        if github:
            updated_tex = re.sub(r"\\href\{https://github\.com/[^}]+\}", lambda m: f"\\href{{{github}}}", updated_tex)

        # Unless the user explicitly uploaded a custom photo, remove photo box and expand header to full width
        if not has_custom_photo:
            updated_tex = re.sub(
                r"\\begin\{minipage\}\[c\]\{0\.72\\origtextwidth\}",
                lambda m: "\\begin{minipage}[c]{\\origtextwidth}",
                updated_tex
            )
            updated_tex = re.sub(
                r"\\hfill\s*\\begin\{minipage\}\[c\]\{0\.20\\origtextwidth\}[\s\S]*?\\end\{minipage\}%",
                "",
                updated_tex
            )

        return updated_tex

    @classmethod
    def compile_latex(
        cls,
        main_tex_content: str,
        section_files: Optional[Dict[str, str]] = None,
        job_name: str = "Candidate_Resume",
        candidate_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[bytes], str]:
        """
        Compiles LaTeX content into PDF.
        Strict Privacy: Never includes personal photo unless user explicitly uploaded one in their current session.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_subfolder = temp_path / "tex"
            images_subfolder = temp_path / "images"
            tex_subfolder.mkdir(parents=True, exist_ok=True)
            images_subfolder.mkdir(parents=True, exist_ok=True)
            
            # Copy only icon images (linkedin, github, scholar) - NEVER copy Self_Pic.jpg
            if IMAGES_DIR.exists():
                for icon_file in IMAGES_DIR.glob("*.png"):
                    shutil.copy(icon_file, images_subfolder / icon_file.name)
            
            # Check if custom photo base64 is explicitly uploaded by the user
            candidate_meta = candidate_data or {}
            photo_mode = candidate_meta.get("photo_mode", "none")
            if photo_mode == "custom" and candidate_meta.get("photo_base64"):
                try:
                    photo_b64 = candidate_meta["photo_base64"]
                    if "," in photo_b64:
                        photo_b64 = photo_b64.split(",", 1)[1]
                    photo_bytes = base64.b64decode(photo_b64)
                    (images_subfolder / "Self_Pic.jpg").write_bytes(photo_bytes)
                except Exception as e:
                    print(f"Warning: Failed to process uploaded photo: {e}")

            # Write modular section files if provided
            if section_files:
                filename_map = {
                    "personal_info": "Personal_Info.tex",
                    "work_experience": "Work_Experience.tex",
                    "projects": "Projects.tex",
                    "education": "Education.tex",
                    "skills": "Skills.tex",
                    "certifications": "Training_And_Certifications.tex",
                    "publications": "Publications.tex",
                    "interests": "Interests.tex"
                }
                for key, content in section_files.items():
                    target_name = filename_map.get(key, f"{key}.tex")
                    (tex_subfolder / target_name).write_text(content, encoding="utf-8")
            else:
                workspace_tex = WORKSPACE_DIR / "tex"
                if workspace_tex.exists():
                    shutil.copytree(workspace_tex, tex_subfolder, dirs_exist_ok=True)
                    
            # Apply dynamic candidate header & strict photo privacy
            processed_main_tex = cls.inject_candidate_header(main_tex_content, candidate_data)

            # Write main tex file
            main_file_path = temp_path / f"{job_name}.tex"
            main_file_path.write_text(processed_main_tex, encoding="utf-8")
            
            # Build using latexmk or pdflatex
            cmd = [
                LATEXMK_PATH,
                "-pdf",
                "-interaction=nonstopmode",
                f"-jobname={job_name}",
                f"{job_name}.tex"
            ]
            
            if not Path(LATEXMK_PATH).exists():
                cmd = [
                    PDFLATEX_PATH,
                    "-interaction=nonstopmode",
                    f"-jobname={job_name}",
                    f"{job_name}.tex"
                ]

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(temp_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                output_pdf = temp_path / f"{job_name}.pdf"
                
                logs = f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}"
                if output_pdf.exists():
                    pdf_data = output_pdf.read_bytes()
                    return True, pdf_data, logs
                else:
                    return False, None, f"PDF file not generated. Exit code: {proc.returncode}\n{logs}"
            except Exception as e:
                return False, None, f"LaTeX Compilation Exception: {str(e)}"
