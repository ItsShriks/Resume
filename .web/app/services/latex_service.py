import base64
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from app.config import TEX_DIR, REFS_DIR, IMAGES_DIR, LATEXMK_PATH, PDFLATEX_PATH
from app.services.profile_service import SECTION_FILES


def _escape(text: str) -> str:
    for ch in ("&", "%", "#", "_", "$"):
        text = text.replace(ch, "\\" + ch)
    return text


class LatexService:
    @staticmethod
    def inject_candidate_header(main_tex: str, candidate_data: Optional[Dict[str, Any]] = None) -> str:
        """Overrides the header macros from refs/Personal_Info.tex (\\cvname, \\cvemail, ...)
        right before \\begin{document}, and hides the photo unless one was explicitly uploaded."""
        meta = candidate_data or {}
        overrides = {
            "cvname": meta.get("name") or meta.get("candidate_name"),
            "cvlocation": meta.get("location") or meta.get("candidate_location"),
            "cvemail": meta.get("email") or meta.get("candidate_email"),
            "cvlinkedin": meta.get("linkedin") or meta.get("candidate_linkedin"),
            "cvgithub": meta.get("github") or meta.get("candidate_github"),
        }
        lines = []
        for macro, value in overrides.items():
            if value:
                value = value if macro in ("cvemail", "cvlinkedin", "cvgithub") else _escape(value)
                lines.append(f"\\renewcommand{{\\{macro}}}{{{value}}}")
        has_custom_photo = bool(meta.get("photo_base64")) and meta.get("photo_mode", "none") == "custom"
        if not has_custom_photo:
            lines.append("\\cvphotofalse")

        marker = "\\begin{document}"
        if marker not in main_tex:
            return main_tex
        return main_tex.replace(marker, "\n".join(lines) + "\n" + marker, 1)

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
            
            # Master content, needed by every document (layout comes with tex/ below)
            if REFS_DIR.exists():
                shutil.copytree(REFS_DIR, temp_path / "refs", dirs_exist_ok=True)

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
            if TEX_DIR.exists():
                shutil.copytree(TEX_DIR, tex_subfolder, dirs_exist_ok=True)
            if section_files:
                for key, content in section_files.items():
                    target_name = SECTION_FILES.get(key, f"{key}.tex")
                    (tex_subfolder / target_name).write_text(content, encoding="utf-8")

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
