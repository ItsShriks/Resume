import os
import base64
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.profile_service import ProfileService
from app.services.gemini_service import GeminiService
from app.services.latex_service import LatexService
from app.config import WORKSPACE_DIR

app = FastAPI(title="AI Resume & Cover Letter Tailor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for latest session outputs
SESSION_STORE: Dict[str, Any] = {
    "resume_pdf_bytes": None,
    "resume_tex_sections": {},
    "cover_letter_pdf_bytes": None,
    "cover_letter_tex": ""
}

class AnalyzeRequest(BaseModel):
    jd_text: str
    candidate_name: Optional[str] = None
    candidate_title: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

class TailorRequest(BaseModel):
    jd_text: str
    target_role: Optional[str] = None
    language: Optional[str] = "English"
    focus_area: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_title: Optional[str] = None
    candidate_location: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_linkedin: Optional[str] = None
    candidate_github: Optional[str] = None
    photo_mode: Optional[str] = "default"
    photo_base64: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

class CoverLetterRequest(BaseModel):
    jd_text: str
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    language: Optional[str] = "English"
    candidate_name: Optional[str] = None
    candidate_location: Optional[str] = None
    candidate_email: Optional[str] = None
    photo_mode: Optional[str] = "default"
    photo_base64: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

class ParseResumeRequest(BaseModel):
    raw_cv_text: str
    api_key: Optional[str] = None
    model: Optional[str] = None

class CompileResumeRequest(BaseModel):
    sections: Dict[str, str]
    main_tex: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_location: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_linkedin: Optional[str] = None
    candidate_github: Optional[str] = None
    photo_mode: Optional[str] = "default"
    photo_base64: Optional[str] = None

class CompileCoverLetterRequest(BaseModel):
    cover_letter_tex: str

@app.get("/api/master-profile")
def get_master_profile():
    """Returns master profile and LaTeX templates."""
    try:
        profile = ProfileService.get_master_profile()
        return {"status": "success", "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-resume")
def parse_raw_resume(req: ParseResumeRequest):
    """Parses any raw resume text into structured LaTeX sections using AI."""
    if not req.raw_cv_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is empty.")
    try:
        parsed_profile = GeminiService.parse_raw_resume(
            raw_cv_text=req.raw_cv_text,
            api_key=req.api_key,
            model=req.model
        )
        return {"status": "success", "parsed_profile": parsed_profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
def analyze_job(req: AnalyzeRequest):
    """Analyzes a Job Description against candidate profile across any industry."""
    if not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is empty.")
    
    try:
        profile = ProfileService.get_master_profile()
        if req.candidate_name: profile["name"] = req.candidate_name
        if req.candidate_title: profile["title"] = req.candidate_title

        analysis = GeminiService.analyze_job(
            jd_text=req.jd_text,
            master_profile=profile,
            api_key=req.api_key,
            model=req.model
        )
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tailor")
def tailor_resume(req: TailorRequest):
    """Generates tailored resume sections for any field and automatically compiles PDF."""
    if not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is empty.")
    
    try:
        profile = ProfileService.get_master_profile()
        if req.candidate_name: profile["name"] = req.candidate_name
        if req.candidate_title: profile["title"] = req.candidate_title
        if req.candidate_location: profile["location"] = req.candidate_location
        if req.candidate_email: profile["email"] = req.candidate_email

        tailor_result = GeminiService.tailor_resume(
            jd_text=req.jd_text,
            master_profile=profile,
            target_role=req.target_role,
            language=req.language or "English",
            focus_area=req.focus_area,
            api_key=req.api_key,
            model=req.model
        )

        # Merge tailored sections with master sections
        updated_sections = dict(profile.get("sections", {}))
        if "tailored_summary_tex" in tailor_result:
            updated_sections["personal_info"] = tailor_result["tailored_summary_tex"]
        if "tailored_work_experience_tex" in tailor_result:
            updated_sections["work_experience"] = tailor_result["tailored_work_experience_tex"]
        if "tailored_projects_tex" in tailor_result:
            updated_sections["projects"] = tailor_result["tailored_projects_tex"]
        if "tailored_skills_tex" in tailor_result:
            updated_sections["skills"] = tailor_result["tailored_skills_tex"]

        # Compile tailored resume into PDF
        main_tex = profile.get("main_resume_tex", "")
        job_name = f"{(req.candidate_name or 'Candidate').replace(' ', '_')}_Tailored"
        candidate_meta = {
            "name": req.candidate_name,
            "title": req.candidate_title,
            "location": req.candidate_location,
            "email": req.candidate_email,
            "linkedin": req.candidate_linkedin,
            "github": req.candidate_github,
            "photo_mode": req.photo_mode,
            "photo_base64": req.photo_base64
        }
        success, pdf_bytes, logs = LatexService.compile_latex(
            main_tex_content=main_tex,
            section_files=updated_sections,
            job_name=job_name,
            candidate_data=candidate_meta
        )

        pdf_base64 = None
        if success and pdf_bytes:
            SESSION_STORE["resume_pdf_bytes"] = pdf_bytes
            SESSION_STORE["resume_tex_sections"] = updated_sections
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return {
            "status": "success",
            "tailored_data": tailor_result,
            "updated_sections": updated_sections,
            "compile_success": success,
            "pdf_base64": pdf_base64,
            "compile_logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cover-letter")
def generate_cover_letter(req: CoverLetterRequest):
    """Generates a tailored cover letter and compiles to PDF for any profession."""
    if not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is empty.")
    
    try:
        profile = ProfileService.get_master_profile()
        if req.candidate_name: profile["name"] = req.candidate_name
        if req.candidate_location: profile["location"] = req.candidate_location
        if req.candidate_email: profile["email"] = req.candidate_email

        cl_result = GeminiService.generate_cover_letter(
            jd_text=req.jd_text,
            master_profile=profile,
            company_name=req.company_name,
            role_title=req.role_title,
            language=req.language or "English",
            api_key=req.api_key,
            model=req.model
        )

        cover_tex = cl_result.get("cover_letter_tex", "")
        candidate_meta = {
            "name": req.candidate_name,
            "location": req.candidate_location,
            "email": req.candidate_email,
            "photo_mode": req.photo_mode,
            "photo_base64": req.photo_base64
        }
        success, pdf_bytes, logs = LatexService.compile_latex(
            main_tex_content=cover_tex,
            job_name="Cover_Letter_Tailored",
            candidate_data=candidate_meta
        )

        pdf_base64 = None
        if success and pdf_bytes:
            SESSION_STORE["cover_letter_pdf_bytes"] = pdf_bytes
            SESSION_STORE["cover_letter_tex"] = cover_tex
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return {
            "status": "success",
            "cover_letter_data": cl_result,
            "compile_success": success,
            "pdf_base64": pdf_base64,
            "compile_logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compile-resume")
def compile_resume_custom(req: CompileResumeRequest):
    """Compiles custom modified sections into a fresh PDF."""
    try:
        profile = ProfileService.get_master_profile()
        main_tex = req.main_tex or profile.get("main_resume_tex", "")
        job_name = f"{(req.candidate_name or 'Candidate').replace(' ', '_')}_Custom"
        candidate_meta = {
            "name": req.candidate_name,
            "location": req.candidate_location,
            "email": req.candidate_email,
            "linkedin": req.candidate_linkedin,
            "github": req.candidate_github,
            "photo_mode": req.photo_mode,
            "photo_base64": req.photo_base64
        }
        success, pdf_bytes, logs = LatexService.compile_latex(
            main_tex_content=main_tex,
            section_files=req.sections,
            job_name=job_name,
            candidate_data=candidate_meta
        )

        pdf_base64 = None
        if success and pdf_bytes:
            SESSION_STORE["resume_pdf_bytes"] = pdf_bytes
            SESSION_STORE["resume_tex_sections"] = req.sections
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return {
            "status": "success" if success else "error",
            "compile_success": success,
            "pdf_base64": pdf_base64,
            "compile_logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compile-cover-letter")
def compile_cover_letter_custom(req: CompileCoverLetterRequest):
    """Compiles customized cover letter TeX into PDF."""
    try:
        success, pdf_bytes, logs = LatexService.compile_latex(
            main_tex_content=req.cover_letter_tex,
            job_name="Cover_Letter_Custom"
        )

        pdf_base64 = None
        if success and pdf_bytes:
            SESSION_STORE["cover_letter_pdf_bytes"] = pdf_bytes
            SESSION_STORE["cover_letter_tex"] = req.cover_letter_tex
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return {
            "status": "success" if success else "error",
            "compile_success": success,
            "pdf_base64": pdf_base64,
            "compile_logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/resume.pdf")
def download_resume():
    """Serves the latest resume PDF."""
    pdf_bytes = SESSION_STORE.get("resume_pdf_bytes")
    if not pdf_bytes:
        # Try compiling default
        profile = ProfileService.get_master_profile()
        success, default_bytes, _ = LatexService.compile_latex(
            main_tex_content=profile.get("main_resume_tex", ""),
            section_files=profile.get("sections", {}),
            job_name="Shrikar_Nakhye"
        )
        if success and default_bytes:
            pdf_bytes = default_bytes
        else:
            raise HTTPException(status_code=404, detail="No resume PDF found or compiled.")
            
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Shrikar_Nakhye_CV.pdf"}
    )

@app.get("/api/download/cover-letter.pdf")
def download_cover_letter():
    """Serves the latest cover letter PDF."""
    pdf_bytes = SESSION_STORE.get("cover_letter_pdf_bytes")
    if not pdf_bytes:
        profile = ProfileService.get_master_profile()
        success, default_bytes, _ = LatexService.compile_latex(
            main_tex_content=profile.get("cover_letter_tex", ""),
            job_name="Cover_Letter"
        )
        if success and default_bytes:
            pdf_bytes = default_bytes
        else:
            raise HTTPException(status_code=404, detail="No cover letter PDF found or compiled.")
            
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Shrikar_Nakhye_Cover_Letter.pdf"}
    )

# Mount static web directory
static_dir = WORKSPACE_DIR / "app" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
