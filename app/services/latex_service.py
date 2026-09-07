import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
from app.config import WORKSPACE_DIR, IMAGES_DIR, LATEXMK_PATH, PDFLATEX_PATH

class LatexService:
    @staticmethod
    def compile_latex(
        main_tex_content: str,
        section_files: Optional[Dict[str, str]] = None,
        job_name: str = "Shrikar_Nakhye"
    ) -> Tuple[bool, Optional[bytes], str]:
        """
        Compiles LaTeX content into PDF.
        Returns: (success: bool, pdf_bytes: Optional[bytes], logs: str)
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_subfolder = temp_path / "tex"
            tex_subfolder.mkdir(parents=True, exist_ok=True)
            
            # Copy images folder if available
            if IMAGES_DIR.exists():
                shutil.copytree(IMAGES_DIR, temp_path / "images", dirs_exist_ok=True)
            
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
                # Copy workspace tex files as fallback
                workspace_tex = WORKSPACE_DIR / "tex"
                if workspace_tex.exists():
                    shutil.copytree(workspace_tex, tex_subfolder, dirs_exist_ok=True)
                    
            # Write main tex file
            main_file_path = temp_path / f"{job_name}.tex"
            main_file_path.write_text(main_tex_content, encoding="utf-8")
            
            # Build using latexmk or pdflatex
            cmd = [
                LATEXMK_PATH,
                "-pdf",
                "-interaction=nonstopmode",
                f"-jobname={job_name}",
                f"{job_name}.tex"
            ]
            
            # If latexmk is missing, fall back to pdflatex
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
